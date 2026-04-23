import requests
import os
import json 
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv() #goes into env file and loads the API key and the variable its assigned to into Python memory
client = OpenAI()
from flask import Flask, render_template, request
MAPBOX_KEY = os.getenv("MAPBOX_TOKEN")
OPEN_AI_KEY = os.getenv("OPENAI_API_KEY")
OPEN_WEATHER_KEY = os.getenv("OPENWEATHER_KEY")



#API Pipeline Dev

#Function for taking location name and returning long/lat 
#How it all works: When I request from MapBox, I'm saying here's the location name w/ my API key. That request hits their servers i.e. computers+datbase w/ all this info and they verify my API key, takes in that location name, recognizes it bcz they already have associated location names and coordinates in their system+external data they used 
#This should work for anywhere in the world, not just Boston

def long_lat(place_name):
    url = "https://api.mapbox.com/search/searchbox/v1/forward"
    params = {"q": place_name, "access_token": MAPBOX_KEY, "limit": 1} 
    response = requests.get(url, params = params) #sends request to MapBox for data
    response.raise_for_status() #handles api errors 
    data = response.json()#converts data into dict/JSON form 
    if not data["features"]:
        raise ValueError(f"Could not find location: {place_name}") #if a user types in random nonsense and if Mapbox is unable to find the location, it will return a friendly error i.e. Can't find xyz location 
    print(data) #this is a list of dicts
    lng, lat = data["features"][0]["geometry"]["coordinates"]
     #tuple = unpacking/packing: assigning the first value to lng and second to lat
    return lat, lng


#data is a dictionary bcz you converted it into JSON
#'features': [{'type': 'Feature', 'geometry': {'coordinates': [-71.0795, 42.349516]
#features is a key and its value is that entire list 
#data[features] gets back the list
#data["features"][0] is getting the first value in the list which is {'type': 'Feature', 'geometry': {'coordinates': [-71.0795, 42.349516]
#data["features"][0]["geometry"] is getting {'coordinates': [-71.0795, 42.349516]
#data["features"][0]["geometry"]["coordinates"] getting [-71.0795, 42.349516]


#Second Function (Weather)
def get_weather(lat,lng):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lng,
        "appid": OPEN_WEATHER_KEY,
        "units": "imperial"  # Fahrenheit
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    weather = {
        "description": data["weather"][0]["description"],
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "city": data["name"]
    }
    return weather

#Third function (OpenAI)
def open_ai_recs(place, weather):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an activity recommendation engine for the user's local geographic area. "
                "Give suggestions for activities to do based on weather and location. Keep it concise."
            ),
        },
        {
            "role": "user",
            "content": f"""
Location: {place}
Weather: {weather['description']}, {weather['temp']}F

Return a JSON array of 13 activities with this exact structure:
[
  {{
    "name": "Activity name",
    "category": "indoor",
    "description": "Brief description",
    "price": "Free or estimated price e.g. $15-20",
    "website": "https://official website or booking page"
  }}
]

Categories must include:
- 3 indoor
- 3 outdoor  
- 2 hidden_gem
- 3 free
- 2 family_friendly
For the website: use the official website or bookings page if it exists. If there are none or if it is difficult to find, use https://www.google.com/search?q=Activity+Name+{place}
""",
        },
    ]

    response = client.responses.create(
        model="gpt-5-nano",
        input=messages,
    )

    result = json.loads(response.output_text)
    return result



#Testing Together 
if __name__ == "__main__":
    place = "Boston Common"
    lat, lng = long_lat(place)
    weather = get_weather(lat, lng)
    recs = open_ai_recs(place, weather)

    print("\n=== WEATHER ===")
    print(weather)

    print("\n=== RECOMMENDATIONS ===")
    for activity in recs:
        print(f"{activity['category'].upper()}")
        print(f"  {activity['name']}, {activity['price']}")
        print(f"  {activity['website']}")
        print()


#Flask Section
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recommendations", methods=["POST"])
def recommendations():
    place = request.form["place"]
    try:
        lat, lng = long_lat(place)
        weather = get_weather(lat,lng)
        recs = open_ai_recs(place, weather)
        return render_template("output.html",
            place=place,
            weather=weather,
            recs=recs,
            lat=lat,
            lng=lng,
            mapbox_token=MAPBOX_KEY
        )
    except Exception as e:
        return render_template("index.html", error=f"Something went wrong: {e}")

if __name__ == "__main__":
    app.run(debug=True)






    
