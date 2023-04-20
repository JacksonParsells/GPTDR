import os
import openai
from dotenv import load_dotenv

load_dotenv('.env')


class GPTDR:
    def __init__(self, openai_api_key):
        self.openai_instance = openai
        self.openai_instance.api_key = openai_api_key
        self.num_runs = 0
        self.messages = [{"role": "system", "content": "You are a very smart doctor. You are working with\
         a patient who does not have access to a doctor they can see in person, and you are going to help \
                          them figure out their medical issue."},
                         {"role": "user", "content": "I am your patient and you are my doctor.\
                            unfortunately I'm unable to see a doctor in person, so you are going\
                            to need to help me diagnose my symptoms as best you can."},
                         {"role": "assistant", "content": "What symptoms are you experiencing?"}]

    def create_initial_text(self, user_input):
        self.messages.append({"role": "user", "content": user_input + "What followup questions do you have?\
          Please format questions as a list with multiple choice options."})

        ans = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )

        while not "a." in ans.choices[0].message.content:
            ans = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.messages
            )

        self.num_runs += 1
        self.messages.append(
            {"role": "assistant", "content": ans.choices[0].message.content})

        return ans.choices[0].message.content

    def create_followup_text(self, user_input):
        temp_messages = self.messages + [{"role": "user", "content": user_input +
                                          "Are you prepared to make a diagnosis? If so, say yes. If not, say no."}]

        ans = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=temp_messages
        )

        if 'yes' in ans.choices[0].message.content or self.num_runs > 2:
            self.messages.append({"role": "user", "content": user_input +
                                 "What is your diagnosis, and how do you recommend treating it? Do not include any followup questions here."})
        else:
            self.messages.append(
                {"role": "user", "content": user_input + "What followup \
                 questions do you have to figure out what the issue is? \
                 Remember that I don't have ready access to a doctor right now. \
                 Please format questions as a list with multiple choice options a. through d.\
                 and limit the number of questions to 4."})

        ans = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )

        while not "a." in ans.choices[0].message.content:
            ans = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.messages
            )

        self.num_runs += 1
        self.messages.append(
            {"role": "assistant", "content": ans.choices[0].message.content})

        return ans.choices[0].message.content
