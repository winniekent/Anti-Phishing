# 🚀 Quick Start Guide - Phishing Detector API

## Verify Your System Setup ✅

### What's Already Configured
✅ **Pretrained Model:** `models/trainer_runs/checkpoint-1104/`
- Uses DistilBERT base model fine-tuned on phishing data
- Ready to classify emails immediately

✅ **Training Data:** `data/Phishing_Email.csv`
- Contains labeled examples: Safe Email & Phishing Email
- Model was trained on this data

✅ **Backend API:** `backend/app.py`
- FastAPI server with `/api/predict` endpoint
- Loads model automatically on startup
- Uses configurable threshold (0.70 to reduce false positives)

✅ **Fixes Applied:**
- Threshold adjusted to 0.70 (was too aggressive at 0.5)
- Confidence levels added to responses
- Better explanations included

---

## Starting the Server

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Install Dependencies (if needed)
```bash
pip install fastapi uvicorn transformers torch
```

### 3. Start the API Server
```bash
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

## Testing the API

### Option A: Using curl (Command Line)

**Test 1: Single Legitimate Email**
```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Can you send me the quarterly report?"}'
```

**Expected Response:**
```json
{
  "label": "safe",
  "score": 0.05,
  "confidence": "low",
  "explanation": "Low phishing probability - likely safe"
}
```

**Test 2: Single Phishing Email**
```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "URGENT: Verify your account immediately or it will be locked!"}'
```

**Expected Response:**
```json
{
  "label": "phishing",
  "score": 0.92,
  "confidence": "high",
  "explanation": "High confidence phishing"
}
```

**Test 3: Multiple Emails**
```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Meeting at 3 PM",
      "Click here to verify credentials",
      "Project status update attached"
    ]
  }'
```

### Option B: Using Python Script (Recommended)

```bash
cd backend
python test_api.py
```

**Choose:**
- `1` - Run Full Test Suite (tests many scenarios)
- `2` - Test Single Email (interactive)
- `3` - Exit

### Option C: Using Browser

1. Open: `http://localhost:8000/docs`
2. Click on `/api/predict` endpoint
3. Click "Try it out"
4. Enter JSON:
   ```json
   {"text": "Your email here"}
   ```
5. Click "Execute"

---

## Model Classification Details

### How It Works

```
Your Email (Plain Text)
    ↓
Tokenization (Converts text to numbers)
    ↓
DistilBERT Neural Network (Processes tokens)
    ↓
Output Layer (2 classes)
    ↓
Softmax (Converts to probabilities)
    ↓
Decision:
  • Score > 0.70 → PHISHING ⚠️
  • Score ≤ 0.70 → SAFE ✅
```

### Response Format

```json
{
  "label": "safe" or "phishing",          // Classification result
  "score": 0.0 to 1.0,                  // Probability of being phishing (0=safe, 1=phishing)
  "confidence": "low/medium/high",      // Confidence level of prediction
  "explanation": "..."                   // Explanation message
}
```

### Confidence Levels
- **High** (score > 0.80): Very confident prediction
- **Medium** (0.60 < score ≤ 0.80): Fairly confident
- **Low** (score ≤ 0.60): Less confident, likely safe

---

## Troubleshooting

### Problem: Connection Refused
**Solution:** Make sure server is running
```bash
python -m uvicorn app:app --reload
```

### Problem: Model Not Found
**Solution:** Verify checkpoint exists
```bash
ls models/trainer_runs/checkpoint-1104/
```

Should show: `config.json`, `model.safetensors`, `tokenizer.json`, `tokenizer_config.json`

### Problem: Too Many False Positives
**Solution:** Increase threshold in `app.py` line 41
```python
PHISHING_THRESHOLD = 0.75  # Was 0.70
```

Higher = fewer false positives (but might miss phishing)

### Problem: Missing Phishing Emails
**Solution:** Decrease threshold in `app.py` line 41
```python
PHISHING_THRESHOLD = 0.65  # Was 0.70
```

Lower = catches more phishing (but more false positives)

---

## Testing Your Own Emails

### Method 1: Save to File and Test
```bash
# Create test_my_emails.py
cat > test_my_emails.py << 'EOF'
import requests
import json

emails = [
    "Your email 1 here",
    "Your email 2 here",
    "Your email 3 here",
]

for email in emails:
    response = requests.post(
        "http://localhost:8000/api/predict",
        json={"text": email}
    )
    print(f"Email: {email[:50]}...")
    print(f"Result: {response.json()}\n")
EOF

python test_my_emails.py
```

### Method 2: Interactive Testing
```bash
python test_api.py
# Select option 2 for quick single email test
```

---

## API Documentation

### Interactive Docs
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoint: POST /api/predict

**Request:**
```json
{
  "text": "string",     // Single email (optional)
  "texts": ["string"]   // Multiple emails (optional)
}
```

**Response (Single Email):**
```json
{
  "label": "safe|phishing",
  "score": 0.0-1.0,
  "confidence": "low|medium|high",
  "explanation": "string"
}
```

**Response (Multiple Emails):**
```json
{
  "results": [
    { /* as above */ },
    { /* as above */ }
  ]
}
```

---

## Performance Indicators

### Good Signs ✅
- Legitimate business emails classified as "safe"
- Phishing emails classified as "phishing"
- Response time < 1 second per email
- Confidence levels seem reasonable

### Warning Signs ⚠️
- All emails classified as phishing (check threshold)
- All emails classified as safe (check model loading)
- Very slow responses (check GPU/CPU usage)
- Cryptic error messages (check logs)

---

## Next Steps

1. **Run Full Test Suite** (recommended)
   ```bash
   cd backend
   python test_api.py
   # Select option 1
   ```

2. **Test with Your Emails**
   - Collect examples of emails you want to classify
   - Test them via the API
   - Monitor accuracy

3. **Fine-tune If Needed**
   - If too many false positives: increase threshold (0.75-0.80)
   - If missing phishing: decrease threshold (0.60-0.65)

4. **Monitor Performance**
   - Keep logs of predictions
   - Compare with user feedback
   - Adjust threshold based on results

---

## System Architecture

```
┌─────────────────┐
│  Email Client   │ (Browser/Extension/API)
└────────┬────────┘
         │ HTTP POST /api/predict
         │ {"text": "email content"}
         ↓
┌─────────────────┐
│  FastAPI App    │ (backend/app.py)
│  - CORS enabled │
│  - JSON parser  │
└────────┬────────┘
         │ Load model
         ↓
┌─────────────────┐
│  DistilBERT     │ (models/trainer_runs/checkpoint-1104/)
│  - Tokenizer    │
│  - Model weights│
│  - Config       │
└────────┬────────┘
         │ Process
         ↓
┌─────────────────┐
│  Classification │
│  - Logits       │
│  - Softmax      │
│  - Threshold    │
└────────┬────────┘
         │ JSON Response
         ↓
┌─────────────────┐
│  Email Client   │ Returns result
└─────────────────┘
```

---

## Quick Command Reference

| Command | Purpose |
|---------|---------|
| `python -m uvicorn app:app --reload` | Start server |
| `python test_api.py` | Run test suite |
| `curl -X POST http://localhost:8000/api/predict ...` | Test via curl |
| `http://localhost:8000/docs` | Interactive docs |
| Edit `app.py` line 41 | Adjust threshold |

---

## Summary

✅ **Your system is ready to:**
1. Load the pretrained DistilBERT model
2. Read any email text
3. Classify it as Safe or Phishing
4. Return confidence scores and explanations

🎯 **To get started:**
```bash
cd backend
python -m uvicorn app:app --reload
python test_api.py
```

Happy testing! 🎉
