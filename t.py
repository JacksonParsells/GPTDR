"""
twilio.py wraps the twilio API for GPTDR
"""

from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request, redirect
import os
from twilio.rest import Client
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv('.env')

# init constants
DEFAULTINTROMESSAGE = "Welcome to GPTDR! Thank you for providing initial \
                       information for the diagnosis. To continue on, please \
                       answer a few more questions."
TESTSUBCRIBEDNUMBER = '+13025841779'
GPTDRPHONENUMBER = '+18885143317'

# init variables
key = "TWILIO_AUTH_TOKEN"
account_sid = "AC51cd81e721fd58f313cfcc3738677592"
auth_token = os.getenv(key)
client = Client(account_sid, auth_token)


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    resp = MessagingResponse()

    # Add a message
    resp.message(DEFAULTINTROMESSAGE)

    return str(resp)


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body == 'hello':
        resp.message("Hi!")
    elif body == 'bye':
        resp.message("Goodbye")

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
