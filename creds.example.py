# Copy this file to creds.py and fill in your values.
# creds.py is excluded from version control — never commit real credentials.

# ── Twilio (SMS) ───────────────────────────────────────────────────────────────
# https://console.twilio.com
account_sid           = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
auth_token            = 'your_auth_token_here'
messaging_service_sid = 'MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# Phone number to receive SMS alerts (E.164 format)
phone_receiver = '+15140000000'

# ── Gmail (Email) ──────────────────────────────────────────────────────────────
# Use a Gmail App Password — not your account password.
# https://support.google.com/accounts/answer/185833
email_user      = 'your_gmail@gmail.com'
email_password2 = 'your_app_password'        # 16-char App Password

# Address to receive email alerts (can be an email-to-SMS gateway, e.g. number@txt.bell.ca)
email_receiver  = 'receiver@example.com'
