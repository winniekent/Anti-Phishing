"""
Test script to compare predictions with old threshold (0.5) vs new threshold (0.7)
This demonstrates the improvement in false positive reduction.
"""
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import os

# Load model
checkpoint_dir = "../models/trainer_runs/checkpoint-1104"
tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir)
model = AutoModelForSequenceClassification.from_pretrained(checkpoint_dir)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# Test emails
test_cases = {
    "legitimate": [
        "Can you please send me the latest sales figures by end of day?",
        "Please find the quarterly report attached.",
        "Can you provide me with the project details?",
        "What are the revenue numbers for this quarter?",
        "Send me the customer list for review.",
        "Please share the budget allocation document.",
    ],
    "phishing": [
        "Verify your account immediately by clicking here",
        "Your bank account has been compromised - confirm credentials now",
        "Urgent: Click here to update your payment information",
        "You've won a prize! Claim it by entering your SSN",
        "Re-authenticate your account for security purposes",
    ]
}

print("="*100)
print("THRESHOLD COMPARISON TEST: 0.5 (OLD) vs 0.7 (NEW)")
print("="*100)
print()

# Thresholds to compare
OLD_THRESHOLD = 0.5  # Original (too aggressive)
NEW_THRESHOLD = 0.7  # Fixed

results_summary = {"legitimate": {"fp_old": 0, "fp_new": 0, "total": 0},
                   "phishing": {"missed_old": 0, "missed_new": 0, "total": 0}}

with torch.inference_mode():
    for category, emails in test_cases.items():
        print(f"\n{'█' * 100}")
        print(f"CATEGORY: {category.upper()}")
        print(f"{'█' * 100}\n")
        
        results_summary[category]["total"] = len(emails)
        
        for email in emails:
            inputs = tokenizer(
                email,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}
            outputs = model(**inputs)
            
            probs = torch.softmax(outputs.logits[0], dim=0).cpu().tolist()
            phishing_prob = probs[1]
            safe_prob = probs[0]
            
            # Old prediction (threshold 0.5)
            old_pred = "PHISHING" if phishing_prob > OLD_THRESHOLD else "SAFE"
            
            # New prediction (threshold 0.7)
            new_pred = "PHISHING" if phishing_prob > NEW_THRESHOLD else "SAFE"
            
            # Track errors
            if category == "legitimate":
                if old_pred == "PHISHING":
                    results_summary[category]["fp_old"] += 1
                if new_pred == "PHISHING":
                    results_summary[category]["fp_new"] += 1
            else:  # phishing
                if old_pred == "SAFE":
                    results_summary[category]["missed_old"] += 1
                if new_pred == "SAFE":
                    results_summary[category]["missed_new"] += 1
            
            # Display result
            status_old = "❌" if old_pred != category.replace("legitimate", "safe").replace("phishing", "phishing") else "✅"
            status_new = "❌" if new_pred != category.replace("legitimate", "safe").replace("phishing", "phishing") else "✅"
            
            match_old = "✅" if (category == "legitimate" and old_pred == "SAFE") or (category == "phishing" and old_pred == "PHISHING") else "❌"
            match_new = "✅" if (category == "legitimate" and new_pred == "SAFE") or (category == "phishing" and new_pred == "PHISHING") else "❌"
            
            print(f"Email: {email[:70]}...")
            print(f"  Phishing Probability: {phishing_prob:.4f}")
            print(f"  Old Threshold (0.5): {old_pred:8} {match_old}  |  New Threshold (0.7): {new_pred:8} {match_new}")
            print()

print("\n" + "="*100)
print("SUMMARY REPORT")
print("="*100)
print()

print("LEGITIMATE EMAILS (Should be classified as SAFE)")
print("-" * 100)
print(f"  Total legitimate emails tested: {results_summary['legitimate']['total']}")
print(f"  False Positives with OLD threshold (0.5): {results_summary['legitimate']['fp_old']}/{results_summary['legitimate']['total']} ({results_summary['legitimate']['fp_old']*100/results_summary['legitimate']['total']:.1f}%)")
print(f"  False Positives with NEW threshold (0.7): {results_summary['legitimate']['fp_new']}/{results_summary['legitimate']['total']} ({results_summary['legitimate']['fp_new']*100/results_summary['legitimate']['total']:.1f}%)")
print(f"  ➜ Improvement: {results_summary['legitimate']['fp_old'] - results_summary['legitimate']['fp_new']} fewer false positives ✅")
print()

print("PHISHING EMAILS (Should be classified as PHISHING)")
print("-" * 100)
print(f"  Total phishing emails tested: {results_summary['phishing']['total']}")
print(f"  Missed (False Negatives) with OLD threshold (0.5): {results_summary['phishing']['missed_old']}/{results_summary['phishing']['total']} ({results_summary['phishing']['missed_old']*100/results_summary['phishing']['total']:.1f}%)")
print(f"  Missed (False Negatives) with NEW threshold (0.7): {results_summary['phishing']['missed_new']}/{results_summary['phishing']['total']} ({results_summary['phishing']['missed_new']*100/results_summary['phishing']['total']:.1f}%)")
if results_summary['phishing']['missed_new'] - results_summary['phishing']['missed_old'] > 0:
    print(f"  ⚠️  Warning: {results_summary['phishing']['missed_new'] - results_summary['phishing']['missed_old']} more phishing emails missed")
else:
    print(f"  ✅ No additional phishing emails missed")
print()

print("="*100)
print("CONCLUSION")
print("="*100)
fp_improvement = results_summary['legitimate']['fp_old'] - results_summary['legitimate']['fp_new']
if fp_improvement > 0:
    print(f"✅ The new threshold (0.7) REDUCES false positives by {fp_improvement} cases")
    print(f"   This means {fp_improvement} legitimate emails will no longer be flagged as phishing")
else:
    print("⚠️  No improvement in false positives - consider adjusting threshold further or implementing whitelist")

if results_summary['phishing']['missed_new'] - results_summary['phishing']['missed_old'] <= 0:
    print(f"✅ No additional phishing emails are missed with the new threshold")
else:
    print(f"⚠️  {results_summary['phishing']['missed_new'] - results_summary['phishing']['missed_old']} phishing emails might be missed")

print("="*100)
print()
print("HOW TO USE THIS TEST:")
print("1. Run this script before deploying to see the improvement")
print("2. Add more test cases specific to your emails")
print("3. If still too many false positives, increase threshold to 0.75-0.80")
print("4. If missing phishing, decrease threshold back toward 0.5")
print()
