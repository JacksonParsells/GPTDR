"""
twilio.py wraps the twilio API for GPTDR
"""

from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse, Dial, Gather
from flask import Flask, request, redirect
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv
import GPTDR
import time

app = Flask(__name__)
load_dotenv('.env')

# init constants
DEFAULTINTROTEXT = "Welcome to GPTDR! Thank you for providing initial \
                       information for the diagnosis. To continue on, please \
                       answer a few more questions."
CALLRESPONSE1 = "Welcome to GPTDR! Thank you for calling. Following this\
                        message, please accept the return call and  provide \
                        a quick description of what your problem is, including \
                        the area affected, when the issue began, and any symptoms."
CALLBACKMESSAGE = "Please describe your problem, including the area affected, \
                        when the issue began, and any symptoms after the beep. \
                            Press the pound key when you are finished."
TESTSUBCRIBEDNUMBER = '+13025841779'
GPTDRPHONENUMBER = '+18885143317'

# init variables
key = "TWILIO_AUTH_TOKEN"
sid = "ACCOUNT_SID"
account_sid = os.getenv(sid)
auth_token = os.getenv(key)
client = Client(account_sid, auth_token)
openai_api_key = os.getenv("OPENAI_API_KEY")

"""
phase 1 - user call and initial message
"""


@app.route('/call', methods=['GET', 'POST'])
def call():
    # create a new Twilio voice response object
    resp = VoiceResponse()

    # get the user's phone number
    user_phone_number = request.values.get('From')

    # ask the user to press any key to continue, call the connect function with
    # the user's phone number as a parameter
    gather = Gather(num_digits=1,
                    action=request.url_root + 'connect/' + user_phone_number,
                    method='POST')
    gather.say(CALLRESPONSE1)
    resp.append(gather)

    # return the Twilio voice response to the user
    return str(resp)


@app.route('/connect/<phone_number>', methods=['GET', 'POST'])
def connect(phone_number):
    # create a new Twilio voice response object
    resp = VoiceResponse()

    call = client.calls.create(
        to=phone_number,  # the user's phone number
        from_=GPTDRPHONENUMBER,  # your Twilio phone number
        url=request.url_root + 'record/' + phone_number
    )

    # return the Twilio voice response to Twilio
    return str(resp)


@app.route('/record/<phone_number>', methods=['GET', 'POST'])
def record(phone_number):
    # create a new Twilio voice response object
    resp = VoiceResponse()

    # add a message that will be played to the user
    resp.say(CALLBACKMESSAGE)

    # record the user's response until they press the # key
    resp.record(finish_on_key='#', transcribe=True,
                transcribe_callback=request.url_root + 'process/' + phone_number)

    # hang up the call
    resp.hangup()

    # return the Twilio voice response to Twilio
    return str(resp)


@app.route('/process/<phone_number>', methods=['GET', 'POST'])
def process(phone_number):
    # create a new Twilio voice response object
    resp = VoiceResponse()

    # get the transcription of the recording from the request
    user_response = request.values.get('TranscriptionText')

    # add a message that will be played to the user
    resp.say("Thank you for your response. We will contact you shortly.")

    # hang up the call
    resp.hangup()

    # call the sms function with the user's phone number as a parameter
    sms(phone_number, user_response)

    # return the Twilio voice response to Twilio
    return str(resp)


"""
phase 2 - user text and follow up questions
"""


@app.route('/sms/<phone_number><user_response>', methods=['GET', 'POST'])
def sms(phone_number, user_response):
    print("sms called")
    print(phone_number, user_response)

    gpt_dr = GPTDR.GPTDR(openai_api_key)
    GPTDRresponse = gpt_dr.create_initial_text(user_response)

    # create a new Twilio voice response object
    message = client.messages.create(
        to=phone_number,
        from_=GPTDRPHONENUMBER,
        body=GPTDRresponse
    )

    return str(message)


if __name__ == "__main__":
    app.run(debug=True)
