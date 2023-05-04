"""
twilio.py wraps the twilio API for GPTDR
"""

from twilio.twiml.messaging_response import MessagingResponse, Message
from twilio.twiml.voice_response import VoiceResponse, Dial, Gather
from flask import Flask, request, redirect
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv
import GPTDR
import os
import time
import pandas as pd

app = Flask(__name__)
load_dotenv('.env')

# init constants
DEFAULTINTROTEXT = "Welcome to GPTDR! Thank you for providing initial \
                       information for the diagnosis. To continue on, please \
                       answer a few more questions. Format multiple choice responses as follows: \
                        [answer 1], [answer 2], [answer 3], [answer 4]"
CALLBACKMESSAGE = "Please describe your problem, including the area affected, \
                        when the issue began, and any symptoms after the beep. \
                        Hang up when you are finished.\
                        We will send you a text message with follow up \
                        questions. Once you answer those questions, we will \
                        send you a diagnosis and recommendations via text. \
                        Note that G P T D R is not a medical professional and \
                        is not liable for any advice or information it provides."
# CALLBACKMESSAGE = "respond fool"
GPTDRPHONENUMBER = '+18885143317'

# init variables
key = "TWILIO_AUTH_TOKEN"
sid = "ACCOUNT_SID"
account_sid = os.getenv(sid)
auth_token = os.getenv(key)
client = Client(account_sid, auth_token)
openai_api_key = os.getenv("OPENAI_API_KEY")
googlemaps_api_key = os.getenv("GOOGLEMAPS_API_KEY")
gpt_dr = GPTDR.GPTDR(openai_api_key, googlemaps_api_key)

"""
phase 1 - user call and initial message
"""


@app.route('/call', methods=['GET', 'POST'])
def call():
    # create a new Twilio voice response object
    resp = VoiceResponse()

    # reject initial call
    resp.reject(reason='busy')

    # get the user's phone number
    phone_number = request.values.get('From')

    # call the user's phone number
    call = client.calls.create(
        to=phone_number,  # the user's phone number
        from_=GPTDRPHONENUMBER,  # your Twilio phone number
        url=request.url_root + 'record/' + phone_number
    )

    # return the Twilio voice response to Twilio
    return str(resp)


@ app.route('/record/<phone_number>', methods=['GET', 'POST'])
def record(phone_number):
    # create a new Twilio voice response object
    resp = VoiceResponse()

    # add a message that will be played to the user
    resp.say(CALLBACKMESSAGE)

    # record the user's response until they hang up
    resp.record(transcribe=True, transcribe_callback=request.url_root +
                'process/' + phone_number)

    # hang up the call
    resp.hangup()

    # return the Twilio voice response to Twilio
    return str(resp)


@ app.route('/process/<phone_number>', methods=['GET', 'POST'])
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
    send_initial_text(phone_number, user_response)

    # return the Twilio voice response to Twilio
    return str(resp)


"""
phase 2 - user text and follow up questions
"""


def send_initial_text(phone_number, user_response):
    GPTDRresponse = DEFAULTINTROTEXT + gpt_dr.create_initial_text(user_response)

    # create a new Twilio voice response object
    message = client.messages.create(
        to=phone_number,
        from_=GPTDRPHONENUMBER,
        body=GPTDRresponse
    )

    return str(message)


@ app.route('/sms', methods=['GET', 'POST'])
def sms():
    # resp = MessagingResponse()
    resp = ""
    user_number = request.values.get('From')
    user_message = request.values.get('Body')
    if not gpt_dr.delivered_diagnosis:
        # create a new Twilio messaging response object

        # get the user's message

        # create a GPTDR instance and create a follow-up question
        follow_up_question = gpt_dr.create_followup_text(user_message)

        # add the follow-up question to the Twilio messaging response object
        if not gpt_dr.delivered_diagnosis:
            resp += follow_up_question
        else:
            resp += follow_up_question
            resp += " Would you like to see the nearest local medical facility? Respond yes or no."

    elif gpt_dr.location_pending:
        location_response = gpt_dr.nearestClinic(request.values.get('Body'))
        resp += location_response
    else:
        if request.values.get('Body').lower() == "yes":
            gpt_dr.location_pending = True
            resp += "Great! Please send the name the name of the town or city that you're in."
        else:
            resp += "It looks like you either said no or entered a command I don't recognize. Bye!"

    print("curling with ", resp)
    account_creds = '-u ' + account_sid + ':' + auth_token
    os.system("curl 'https://api.twilio.com/2010-04-01/Accounts/AC51cd81e721fd58f313cfcc3738677592/Messages.json' -X POST \
    --data-urlencode 'To=" + user_number + "' \
    --data-urlencode 'From=+18885143317' \
    --data-urlencode 'MessagingServiceSid=MG9638393c09012bcb7bb4d24c31e3af01' \
    --data-urlencode 'Body=" + resp.replace("'", "`") + "' \
    " + account_creds)

    return ""


if __name__ == "__main__":
    app.run(debug=True, port=5002)
