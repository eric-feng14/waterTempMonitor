#!/usr/bin/env python3
"""
Test script for email functionality on Raspberry Pi
Run this to test if email alerts work correctly
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Import email configuration
try:
    from email_config import *
except ImportError:
    print("❌ email_config.py not found. Using default settings.")
    EMAIL_ENABLED = True
    EMAIL_SENDER = "ericfeng242@gmail.com"
    EMAIL_PASSWORD = "xijs wzcu hdoy tvvc"
    EMAIL_RECIPIENT = "14ericfeng@gmail.com"
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

def test_email():
    """Test email sending functionality"""
    print("🧪 Testing Email Functionality")
    print("=" * 40)
    
    if not EMAIL_ENABLED:
        print("❌ Email is disabled in configuration")
        return False
    
    print(f"📧 Sender: {EMAIL_SENDER}")
    print(f"📧 Recipient: {EMAIL_RECIPIENT}")
    print(f"📧 SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECIPIENT
        msg['Subject'] = "🧪 Test Email from Raspberry Pi Temperature Monitor"
        
        body = f"""
This is a test email from your Raspberry Pi temperature monitoring system.

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If you receive this email, the email functionality is working correctly!
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        print("📤 Sending test email...")
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, text)
        server.quit()
        
        print("✅ Test email sent successfully!")
        print("📧 Check your email inbox for the test message.")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your Gmail App Password is correct")
        print("2. Ensure 2-Step Verification is enabled on your Google account")
        print("3. Verify the email addresses are correct")
        print("4. Check your internet connection")
        return False

if __name__ == "__main__":
    test_email()

