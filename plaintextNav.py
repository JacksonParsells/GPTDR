import requests
import re

origin = "Toronto"
destination = "Montreal"
mode = "driving"
api_key = "AIzaSyCfuq3GcxyeMVrF0kp3YePV-WnkB_R_u0s"

url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode={mode}&key={api_key}"
response = requests.get(url)
data = response.json()

for leg in data["routes"][0]["legs"]:
    for step in leg["steps"]:
        instructions = step["html_instructions"]
        instructions = re.sub("<.*?>", "", instructions)
        print(instructions)

