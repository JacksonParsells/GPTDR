import requests

def geoLocation(address):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key=AIzaSyCfuq3GcxyeMVrF0kp3YePV-WnkB_R_u0s"
    response = requests.get(url)
    data = response.json()
    #print("length of result :" + str(len(data["results"])))
    location = data["results"][0]["geometry"]["location"]
    return location

location = geoLocation("National Childrens Park & Zoo Abuja")
print((location["lat"], location["lng"]))