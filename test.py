import os
import openai

# This definitely should not be stored like this
openai.api_key = "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"

usr_input = input("Hello what are your symptoms? ")


response = openai.Completion.create(
model="text-davinci-003",
prompt=usr_input + "in order to diagnose this problem, what followup \
questions do you have? Please format followup questions as a list.",
temperature=1,
max_tokens=859,
top_p=1,
frequency_penalty=0,
presence_penalty=0
)

print(response.choices[0].text)
usr_input = input()

response = openai.Completion.create(
model="text-davinci-003",
prompt= "Here are the answers \n" + usr_input + "What do you think the problem is?",
temperature=1,
max_tokens=859,
top_p=1,
frequency_penalty=0,
presence_penalty=0
)

print(response.choices[0].text)