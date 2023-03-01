"""
Google Map API to find rough user 
API key: AIzaSyCfuq3GcxyeMVrF0kp3YePV-WnkB_R_u0s
"""
import requests

# Ask the user for an address
addressByName = "Tufts University"
addressByAddress = "419 Boston Ave"

# Use the Google Maps Geocoding API to get the coordinates
url = f"https://maps.googleapis.com/maps/api/geocode/json?address={addressByName}&key=AIzaSyCfuq3GcxyeMVrF0kp3YePV-WnkB_R_u0s"
response = requests.get(url)
data = response.json()
location = data["results"][0]["geometry"]["location"]

# Print the coordinates
print((location["lat"], location["lng"]))

"""
Naive Haversine algorithm to find shortest point to origin, given
"""