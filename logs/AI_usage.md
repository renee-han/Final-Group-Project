##What you asked - the prompt or question
[To give a bit of context, all the code starting at the very top when we do the initial set up i.e. importing libaries/initalizing API keys and the MapBox and OpenWeather API function base code are all code we got from class and Renee's mini project. It gave us a really strong basis to begin and embellish with AI. As for the Open AI API function, we tried to use the demo class code but the context was different. Here are the things we asked:

1. How do I go about including code that will handle errors related to the API itself i.e. running out of API calls/etc?
2. How do I add code that handles a user incorrectly typing something in or some random gibberish or if MapBox is unable to find the location at all?  
3. I pasted the demo code into AI and asked, "How can I alter this to match my project context?"  
4. Once the weather and activities are given, I also want the user to be able to directly use the activities' website or booking page to make a reservation or learn more. How can I do that?
5. For the itinerary section, I used the similar code structure from the open_ai function, however, I asked AI, in def generate_itinerary(place, weather, recs): activities_list = "\n".join([f"- {a['name']} ({a['category']}, {a['price']})" for a in recs]), what does the code after activities_list do?
6. How can I create a SQLite table/database adjacent structure in a page after the output that displays unique itinerary links for users?
7. How can you build a user friendly interface for this app to make it look nice and easy to use?
8. Can you seperate with subheadings like indoor and outdoor rather than having them appear as tags? Then, I want to change tags like Hidden_Gem to appear as two words, like "Hidden Gem".
9. Can you create the webpage for the itinerary part of the web app and make it look coherent with the rest of the app?]

##What AI generated - the output you received
[Here's the output we received from the accompanying questions: 

1. Use response.raise_for_status() as it checks the HTTP response status code and raises an error if the request failed

2. Use if not data["features"]:
        raise ValueError(f"Could not find location: {place_name}")
        
3. def open_ai_recs(place, weather):
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
  4. Return a JSON array of 13 activities with this exact structure:
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

5. This line of code takes the list of recommended activities (recs), formats each activity into a readable bullet point string that includes its name, category, and price, and then combines all of those strings into one single text block. It uses a loop to process each activity dictionary, converts each one into a formatted line like “- Museum (Culture, $20),” and then joins all of those lines together with line breaks so the final result is a neatly formatted list stored in activities_list

6. @app.route("/itinerary", methods=["POST"])
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
and: #Itinerary SQL Lite Setup

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
7. Develop an HTML homepage with highlighted features, a search bar for locations, and an error message display. Then create a results page that is featuring the location and weather at the top, followed by activity cards with the name, description, price, and any applicable links. It also features a back button to return to the homepage.
8. Update the output HTML file to reorganize activities by categorys with clear subheadings. Then add CSS styles for new category subheadings and website links. After, update the styling of the activity cards to remove the category tags and adapt to the new layout.
9. Based on the app, the itinerary should display an hourly schedule, weather information, and a saved history of previous itineraries. It should have a header section, timeline schedule, responsive design, and consistent styling.]

##What you did with it - how you verified, modified, or integrated the output
[When AI gave back the code, we didn't just copy and paste it in VSCode and move along to the next task. We actually spent time trying to pick apart and dissect the code it gave back, as seen in our thorough annotations and comments. The whole point of this project is to learn and problem solve and if we just simply asked AI to generate code without really understanding what was going on, there would be no point of learning! Once we asked something from Claude or ChatGPT, we actually asked follow up questions after it was done generating i.e. why did you do xyz?, I'm confused with xyz part, can you explain it again, or I want to keep things simpler as I'm a beginner in Python, how can you edit the code or the way you explain something to explain that? Once all those knots were combed through, then we moved on to the next task. We also used the agent function to reflect on the code we had already built and move forward to advance our project. This allowed us to easily review any changes that were being made before we saved them, and also allowed us to track our progress. After implementing any changes, we made sure to test our code and ensure everything was running properly and if it wasn't, we would make necessary adjustments. We also checked the output of the app to ensure it was correct information that was being given.]

##What you learned - what you understood better as a result
[The main takeaway that we had from this project was that you don't need to be an expert at coding in Python to build something that works, is useful, and looks nice. Our base understanding of the language allowed us to collaborate with each other and AI tools to build an app that we would actually use in everyday life. It also taught us about the power of APIs, especially when they are combined with each other. For example, the output of our OpenAI API depended on the OpenWeather API, so we were able to add value to our project with unique combinations of APIs. The use of AI for this project also helped our understanding of error messages, because we had both experienced frustration in the past with interpreting and remedying error messages. However, with the help of AI, we could have the explanation of what went wrong in plain English and step by step instructions on how to fix it, making coding less stressful.]