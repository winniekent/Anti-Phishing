#!/usr/bin/env python3
"""
Comprehensive API Testing Guide for Phishing Detector
Tests the /api/predict endpoint with various email scenarios
"""

import requests
import json
from typing import Dict, List

# API Configuration
API_BASE_URL = "http://localhost:8000"
PREDICT_ENDPOINT = f"{API_BASE_URL}/api/predict"

class PhishingDetectorTest:
    """Test suite for phishing detector API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.predict_url = f"{base_url}/api/predict"
        self.results = []
    
    def test_single_email(self, email_text: str, expected_label: str = None):
        """Test classification of a single email"""
        print(f"\n{'='*80}")
        print(f"Testing: {email_text[:60]}...")
        print(f"{'='*80}")
        
        payload = {"text": email_text}
        
        try:
            response = requests.post(self.predict_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Display results
            print(f"Status Code: {response.status_code}")
            print(f"Label: {result.get('label', 'N/A').upper()}")
            print(f"Score: {result.get('score', 'N/A'):.4f}")
            print(f"Confidence: {result.get('confidence', 'N/A')}")
            print(f"Explanation: {result.get('explanation', 'N/A')}")
            
            # Check if correct
            if expected_label:
                is_correct = result.get('label') == expected_label
                status = "✅ CORRECT" if is_correct else "❌ INCORRECT"
                print(f"Expected: {expected_label} → {status}")
            
            return result
            
        except requests.exceptions.ConnectionError:
            print("❌ ERROR: Cannot connect to API")
            print(f"   Make sure server is running at {self.base_url}")
            return None
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return None
    
    def test_batch_emails(self, emails: List[str]):
        """Test classification of multiple emails"""
        print(f"\n{'='*80}")
        print("BATCH TEST: Multiple Emails")
        print(f"{'='*80}")
        
        payload = {"texts": emails}
        
        try:
            response = requests.post(self.predict_url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            for i, (email, result) in enumerate(zip(emails, results), 1):
                print(f"\n{i}. {email[:60]}...")
                print(f"   → {result.get('label').upper()} (confidence: {result.get('confidence')})")
            
            return data
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return None


def run_test_suite():
    """Run comprehensive test suite"""
    
    tester = PhishingDetectorTest()
    
    print("\n" + "="*80)
    print("🧪 PHISHING DETECTOR API TEST SUITE")
    print("="*80)
    
    # Test 1: Legitimate Business Emails
    print("\n\n" + "█"*80)
    print("TEST CATEGORY 1: LEGITIMATE BUSINESS EMAILS")
    print("█"*80)
    
    legitimate_emails = [
        ("Hi, can you review the attached document?", "safe"),
        ("Please send me the quarterly report.", "safe"),
        ("Meeting scheduled for tomorrow at 2 PM.", "safe"),
        ("Can you provide the project status update?", "safe"),
        ("Thanks for your email. I'll get back to you.", "safe"),
    ]
    
    for email, expected in legitimate_emails:
        tester.test_single_email(email, expected)
    
    # Test 2: Obvious Phishing Emails
    print("\n\n" + "█"*80)
    print("TEST CATEGORY 2: OBVIOUS PHISHING EMAILS")
    print("█"*80)
    
    phishing_emails = [
        ("URGENT: Verify your account immediately!", "phishing"),
        ("Click here to confirm your credentials", "phishing"),
        ("Your account has been compromised - act now!", "phishing"),
        ("Congratulations! You've won a prize. Claim it here.", "phishing"),
    ]
    
    for email, expected in phishing_emails:
        tester.test_single_email(email, expected)
    
    # Test 3: Edge Cases / Borderline Cases
    print("\n\n" + "█"*80)
    print("TEST CATEGORY 3: EDGE CASES / BORDERLINE")
    print("█"*80)
    
    edge_cases = [
        ("Can you send me your password for the database?", "phishing"),
        ("Please update your payment information urgently.", "phishing"),
        ("Hi, just following up on our earlier conversation.", "safe"),
        ("We need to verify your banking details.", "phishing"),
        ("New software version ready for download.", "safe"),
    ]
    
    for email, expected in edge_cases:
        tester.test_single_email(email, expected)
    
    # Test 4: Batch Processing
    print("\n\n" + "█"*80)
    print("TEST CATEGORY 4: BATCH PROCESSING")
    print("█"*80)
    
    batch = [
        "Can you send me the sales figures?",
        "Verify your account urgently",
        "Meeting tomorrow at 3 PM",
        "Click here to update credentials",
    ]
    
    tester.test_batch_emails(batch)
    
    # Test 5: Real-World Scenarios
    print("\n\n" + "█"*80)
    print("TEST CATEGORY 5: REAL-WORLD SCENARIOS")
    print("█"*80)
    
    real_world = [
        ("""
        Hi John,
        
        I hope this email finds you well. I wanted to follow up on our conversation 
        regarding the Q2 budget allocation. Could you please send me the updated 
        figures by end of week? We need to finalize this before the board meeting.
        
        Thanks,
        Sarah
        """, "safe"),
        
        ("""
        ALERT: Unusual activity detected on your account!
        
        Your account has been flagged for suspicious login attempts.
        CLICK HERE IMMEDIATELY to verify your identity and secure your account.
        
        Do NOT ignore this message or your account will be locked.
        
        - Security Team
        """, "phishing"),
        
        ("""
        Dear Valued Customer,
        
        We have a special offer for you this month. 
        Visit our website to see how much you can save.
        
        Best regards,
        Marketing Team
        """, "safe"),
    ]
    
    for email, expected in real_world:
        tester.test_single_email(email.strip(), expected)
    
    print("\n\n" + "="*80)
    print("✅ TEST SUITE COMPLETED")
    print("="*80)
    print("\nSummary:")
    print("- If most tests passed: Model is working correctly ✅")
    print("- If some legitimate emails marked as phishing: Increase threshold to 0.75-0.80")
    print("- If phishing emails not caught: Decrease threshold to 0.60-0.65")
    print("\nTo adjust threshold, edit /backend/app.py line 41")
    print("="*80 + "\n")


def quick_test():
    """Quick single test"""
    
    tester = PhishingDetectorTest()
    
    email = input("Enter email to test: ")
    result = tester.test_single_email(email)
    
    if result:
        print("\n" + "="*80)
        print("Full Response:")
        print(json.dumps(result, indent=2))
        print("="*80)


def verify_server_health():
    """Verify API server is running"""
    
    print("\n🔍 Checking API Server Health...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
        print("✅ API Server is RUNNING")
        print(f"   Base URL: {API_BASE_URL}")
        print(f"   Docs available at: {API_BASE_URL}/docs")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ API Server is NOT RUNNING")
        print(f"   Could not connect to {API_BASE_URL}")
        print("\n   To start the server:")
        print("   cd backend")
        print("   python -m uvicorn app:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*80)
    print("🚀 PHISHING DETECTOR API TEST RUNNER")
    print("="*80)
    
    # First check if server is running
    if not verify_server_health():
        print("\n⚠️  Please start the API server first")
        sys.exit(1)
    
    print("\n" + "="*80)
    print("SELECT TEST MODE:")
    print("="*80)
    print("1. Run Full Test Suite (recommended)")
    print("2. Quick Single Email Test")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        run_test_suite()
    elif choice == "2":
        quick_test()
    else:
        print("Exiting...")
        sys.exit(0)
