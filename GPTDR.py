import os
import openai
from dotenv import load_dotenv

load_dotenv('.env')


class GPTDR:
    def __init__(self, openai_api_key):
        self.openai_instance = openai
        self.openai_instance.api_key = openai_api_key
        self.num_runs = 0
        self.messages = [{"role": "system", "content": "You are a doctor. You are working with\
         a patient who does not have access to a doctor they can see in person."},
                         {"role": "user", "content": "I am your patient and you are my doctor.\
         unfortunately I'm unable to see a doctor in person, so you are going\
         to need to help me diagnose my symptoms as best you can."},
                         {"role": "assistant", "content": "What symptoms are you experiencing"}]

    def create_initial_text(self, user_input):
        self.messages.append({"role": "user", "content": user_input + "What followup questions do you have?\
          Please format questions as a list with multiple choice options."})

        ans = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )

        self.num_runs += 1
        self.messages.append(
            {"role": "assistant", "content": ans.choices[0].message.content})

        return ans.choices[0].message.content

    def create_followup_text(self, user_input):
        self.messages.append(
            {"role": "user", "content": user_input + "What followup questions do you have? Only ask if you need to.\
             Please format questions as a list with multiple choice options."})

        ans = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )

        self.num_runs += 1
        self.messages.append(
            {"role": "assistant", "content": ans.choices[0].message.content})

        return ans.choices[0].message.content


openai_api_key = os.getenv("OPENAI_API_KEY")

gpt_dr = GPTDR(openai_api_key)

# print(gpt_dr.create_initial_text("I have a headache"))
# print(gpt_dr.create_followup_text("I have a headache"))
# commenting out test code for annoyance when restarting
