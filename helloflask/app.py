import requests
import os
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
        raise ValueError(f"Could not find location: {place_name}")
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

#Testing weather
if __name__ == "__main__":
    lat, lng = long_lat("Boston Common")
    print(get_weather(lat, lng))

#OpenAI API function
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

Return:
- 3 indoor activities
- 3 outdoor activities
- 2 hidden gems
- 3 free activities
- 2 family-friendly activities
""",
        },
    ]

    response = client.responses.create(
        model="gpt-5-nano",
        input=messages,
    )

    result = response.output_text
    return result

#Testing Weather
if __name__ == "__main__":
    place = "Boston Common"

    # 1. Get coordinates from Mapbox
    lat, lng = long_lat(place)

    # 2. Get weather from OpenWeather
    weather = get_weather(lat, lng)

    # 3. Get OpenAI recommendations
    recs = open_ai_recs(place, weather)

    # 4. Print results
    print("\n=== WEATHER ===")
    print(weather)

    print("\n=== AI RECOMMENDATIONS ===")
    print(recs)
#Flask Section







    
