import os
import openai
from dotenv import load_dotenv

load_dotenv('.env')


class GPTDR:
    def __init__(self, openai_api_key):
        self.openai_instance = openai
        self.openai_instance.api_key = openai_api_key

    def create_initial_text(self, user_input):
        messages = [{"role": "system", "content": "You are a doctor. You are workign with\
         a patient who does not have access to a doctor they can see in person."},
                    {"role": "user", "content": "I am your patient and you are my doctor.\
         unfortunately I'm unable to see a doctor in person, so you are going\
         to need to help me diagnose my symptoms as bst you can."},
                    {"role": "assistant", "content": "What symptoms are you experiencing"},
                    {"role": "user", "content": user_input + "What followup questions do you have?\
          Please format questions as a list with multiple choice options."}]

        ans = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        return ans.choices[0].text

    def create_followup_text(self, user_input):
        # TODO: add the repeated followups
        moreFollowups = True
        response = self.openai_instance.Completion.create(
            model="text-davinci-003",
            prompt="Here are the answers \n" + user_input +
            "What do you think the problem is?",
            temperature=1,
            max_tokens=859,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        return response.choices[0].text, moreFollowups


openai_api_key = os.getenv("OPENAI_API_KEY")

gpt_dr = GPTDR(openai_api_key)

print(gpt_dr.create_initial_text("I have a headache"))
print(gpt_dr.create_followup_text("I have a headache"))
