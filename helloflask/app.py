import requests
import os
import json 
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv() #goes into env file and loads the API key and the variable its assigned to into Python memory
client = OpenAI()
from flask import Flask, render_template, request
MAPBOX_KEY = os.getenv("MAPBOX_TOKEN")
OPEN_AI_KEY = os.getenv("OPENAI_API_KEY")
OPEN_WEATHER_KEY = os.getenv("OPENWEATHER_KEY")

#Itinerary SQL Lite Setup

def init_db():
    conn = sqlite3.connect("itineraries.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itineraries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place TEXT,
            date TEXT,
            weather TEXT,
            schedule TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

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
                "Give suggestions for activities to do based on weather and location. Keep it concise." "Always respond with valid JSON only. No extra text, no markdown, no code blocks."
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

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=messages,
    )

    result = json.loads(response.choices[0].message.content)  # add this
    return result  

#Itinerary Section
def generate_itinerary(place, weather, recs):
    activities_list = "\n".join([f"- {a['name']} ({a['category']}, {a['price']})" for a in recs])
    
    messages = [
        {
            "role": "system",
            "content": "You are a travel itinerary planner. Always respond with valid JSON only. No extra text, no markdown, no code blocks."
        },
        {
            "role": "user",
            "content": f"""
Location: {place}
Weather: {weather['description']}, {weather['temp']}F
Available activities:
{activities_list}

Create an hour by hour itinerary from 9:00 AM to 9:00 PM using these activities. No meals or restaurants.
Every single hour must have an entry.
Return a JSON array with this exact structure:
[
  {{
    "time": "9:00 AM",
    "activity": "Activity name",
    "duration": "1 hour",
    "description": "What to do/expect this hour",
    "tips": "Practical tip",
    "category": "indoor"
  }}
]

Rules:
- Every hour from 9 AM to 9 PM must have an entry
- No food, meals, or restaurants
- Make activities flow logically by location
- Account for travel time between locations
- Pick activities that make sense given the weather
""",
        },
    ]

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=messages,
    )

    result = json.loads(response.choices[0].message.content)
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


@app.route("/itinerary", methods=["POST"])
def itinerary():
    place = request.form["place"]
    try:
        lat, lng = long_lat(place)
        weather = get_weather(lat, lng)
        recs = open_ai_recs(place, weather)
        schedule = generate_itinerary(place, weather, recs)

        # Save to SQLite
        conn = sqlite3.connect("itineraries.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO itineraries (place, date, weather, schedule)
            VALUES (?, ?, ?, ?)
        """, (
            place,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            f"{weather['description']}, {weather['temp']}F",
            json.dumps(schedule)
        ))
        conn.commit()
        conn.close()

        # Fetch history
        conn = sqlite3.connect("itineraries.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, place, date, weather FROM itineraries ORDER BY id DESC")
        history = cursor.fetchall()
        conn.close()

        return render_template("itinerary.html",
            place=place,
            weather=weather,
            schedule=schedule,
            history=history,
            lat=lat,
            lng=lng,
            mapbox_token=MAPBOX_KEY
        )
    except Exception as e:
        return render_template("index.html", error=f"Something went wrong: {e}")
    
@app.route("/itinerary/<int:id>")
def view_itinerary(id):
    try:
        conn = sqlite3.connect("itineraries.db")
        cursor = conn.cursor()
        cursor.execute("SELECT place, date, weather, schedule FROM itineraries WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return render_template("index.html", error="Itinerary not found.")

        place = row[0]
        date = row[1]
        weather_str = row[2]
        schedule = json.loads(row[3])  # converts JSON string back to Python list

        return render_template("itinerary.html",
            place=place,
            date=date,
            weather={"description": weather_str, "temp": "", "feels_like": "", "humidity": "", "city": place},
            schedule=schedule,
            history=[],  # no need to show history when viewing a saved one
            lat=None,
            lng=None,
            mapbox_token=MAPBOX_KEY
        )
    except Exception as e:
        return render_template("index.html", error=f"Something went wrong: {e}")

if __name__ == "__main__":
    app.run(debug=True)








    
