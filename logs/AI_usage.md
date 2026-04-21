##What you asked - the prompt or question
[To give a bit of context, all the code starting at the very top when I do the initial set up i.e. importing libaries/initalizing API keys and the MapBox and OpenWeather API function base code are all code I got from class and my mini project. It gave me a really strong basis to begin and embelish with AI. As for the Open AI API function, I tried to use the demo class code but the context was different. Here are the things I asked:

1. How do I go about including code that will handle errors related to the API itself i.e. running out of API calls/etc?
2. How do I add code that handles a user incorrectly typing something in or some random gibberish or if MapBox is unable to find the location at all?  
3. I pasted the demo code into AI and asked, "How can I alter this to match my project context?"  
4. Once the weather and activities are given, I also want the user to be able to directly use the activities' website or booking page to make a reservation or learn more. How can I do that?]


##What AI generated - the output you received
[Here's the output I received from the accompanying questions: 

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
For the website: use the official website or bookings page if it exists. If there are none or if it is difficult to find, use https://www.google.com/search?q=Activity+Name+{place}]


##What you did with it - how you verified, modified, or integrated the output
[]
##What you learned - what you understood better as a result
[]