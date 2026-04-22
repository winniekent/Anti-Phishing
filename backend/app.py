from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import json
import os
import math
import re
from html.parser import HTMLParser

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
STATIC_DIR = os.path.join(BASE_DIR, "static")
LANDING_DIR = os.path.join(ROOT_DIR, "landing")

os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

app = FastAPI(title="Phishing Detector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/learn", StaticFiles(directory=LANDING_DIR, html=True), name="learn")

logging.basicConfig(level=logging.DEBUG)

# ====================================================================
# CONFIGURATION
# ====================================================================
PHISHING_THRESHOLD = 0.85
# ====================================================================


# ====================================================================
# HTML STRIPPING
# ====================================================================
class _HTMLTextExtractor(HTMLParser):
    """Extract visible text from HTML, discarding tags and scripts."""
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() in ("script", "style"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag.lower() in ("script", "style"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            stripped = data.strip()
            if stripped:
                self._parts.append(stripped)

    def get_text(self) -> str:
        return " ".join(self._parts)


def _strip_html(text: str) -> str:
    """
    Remove HTML tags, inline JS/CSS, and HTML comments from text.
    Falls back to the original text if parsing fails or yields nothing.
    """
    # Remove HTML comments (including <!-- ... --> blocks with JS inside)
    text_no_comments = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    # Use the parser to extract visible text
    extractor = _HTMLTextExtractor()
    try:
        extractor.feed(text_no_comments)
        clean = extractor.get_text()
    except Exception:
        clean = ""

    # If stripping left us with almost nothing, fall back to raw text
    # (avoids sending an empty string to the model for plain-text emails)
    if len(clean.strip()) < 20:
        # At minimum, strip obvious tags with a simple regex as fallback
        clean = re.sub(r'<[^>]+>', ' ', text)
        clean = re.sub(r'\s+', ' ', clean).strip()

    return clean
# ====================================================================


class TextRequest(BaseModel):
    text: str | None = None
    texts: list[str] | None = None

_TEXT_MODEL = None
_TEXT_TOKENIZER = None
_TEXT_DEVICE = None

def _find_latest_checkpoint(base_dir: str) -> str:
    if not os.path.isdir(base_dir):
        raise RuntimeError(f"Checkpoint base directory not found: {base_dir}")
    best = None
    best_step = -1
    for name in os.listdir(base_dir):
        if not name.startswith("checkpoint-"):
            continue
        step_str = name.split("checkpoint-")[-1]
        try:
            step = int(step_str)
        except ValueError:
            continue
        if step > best_step:
            best_step = step
            best = os.path.join(base_dir, name)
    if best is None:
        raise RuntimeError(f"No checkpoint-* folders found in {base_dir}")
    return best

def _load_text_model():
    global _TEXT_MODEL, _TEXT_TOKENIZER, _TEXT_DEVICE
    if _TEXT_MODEL is not None and _TEXT_TOKENIZER is not None and _TEXT_DEVICE is not None:
        return _TEXT_MODEL, _TEXT_TOKENIZER, _TEXT_DEVICE

    checkpoint_base = os.path.join(ROOT_DIR, "models", "trainer_runs")
    checkpoint_dir = _find_latest_checkpoint(checkpoint_base)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir)
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint_dir)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    _TEXT_MODEL = model
    _TEXT_TOKENIZER = tokenizer
    _TEXT_DEVICE = device
    return model, tokenizer, device

@app.post('/api/predict')
async def predict(payload: TextRequest):
    try:
        texts = None
        if payload.text is not None:
            texts = [payload.text]
        elif payload.texts is not None:
            texts = payload.texts

        if not texts or any(t is None or not str(t).strip() for t in texts):
            logging.error("No text provided in request data.")
            raise HTTPException(status_code=400, detail="No text provided")

        # Strip HTML/JS from all inputs before prediction
        cleaned_texts = [_strip_html(t) for t in texts]
        logging.debug("Predict request texts (cleaned): %s", cleaned_texts)

        model, tokenizer, device = _load_text_model()

        with torch.inference_mode():
            inputs = tokenizer(
                cleaned_texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}
            outputs = model(**inputs)
            logits = outputs.logits.detach().cpu().tolist()
            probs = torch.softmax(outputs.logits, dim=1)
            phishing_scores = probs[:, 1].tolist()

        logging.debug("Model logits: %s", logits)
        logging.debug("Model phishing probabilities: %s", phishing_scores)

        results = []
        for score in phishing_scores:
            if score > 0.95:
                calibrated_score = 0.5 + 0.4 * math.tanh(2.0 * (score - 0.5))
            else:
                calibrated_score = score

            is_phishing = calibrated_score > PHISHING_THRESHOLD
            confidence_level = "high" if calibrated_score > 0.8 else "medium" if calibrated_score > 0.6 else "low"

            if is_phishing:
                explanation = "High confidence phishing" if calibrated_score > 0.8 else "Medium confidence phishing"
            else:
                explanation = "Low phishing probability - likely safe" if calibrated_score < 0.6 else "Medium confidence - borderline safe"

            results.append({
                "label": "phishing" if is_phishing else "safe",
                "score": float(calibrated_score),
                "confidence": confidence_level,
                "explanation": explanation
            })

        if payload.text is not None:
            return results[0]
        return {"results": results}
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Error occurred during text prediction.")
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/collect_url')
async def collect_url(data: dict):
    try:
        path = os.path.join(STORAGE_DIR, "url_data.json")
        with open(path, 'a') as f:
            json.dump(data, f)
            f.write('\n')
        return Response(status_code=204)
    except Exception as e:
        logging.exception("Error occurred while collecting URL.")
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/track')
async def track_event(event_data: dict):
    try:
        event_log_path = os.path.join(STORAGE_DIR, "event_log.json")
        if not os.path.exists(event_log_path):
            with open(event_log_path, 'w') as f:
                pass

        with open(event_log_path, 'a') as f:
            json.dump(event_data, f)
            f.write('\n')

        return Response(status_code=204)
    except Exception as e:
        logging.exception("Error occurred while tracking event.")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app:app', host='0.0.0.0', port=6500, reload=False)