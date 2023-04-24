import os
import openai
from dotenv import load_dotenv
load_dotenv('.env')

import math
import googlemaps
import json
import requests
import re
import pandas as pd
google_api_key = os.getenv("GOOGLE_API_KEY")
gmaps = googlemaps.Client(key=google_api_key)


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
                            to need to help me diagnose my ailment as best you can."},
                         {"role": "assistant", "content": "What symptoms are you experiencing?"}]
        self.delivered_diagnosis = False
        self.location_pending = False
        self.df = self.create_df()
        

    def create_initial_text(self, user_input):
        self.messages.append({"role": "user", "content": user_input + "What followup questions do you have?\
          Please format questions as a list with multiple choice options a. through d.\
          and limit the number of questions to 4."})

        ans = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )

        # while not "a." in ans.choices[0].message.content:
        # ans = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=self.messages
        # )

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

        if 'yes' in ans.choices[0].message.content or self.num_runs > 0:
            self.messages.append({"role": "user", "content": user_input +
                                 "What is your diagnosis, and how do you recommend treating it? Do not include any followup questions here."})
            self.delivered_diagnosis = True
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

        # while not "a." in ans.choices[0].message.content:
        # ans = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=self.messages
        #     )

        self.num_runs += 1
        self.messages.append(
            {"role": "assistant", "content": ans.choices[0].message.content})

        return ans.choices[0].message.content

    def create_df(self):
        # Read JSON file into Python object
        with open('hospitals.json') as f:
            data = json.load(f)

        # Convert Python object to data frame
        df = pd.DataFrame.from_records(data)

        # Filter rows where column 'col_name' contains 0
        mask = (df['Latitude'] == 0.0) | (df['Longitude'] == 0.0)
        rows_to_drop = df[mask].index

        # Drop the filtered rows from the DataFrame
        df.drop(index=rows_to_drop, inplace=True)

        return df
    

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371 # Radius of the earth in km
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat/2) * math.sin(dLat/2) + \
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
            math.sin(dLon/2) * math.sin(dLon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = R * c # Distance in km
        return d

    def geoLocation(self, address):
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={google_api_key}"
        response = requests.get(url)
        data = response.json()
        location = data["results"][0]["geometry"]["location"]
        return location
    
    def nearestClinic(self, geoName):
        start_location_dict = self.geoLocation(geoName)
        start_location = (start_location_dict['lat'], start_location_dict['lng'])
        locations = []
        for index, row in self.df.iterrows():
            locations.append(row.tolist())
        distances = []

        for location in locations:
            distance = self.haversine(start_location[0], start_location[1], \
                                      location[2], location[3])
            distances.append(distance)
        index_of_closest_location = distances.index(min(distances))
        end_location = str (locations[index_of_closest_location][1])
        closest =  str ("Closest medical facility: "\
                        +locations[index_of_closest_location][1]) + ", " \
                        + str(round(distances[index_of_closest_location],2)) + "km away."
        # print(closest)
        mode="driving"
        directions_result = gmaps.directions(start_location, end_location, mode="driving")
    
        guide = "Step by step guidance: " + "\n"
        for step in directions_result[0]['legs'][0]['steps']:
            instructions = step['html_instructions']
            instructions = re.sub("<.*?>", "", instructions)
            guide += instructions + "\n"
        # print(guide)
        route = (closest + "\n" + guide)
        return route
