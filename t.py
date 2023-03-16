"""
twilio.py wraps the twilio API for GPTDR
"""

from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
from flask import Flask, request, redirect
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv
import time

app = Flask(__name__)
load_dotenv('.env')

# init constants
DEFAULTINTROTEXT = "Welcome to GPTDR! Thank you for providing initial \
                       information for the diagnosis. To continue on, please \
                       answer a few more questions."
DEFAULTCALLRESPONSE = "Welcome to GPTDR! Thank you for calling. Following this\
                        message, please accept the return call and  provide \
                        a quick description of what your problem is, including \
                        the area affected, when the issue began, and any symptoms. \
                        press 1 for return call"
TESTSUBCRIBEDNUMBER = '+13025841779'
GPTDRPHONENUMBER = '+18885143317'

# init variables
key = "TWILIO_AUTH_TOKEN"
sid = "ACCOUNT_SID"
account_sid = os.getenv(sid)
auth_token = os.getenv(key)
client = Client(account_sid, auth_token)

"""
phase 1 - user call and initial message
"""


@app.route("/answer", methods=['GET', 'POST'])
def answer():
    """Respond to incoming phone calls with a message."""
    # Start our TwiML response
    resp = VoiceResponse()

    caller = request.values.get('From')
    twilio_number = request.values.get('To')

    with resp.gather(numDigits=1, action='/call-back', method='POST') as gather:
        gather.say(DEFAULTCALLRESPONSE, voice='alice')

    send_sms(caller, twilio_number)

    return str(resp)


@app.route("/call-back", methods=['GET', 'POST'])
def call_back():
    """returns a call (for cost reasons) and records user description"""
    resp = VoiceResponse()
    resp.say('Hello. Please describe your problem after the beep.')
    resp.record()
    call = client.calls.create(
        record=True,
        to=TESTSUBCRIBEDNUMBER,
        twiml=resp,
        from_=GPTDRPHONENUMBER
    )

    # response = VoiceResponse()

    # Use <Record> to record the caller's message

    # time.sleep(10)
    # End the call with <Hangup>
    resp.hangup()
    print(resp.xml)
    return str(resp)


def send_sms(to_number, from_number):
    """Using our caller's number and the number they called, send an SMS."""
    print('sending sms')
    print(to_number, from_number)
    try:
        client.messages.create(
            body=DEFAULTINTROTEXT,
            from_=from_number,
            to=to_number
        )
        print('sent')
    except TwilioRestException as exception:
        print(exception.code)
        # Check for invalid mobile number error from Twilio
        if exception.code == 21614:
            print("Uh oh, looks like this caller can't receive SMS messages.")


"""
SMS functions
"""


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    # Start our TwiML response
    resp = MessagingResponse()
    print('received message')

    # Determine the right reply for this message
    resp.message("we received the message: " + str(body) +
                 ". Thanks you for providing more information! This will be filled in with GPT data once this is combined with Sam's wok")

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
