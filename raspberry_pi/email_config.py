# Email Configuration for Raspberry Pi Temperature Monitor
# Modify these settings as needed

# Email Settings
EMAIL_ENABLED = True  # Set to False to disable email alerts
EMAIL_SENDER = "ericfeng242@gmail.com"
EMAIL_PASSWORD = "xijs wzcu hdoy tvvc"  # Gmail App Password
EMAIL_RECIPIENT = "14ericfeng@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Temperature Alert Settings
TEMP_THRESHOLD_C = 30.0  # Temperature threshold in Celsius
EMAIL_COOLDOWN_MINUTES = 30  # Minutes between email alerts

# Notes:
# 1. For Gmail, you need to use an "App Password" instead of your regular password
#    - Go to Google Account settings > Security > 2-Step Verification > App passwords
#    - Generate a new app password for this application
# 2. The temperature threshold is in Celsius (30.0 = 86°F)
# 3. Email alerts have a cooldown period to prevent spam
# 4. You can add multiple recipients by separating with commas: "email1@example.com,email2@example.com"
