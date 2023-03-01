import os
import openai
from dotenv.main import load_dotenv

# This definitely should not be stored like this
load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

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