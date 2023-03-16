import os
import openai
from dotenv.main import load_dotenv

# This definitely should not be stored like this
load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

usr_input = input("Hello what symptoms are you experiencing? ")


# print(response.choices[0].text)
# usr_input = input()

# response = openai.Completion.create(
# model="text-davinci-003",
# prompt= "Here are the answers \n" + usr_input + "What do you think the problem is?",
# temperature=1,
# max_tokens=859,
# top_p=1,
# frequency_penalty=0,
# presence_penalty=0
# )

# print(response.choices[0].text)

messages = [{"role": "system", "content": "You are a doctor. You are workign with\
         a patient who does not have access to a doctor they can see in person."},
        {"role": "user", "content": "I am your patient and you are my doctor.\
         unfortunately I'm unable to see a doctor in person, so you are going\
         to need to help me diagnose my symptoms as bst you can."},
        {"role": "assistant", "content": "What symptoms are you experiencing"},
        {"role": "user", "content": usr_input + "What followup questions do you have?\
          Please format questions as a list with multiple choice options."}]


ans = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=messages
)

moreFollowups = True

while moreFollowups:
    usr_input = input(ans.choices[0].message.content + "\n")

    messages.append({"role": "assistant", "content": ans.choices[0].message.content})
    messages.append({"role": "user", "content": usr_input + "Do you have any more \
                     followup questions? Please only answer with a yes or a no."})

    ans = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = messages
    )

    # print("Ready for diagnosis answer is: " + ans.choices[0].message.content)

    if not ("yes" in ans.choices[0].message.content or "Yes" in ans.choices[0].message.content):
        moreFollowups = False
    else:
        messages.append({"role": "assistant", "content": ans.choices[0].message.content})
        messages.append({"role": "user", "content": "What additional followup \
                         questions do you have? Again, please format questions \
                        as a list with multiple choice options."})
        ans = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = messages
        )

messages.append({"role": "assistant", "content": "Yes."})
messages.append({"role": "user", "content": "What is your diagnosis?"})
ans = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages = messages
)

print(ans.choices[0].message.content)