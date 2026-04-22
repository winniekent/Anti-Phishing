import json
import requests

text = (
    "Subject: Urgent: Action Required - Verify Your Account Within 24 Hours" 
    "From: \"IT Security Team\" security@paypal-verification.net"
    "To: [Target Email]"
    "Dear valued customer,"
    "We've detected unusual login activity from an unrecognized device attempting to access your account. As a security measure, your account has been temporarily restricted."
    "To avoid permanent suspension, please verify your identity immediately by clicking the link below:"
    "Verify My Account Now"
    "Failure to verify within 24 hours will result in account closure and loss of access to your funds."
    "If you believe this is an error, please contact our support team at +1 (833) 555-0192 (charges may apply)."
    "Thank you for your prompt cooperation."
    "Sincerely,"
    "IT Security Team"
    "security@paypal-verification.net"
    "Sincerely,"
    "PayPal Security Department"
)

response = requests.post('http://localhost:6500/api/predict', json={'text': text}, timeout=10)
print('status', response.status_code)
print(json.dumps(response.json(), indent=2))

