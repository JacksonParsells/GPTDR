import requests
import re

import math
import pandas as pd
import json
import googlemaps
api_key = 'AIzaSyCfuq3GcxyeMVrF0kp3YePV-WnkB_R_u0s'
gmaps = googlemaps.Client(key=api_key)

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

# Print data frame
# print(df)

# Define the Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371 # Radius of the earth in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c # Distance in km
    return d

def geoLocation(address):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key=AIzaSyCfuq3GcxyeMVrF0kp3YePV-WnkB_R_u0s"
    response = requests.get(url)
    data = response.json()
    location = data["results"][0]["geometry"]["location"]
    return location
# param: a string of location
# 
def nearestClinic(geoName):
    start_location_dict = geoLocation(geoName)
    start_location = (start_location_dict['lat'], start_location_dict['lng'])
    locations = []
    for index, row in df.iterrows():
        locations.append(row.tolist())
    distances = []

    for location in locations:
        distance = haversine(start_location[0], start_location[1], location[2], location[3])
        distances.append(distance)
    index_of_closest_location = distances.index(min(distances))
    end_location = str (locations[index_of_closest_location][1])
    closest = "Closest location: " + str (locations[index_of_closest_location][1]) + ", " + str(round(distances[index_of_closest_location],2)) + "km away."
    print(closest)
    mode="driving"
    directions_result = gmaps.directions(start_location, end_location, mode="driving")
    
    guide = ""
    for step in directions_result[0]['legs'][0]['steps']:
        instructions = step['html_instructions']
        instructions = re.sub("<.*?>", "", instructions)
        guide += instructions + "\n"
    print(guide)

#TODO: 
nearestClinic("National Childrens Park and Zoo Abuja")