# 📊 Data Flow & Model Training Pipeline

## Complete Data Pipeline

```
┌──────────────────────────────────────────────────────────────────────┐
│                        TRAINING PHASE (Past)                         │
└──────────────────────────────────────────────────────────────────────┘

data/Phishing_Email.csv
│
├─ 3 columns: [Index, Email Text, Email Type]
│
├─ Rows: Thousands of emails labeled as:
│  ├─ "Safe Email" (legitimate business emails)
│  └─ "Phishing Email" (actual phishing attempts)
│
↓

notebooks/Email_phising (1).ipynb
│
├─ Step 1: Load CSV
│  └─ texts, labels = load_records("Phishing_Email.csv")
│
├─ Step 2: Parse emails
│  └─ Extract email text and label from CSV
│
├─ Step 3: Clean text
│  └─ Remove URLs, lowercase, normalize whitespace
│
├─ Step 4: Train/Val Split
│  └─ train_texts (80%), val_texts (20%)
│
├─ Step 5: Tokenize
│  └─ DistilBertTokenizerFast
│  └─ max_length=128 tokens per email
│
├─ Step 6: Create datasets
│  └─ HuggingFace Dataset objects
│
├─ Step 7: Train model
│  ├─ Model: DistilBertForSequenceClassification
│  ├─ Epochs: 2
│  ├─ Batch size: 16
│  ├─ Learning rate: 2e-5
│  └─ Early stopping: patience=2
│
└─ Step 8: Save checkpoint
   └─ models/trainer_runs/checkpoint-1104/
      ├─ config.json
      ├─ model.safetensors (trained weights)
      ├─ tokenizer.json
      └─ tokenizer_config.json

┌──────────────────────────────────────────────────────────────────────┐
│                      INFERENCE PHASE (Now)                           │
└──────────────────────────────────────────────────────────────────────┘

User Email Input (Plain Text)
│
├─ Example: "Can you send me your password?"
│
↓

backend/app.py
│
├─ Endpoint: POST /api/predict
├─ Load pretrained model: checkpoint-1104/
│  └─ AutoTokenizer.from_pretrained(checkpoint-1104/)
│  └─ AutoModelForSequenceClassification.from_pretrained(checkpoint-1104/)
│
↓

Tokenization
│
├─ Input: "Can you send me your password?"
│
├─ Tokenizer converts to: [CAN] [you] [send] [me] [your] [PASSWORD]
│
├─ Adds special tokens: [CLS] + tokens + [SEP]
│
├─ Pads/truncates to: max_length=512
│
└─ Output: input_ids, attention_mask, token_type_ids
    (all as tensors)

↓

Model Forward Pass
│
├─ Input tensors → DistilBERT layers
│
├─ DistilBERT Processing:
│  ├─ Token embedding
│  ├─ 6 transformer layers (in DistilBERT base)
│  ├─ Attention mechanisms
│  └─ Hidden states extraction
│
├─ Classification head:
│  ├─ Takes [CLS] token representation
│  └─ Dense layer → 2 class scores
│
└─ Output: logits [safe_score, phishing_score]
    Example: [2.5, -2.7]

↓

Probability Conversion
│
├─ Apply softmax to logits
│
├─ softmax([2.5, -2.7]):
│  ├─ safe_prob = 0.95
│  └─ phishing_prob = 0.05
│
└─ Output: probability distribution over 2 classes

↓

Decision & Threshold
│
├─ Extract: phishing_prob = 0.05
│
├─ Apply threshold: PHISHING_THRESHOLD = 0.70
│
├─ Decision logic:
│  ├─ IF phishing_prob > 0.70 → "phishing"
│  └─ IF phishing_prob ≤ 0.70 → "safe"
│
├─ Result: "safe" (0.05 < 0.70)
│
├─ Calculate confidence:
│  ├─ IF score > 0.8 → "high"
│  ├─ IF score > 0.6 → "medium"
│  └─ ELSE → "low"
│
└─ Confidence: "low" (0.05 ≤ 0.6)

↓

Generate Response
│
├─ label: "safe"
├─ score: 0.05
├─ confidence: "low"
└─ explanation: "Low phishing probability - likely safe"

↓

Return JSON Response
│
└─ HTTP 200 OK
   {
     "label": "safe",
     "score": 0.05,
     "confidence": "low",
     "explanation": "Low phishing probability - likely safe"
   }
```

---

## Key Components Explained

### 1. Training Data: `data/Phishing_Email.csv`

**Structure:**
```csv
,Email Text,Email Type
0,"re : 6 . 1100 , disc : uniformitarianism , ...",Safe Email
1,"the other side of * galicismos * ...",Safe Email
2,"re : equistar deal tickets ...",Safe Email
...
N,"URGENT: Verify your account or it will be locked",Phishing Email
```

**Characteristics:**
- Real-world emails (sourced from public datasets)
- Balanced distribution of safe and phishing
- Pre-cleaned and labeled
- Contains 1000+ email examples

**Usage in Training:**
```python
# Parse CSV
texts, labels = load_records("data/Phishing_Email.csv")
# Convert labels
labels = [0 if label == "Safe Email" else 1 for label in labels]
# Split: 80% train, 20% validation
train_texts, val_texts, train_labels, val_labels = train_test_split(
    texts, labels, test_size=0.2, stratify=labels
)
```

### 2. Pretrained Model: `models/trainer_runs/checkpoint-1104/`

**Model Architecture:**
```
DistilBertForSequenceClassification
│
├─ Base Model: distilbert-base-uncased (pretrained)
│  └─ 6 transformer layers (vs 12 in BERT)
│  └─ 66M parameters (vs 110M in BERT)
│
├─ Embedding Layer
│  ├─ Token embeddings: 768-dim
│  ├─ Position embeddings
│  └─ Token type embeddings
│
├─ 6 Transformer Blocks
│  ├─ Multi-head attention (12 heads)
│  ├─ Feed-forward networks
│  └─ Layer normalization
│
└─ Classification Head (fine-tuned)
   ├─ Linear layer: 768 → 2
   └─ Softmax output
```

**File Contents:**
- **config.json**: Model configuration (vocab size, num layers, etc.)
- **model.safetensors**: All trained weights (compressed)
- **tokenizer.json**: Vocabulary and tokenization rules
- **tokenizer_config.json**: Tokenizer settings

### 3. Text Processing Pipeline

**Step 1: Tokenization**
```python
# Input
email = "Can you send me the sales figures?"

# Tokenizer breaks into tokens
tokenizer = DistilBertTokenizerFast.from_pretrained(
    "distilbert-base-uncased"
)
tokens = tokenizer.tokenize(email)
# Output: ['can', 'you', 'send', 'me', 'the', 'sales', 'figures', '?']
```

**Step 2: Convert to IDs**
```python
# Tokenizer converts tokens to vocabulary indices
input_ids = tokenizer.convert_tokens_to_ids(tokens)
# Output: [2054, 2017, 3639, 2033, 1996, 3686, 4232, 1029]
# (vocabulary IDs that model understands)
```

**Step 3: Add Special Tokens**
```python
# Add classification tokens
# [CLS] = classification token (represents whole sequence)
# [SEP] = separator token
# Tokens: [CLS] can you send me the sales figures? [SEP]
```

**Step 4: Padding & Attention Mask**
```python
# Pad to max_length=512
# Create attention_mask: 1 for real tokens, 0 for padding
# Example: [1,1,1,1,1,1,1,1,1,0,0,...,0] (rest are 0s)
```

### 4. Model Inference

**Forward Pass:**
```
Input tokens [batch_size, seq_length, 768]
  ↓
Embedding layer
  ↓
6 Transformer blocks (each adds context awareness)
  ↓
[CLS] token representation [batch_size, 768]
  ↓
Dense layer [batch_size, 2]
  ↓
Logits: [safe_logit, phishing_logit]
```

**Example Processing:**
```
Input: "Can you send me your password?"
↓
Tokenized: [CLS] can you send me your password [SEP]
↓
Embedded: 9 × 768-dim vectors
↓
Through 6 transformer layers: context enriched
↓
Extract [CLS] representation: 768-dim vector
↓
Dense layer: 2 outputs
  → output[0] = 0.3 (safe score)
  → output[1] = 2.1 (phishing score)
↓
Softmax: 
  → safe_prob = 0.11 (softmax of 0.3)
  → phishing_prob = 0.89 (softmax of 2.1)
↓
Decision (threshold 0.70):
  → 0.89 > 0.70 → PHISHING ⚠️
```

---

## Data Sources

### Where Training Data Comes From
- **Enron Email Dataset**: Real corporate emails (safe examples)
- **Public Phishing Corpora**: Labeled phishing attempts
- **Security Datasets**: Curated phishing examples

### Why It Works
1. **Diverse examples**: Different phishing techniques represented
2. **Balanced**: Equal number of safe and phishing examples
3. **Real-world**: Actual emails, not synthetic
4. **Labeled**: Expert annotation of phishing vs. safe

---

## Model Performance Indicators

### What Model Learned
✅ Phishing patterns:
- Urgency keywords: "URGENT", "IMMEDIATELY", "ACT NOW"
- Credential requests: "verify password", "confirm account"
- Suspicious links: "click here to update"
- Generic greetings: "Dear Customer"

✅ Safe patterns:
- Specific context: project names, meeting details
- Internal references: specific people, departments
- Business tone: professional language
- Legitimate requests: report access, data sharing

### Confidence Interpretation
```
Score 0.95 → "This is definitely phishing"
Score 0.80 → "This looks like phishing"
Score 0.60 → "Probably phishing, but less certain"
Score 0.40 → "Probably safe, but some red flags"
Score 0.05 → "This is definitely safe"
```

---

## Threshold Sensitivity

### Current Setting: 0.70

```
Threshold value = 0.70

Safe emails with score < 0.70:
├─ 0.05 - Very safe → Classified: SAFE ✅
├─ 0.30 - Likely safe → Classified: SAFE ✅
├─ 0.69 - On the edge → Classified: SAFE ✅
└─ 0.71 - Just over → Classified: PHISHING (FP)

Phishing emails with score > 0.70:
├─ 0.71 - Barely over → Classified: PHISHING ✅
├─ 0.85 - Clearly phishing → Classified: PHISHING ✅
├─ 0.95 - Very clear phishing → Classified: PHISHING ✅
└─ 0.69 - Just under → Classified: SAFE (FN - missed)
```

---

## Summary Flow

```
TRAINING (Offline)
Training Data → Clean → Tokenize → Train Model → Save Checkpoint
     ↓
   1000s of emails    DistilBERT    Fine-tune    checkpoint-1104/

PREDICTION (Online/Runtime)
User Email → Tokenize → Load Model → Forward Pass → Threshold → Response
     ↓
   Single email    Same tokenizer   checkpoint-1104/   0.70    JSON
```

---

## Key Takeaways

1. **Model uses pretrained DistilBERT**: Reduces training needed, leverages general language understanding
2. **Training data in `data/` folder**: Used to fine-tune the model for phishing detection
3. **Pretrained checkpoint saved**: `models/trainer_runs/checkpoint-1104/` contains all necessary weights
4. **Inference pipeline**: Text → Tokens → Model → Probabilities → Threshold → Classification
5. **Configurable threshold**: 0.70 balances false positives vs. false negatives

All components are ready to use! 🎉
