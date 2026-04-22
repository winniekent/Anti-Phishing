import requests

emails = [
    ('Substack Newsletter', '4 Content Creation Claude Prompts that will make you Viral. Amazing opportunity to learn.'),
    ('Business Email', 'Hi, can you send me the sales figures for Q1 2024?'),
    ('Obvious Phishing', 'URGENT!!!  Your Amazon account has been compromised!!! Click here NOW: https://amaz0n-verify-account.fake.com/login and verify your credit card information or your account will be permanently deleted!!!'),
]

print("Testing calibrated model with more realistic phishing:\n")
for name, email in emails:
    response = requests.post('http://localhost:6500/api/predict', json={'text': email})
    result = response.json()
    score = result.get('score', 0)
    label = result.get('label', 'unknown')
    print(f"{name:25} | Score: {score:.4f} | Label: {label:10}")
