"""
twilio.py wraps the twilio API for GPTDR
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

# Set environment variables for your credentials
# Read more at http://twil.io/secure

load_dotenv('.env')

key = "TWILIO_AUTH_TOKEN"
account_sid = "AC51cd81e721fd58f313cfcc3738677592"
auth_token = os.getenv(key)
client = Client(account_sid, auth_token)

call = client.calls.create(
    url="http://demo.twilio.com/docs/voice.xml",
    to="+13025841779",
    from_="+18885143317"
)

print(call.sid)
