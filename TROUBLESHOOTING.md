# Why Your Model Misclassifies Normal Emails as Phishing

## Problem Summary
The model is classifying legitimate business emails as phishing, particularly emails containing phrases like "send me the latest sales figures."

**Example False Positive:**
- Email: "Can you please send me the latest sales figures by end of day?"
- **Prediction: PHISHING (85.51% confidence)** ❌
- Correct prediction: SAFE

---

## Root Causes

### 1. **Training Data Bias** 🎯
The model was trained on a dataset where certain phrases were strongly associated with phishing attacks:
- **"send me"** - Common phishing request pattern
- **"sales figures"** / business data requests - Phishing often targets financial/business data
- **Urgency indicators** - "by end of day" creates artificial urgency

**Impact:** These patterns are legitimate in business emails but appear frequently in phishing emails too.

### 2. **Imbalanced Training Data**
Possible class imbalance in your training set:
- More phishing examples than legitimate emails
- OR disproportionate representation of certain phishing patterns

This causes the model to be **over-confident** when it sees similar patterns.

### 3. **Insufficient Context Understanding**
The model truncates emails at 512 tokens (very long emails may be cut off), losing context that would help distinguish legitimate requests from phishing attempts.

### 4. **No Request Type Distinction**
The model treats all data requests the same way:
- Phishing: "Send me your banking credentials"
- Legitimate: "Send me the sales figures"

Both trigger similar warning patterns.

---

## Quick Fixes (Immediate)

### Fix 1: Adjust Decision Threshold ✅ EASIEST
Instead of classifying anything with >50% phishing probability as phishing, use a **70% threshold**:

**In your `app.py`:**
```python
# Around line 80, modify the prediction logic:
PHISHING_THRESHOLD = 0.7  # was implicitly 0.5

# In the prediction response:
for label, score in zip(preds, phishing_scores):
    # Only classify as phishing if confidence > threshold
    is_phishing = score > PHISHING_THRESHOLD
    results.append({
        "label": "phishing" if is_phishing else "safe",
        "score": float(score),
        "confidence": "high" if score > 0.8 else "medium" if score > 0.6 else "low"
    })
```

**Expected Impact:** Reduces false positives significantly while maintaining phishing detection.

---

### Fix 2: Whitelist Business Terms
Add a simple pre-filter for common legitimate business requests:

```python
def is_likely_legitimate_request(text):
    """Whitelist common legitimate business patterns"""
    legitimate_patterns = [
        "send me the .* (report|figures|data|results|update)",
        "can you please send me",
        "please provide .* (numbers|stats|information)",
        "what are the .* (details|figures|numbers)",
    ]
    
    text_lower = text.lower()
    for pattern in legitimate_patterns:
        if re.search(pattern, text_lower):
            # Override model prediction for clearly legitimate requests
            return True
    return False
```

---

## Long-Term Solutions (Recommended)

### Solution 1: Rebalance Training Data 🔄
1. Check the class distribution in your training dataset
2. Use techniques like:
   - **Stratified sampling** - Ensure equal proportions
   - **Oversampling** - Duplicate minority class
   - **Undersampling** - Reduce majority class
   - **SMOTE** - Synthetic oversampling

**Code to add to notebook:**
```python
from sklearn.utils.class_weight import compute_class_weight

class_weights = compute_class_weight(
    'balanced',
    classes=np.unique(train_labels),
    y=train_labels
)

# Apply in training arguments:
training_args = TrainingArguments(
    # ... other args
    class_weight=class_weights,  # Add this
)
```

### Solution 2: Add Context-Aware Features 📋
Instead of just text, include:
- **Email metadata:** sender domain, recipient domain
- **Content type:** request for action vs. threat
- **Urgency level:** actual urgency vs. false urgency
- **Business context:** legitimate department/role?

```python
def extract_features(email_text, sender, recipient):
    features = {
        "text": email_text,
        "has_urgency_language": has_urgency_markers(email_text),
        "is_internal_domain": is_internal_sender(sender),
        "data_sensitivity": classify_data_type(email_text),
        "request_type": classify_request(email_text),
    }
    return features
```

### Solution 3: Retrain with Adjusted Model Parameters ⚙️
Update your notebook training section:

```python
# Notebook: Increase training with better settings
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,  # Increase from 2
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    load_best_model_at_end=True,
    metric_for_best_model="f1",  # Add this - optimize for F1 score
    greater_is_better=True,
    fp16=True,
    report_to="none",
    # ADD THESE:
    weight_decay=0.01,  # Regularization
    learning_rate=2e-5,  # Better learning rate
    warmup_steps=500,    # Warmup training
)

# Use weighted loss for imbalanced data
from transformers import Trainer, TrainingArguments, EarlyStoppingCallback
import numpy as np

class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        
        # Apply class weights
        loss_fct = torch.nn.CrossEntropyLoss(weight=torch.tensor([0.3, 0.7]))
        loss = loss_fct(logits.view(-1, self.model.config.num_labels), 
                       labels.view(-1))
        return (loss, outputs) if return_outputs else loss

trainer = WeightedTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
    tokenizer=tokenizer,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
)
```

### Solution 4: Add Ensemble Approach 🔀
Use multiple models/heuristics:

```python
def ensemble_predict(text):
    # 1. DistilBERT model
    bert_score = get_bert_prediction(text)
    
    # 2. Keyword-based heuristic
    keyword_score = check_phishing_keywords(text)
    
    # 3. URL analysis (if emails have links)
    url_score = analyze_urls_in_email(text)
    
    # 4. Sender analysis
    sender_score = analyze_sender_domain(text)
    
    # Weighted ensemble
    final_score = (
        0.5 * bert_score +
        0.2 * keyword_score +
        0.2 * url_score +
        0.1 * sender_score
    )
    
    return final_score
```

---

## Testing Your Fixes

Create a test set with:
1. ✅ Legitimate business emails
2. ❌ Known phishing emails
3. 🤔 Borderline cases

```python
test_cases = {
    "safe": [
        "Can you send me the sales figures?",
        "Please provide the quarterly report",
        "What are the project details?",
    ],
    "phishing": [
        "Verify your account urgently by clicking here",
        "Confirm your credentials for security",
        "Your account has been compromised - act now",
    ]
}

# Test and evaluate
for category, emails in test_cases.items():
    for email in emails:
        pred = predict(email)
        print(f"{category}: {email[:50]}... -> {pred}")
```

---

## Recommended Action Plan

**Priority 1 (Do Today):**
- ✅ Apply Fix 1: Change threshold to 0.7 in app.py
- ✅ Test with your false positive cases

**Priority 2 (This Week):**
- Implement Fix 2: Add whitelist for business terms
- Analyze training data distribution

**Priority 3 (Next Sprint):**
- Retrain with Solution 3: Weighted loss + better parameters
- Add metadata features (Solution 2)

---

## Files to Update

1. **Backend API** - `/backend/app.py`
   - Change prediction threshold
   - Add whitelist logic

2. **Training Notebook** - `/notebooks/Email_phising (1).ipynb`
   - Add class weights
   - Adjust training parameters
   - Add evaluation metrics

3. **Configuration** - Create `/backend/config.py`
   - Store thresholds and parameters
   - Make it easy to adjust settings

---

## Questions to Answer

To further improve the model, find answers to:
1. What's the class distribution in your training data?
   - % Phishing vs. % Legitimate?
2. What are the most common false positives?
3. Are there specific domains/senders being misclassified?
4. Do you have access to more diverse training data?

---

## Summary

| Issue | Impact | Quick Fix | Long-term Fix |
|-------|--------|-----------|---------------|
| Too aggressive phishing detection | False positives | ↑ Threshold to 0.7 | Retrain with balanced data |
| Missing context | Misses legitimate patterns | Whitelist terms | Add email metadata |
| Imbalanced training | Model bias | Weight classes | Rebalance dataset |
| Limited features | Low accuracy | Pre-filtering | Ensemble + features |

