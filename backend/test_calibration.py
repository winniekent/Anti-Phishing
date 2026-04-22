import requests

emails = [
    ('Substack Newsletter', '4 Content Creation Claude Prompts that will make you Viral. Amazing opportunity to learn.'),
    ('Business Email', 'This is a normal business email about sales figures and quarterly reports.'),
    ('Phishing Email', 'Urgent: Verify your account immediately or it will be closed. Click here: http://fake-bank.com'),
    ('Marketing', 'Learn Python for N15,000. Limited time offer. Click here for details.'),
]

print("Testing calibrated model:\n")
for name, email in emails:
    response = requests.post('http://localhost:6500/api/predict', json={'text': email})
    result = response.json()
    score = result.get('score', 0)
    label = result.get('label', 'unknown')
    print(f"{name:20} | Score: {score:.4f} | Label: {label:10}")
