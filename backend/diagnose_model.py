"""
Diagnostic tool to analyze why the model misclassifies normal emails as phishing.
"""
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import json
import os

# Load model
checkpoint_dir = "../models/trainer_runs/checkpoint-1104"
tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir)
model = AutoModelForSequenceClassification.from_pretrained(checkpoint_dir)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# Test cases - normal emails that might be misclassified
test_emails = [
    "Hi, I wanted to check if you're available for a meeting next Tuesday?",
    "Please find the project report attached. Let me know if you have any questions.",
    "Thanks for your email. I'll review it and get back to you soon.",
    "Our team meeting has been rescheduled to 3 PM today.",
    "Can you please send me the latest sales figures by end of day?",
    "I'm following up on our previous conversation about the contract.",
    "Please confirm your attendance for the conference next month.",
    "The new software version is ready for deployment.",
]

print("="*80)
print("MODEL DIAGNOSTIC REPORT")
print("="*80)
print(f"Model Directory: {checkpoint_dir}")
print(f"Device: {device}")
print()

# Check label mappings
print("Label Configuration:")
print(f"  id2label: {model.config.id2label}")
print(f"  label2id: {model.config.label2id}")
print()

# Test predictions
print("-"*80)
print("PREDICTION ANALYSIS ON NORMAL EMAILS")
print("-"*80)
print()

false_positives = 0
confidences = []

with torch.inference_mode():
    for email in test_emails:
        inputs = tokenizer(
            email,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        outputs = model(**inputs)
        
        logits = outputs.logits[0].detach().cpu().tolist()
        probs = torch.softmax(outputs.logits[0], dim=0).cpu().tolist()
        pred = torch.argmax(outputs.logits[0], dim=0).item()
        
        label = "PHISHING" if pred == 1 else "SAFE"
        phishing_prob = probs[1]
        safe_prob = probs[0]
        
        print(f"Email: {email[:60]}...")
        print(f"  Prediction: {label}")
        print(f"  Phishing Prob: {phishing_prob:.4f} | Safe Prob: {safe_prob:.4f}")
        print(f"  Logits (Safe/Phishing): {logits}")
        print()
        
        confidences.append(phishing_prob)
        if pred == 1:
            false_positives += 1

print("-"*80)
print("SUMMARY")
print("-"*80)
print(f"False Positives: {false_positives}/{len(test_emails)}")
print(f"Average Phishing Confidence: {sum(confidences)/len(confidences):.4f}")
print(f"Min Phishing Confidence: {min(confidences):.4f}")
print(f"Max Phishing Confidence: {max(confidences):.4f}")
print()

# Check model bias towards phishing
print("-"*80)
print("POTENTIAL ISSUES")
print("-"*80)

# Issue 1: Check if model is over-predicting phishing
if false_positives > len(test_emails) * 0.3:
    print("⚠️  HIGH FALSE POSITIVE RATE")
    print("   The model is too aggressive in classifying emails as phishing.")
    print("   Possible causes:")
    print("   - Imbalanced training data (more phishing examples)")
    print("   - Low decision threshold")
    print("   - Model overfitting to phishing patterns")
    print()

# Issue 2: Check logit/probability bias
avg_phishing_conf = sum(confidences)/len(confidences)
if avg_phishing_conf > 0.6:
    print("⚠️  HIGH AVERAGE PHISHING CONFIDENCE")
    print(f"   Average confidence: {avg_phishing_conf:.4f}")
    print("   Possible causes:")
    print("   - Model weights biased towards phishing class")
    print("   - Training data had dominant phishing patterns")
    print()

# Issue 3: Check token truncation
print("Token Truncation Check:")
max_tokens_in_config = getattr(model.config, 'max_position_embeddings', 512)
print(f"  Model max sequence length: {max_tokens_in_config}")

for email in test_emails[:2]:
    tokens = tokenizer(email, return_tensors="pt")
    token_count = tokens['input_ids'].shape[1]
    print(f"  '{email[:50]}...' uses {token_count} tokens")

print()
print("="*80)
print("RECOMMENDATIONS")
print("="*80)
print()
print("1. Analyze training data:")
print("   - Check class distribution in training set")
print("   - Look for data quality issues or label errors")
print()
print("2. Adjust decision threshold:")
print("   - Instead of using 0.5 probability as threshold, use higher value (e.g., 0.7)")
print("   - This reduces false positives")
print()
print("3. Review model weights:")
print("   - Check if training converged properly")
print("   - Look at training/validation curves for overfitting")
print()
print("4. Retrain with:")
print("   - Balanced class weights")
print("   - More diverse training data")
print("   - Longer max_length (currently truncates at 512 tokens)")
print()
