import json
import random
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
from googleapiclient.discovery import build
import os

class Chatbot:
    def __init__(self, weather_api_key, google_api_key, google_cse_id):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise OSError(
                "Spacy model 'en_core_web_sm' not found. Please install it with:\n"
                "python -m spacy download en_core_web_sm"
            )
        self.vectorizer = TfidfVectorizer()
        self.load_knowledge_base()
        self.fit_vectorizer()
        self.weather_api_key = weather_api_key
        self.google_api_key = google_api_key
        self.google_cse_id = google_cse_id

    def load_knowledge_base(self):
        try:
            with open('knowledge_base.json', 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                "knowledge_base.json not found. Please ensure the file exists in the correct location."
            )
        except json.JSONDecodeError:
            raise ValueError(
                "Error parsing knowledge_base.json. Please ensure it is valid JSON."
            )

    def fit_vectorizer(self):
        corpus = [q for intent in self.knowledge_base['intents'] for q in intent['questions']]
        self.vectorizer.fit(corpus)

    def google_search(self, query):
        try:
            service = build("customsearch", "v1", developerKey=self.google_api_key)
            result = service.cse().list(q=query, cx=self.google_cse_id, num=1).execute()
            
            if "items" in result:
                # Extract the snippet from the first result
                snippet = result["items"][0]["snippet"]
                link = result["items"][0]["link"]
                return f"{snippet}\n\nSource: {link}"
            return None
        except Exception as e:
            print(f"Google search error: {str(e)}")
            return None

    def get_response(self, user_input):
        if "weather" in user_input.lower():
            return self.get_weather("haldwani")
        
        user_input_vec = self.vectorizer.transform([user_input])
        best_match = None
        best_similarity = 0

        # Tokenize and lemmatize user input
        doc = self.nlp(user_input.lower())
        user_tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]

        for intent in self.knowledge_base['intents']:
            # Check for keyword matches
            if any(keyword in user_tokens for keyword in intent.get('keywords', [])):
                return random.choice(intent['responses'])

            for question in intent['questions']:
                question_vec = self.vectorizer.transform([question])
                similarity = cosine_similarity(user_input_vec, question_vec)[0][0]
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = intent

        if best_match and best_similarity > 0.5:
            return random.choice(best_match['responses'])
        else:
            # Try Google search if no good match found
            google_result = self.google_search(user_input)
            if google_result:
                return f"I found this information online:\n\n{google_result}"
            return "I'm sorry, I don't understand. Could you please rephrase your question or provide more details?"

    def get_weather(self, city):
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": self.weather_api_key,
            "units": "metric"
        }
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if response.status_code == 200:
                weather_desc = data['weather'][0]['description']
                temp = data['main']['temp']
                return f"The current weather in {city} is {weather_desc} with a temperature of {temp}°C."
            else:
                return f"Sorry, I couldn't fetch the weather data for {city}. Error: {data.get('message', 'Unknown error')}"
        except requests.exceptions.RequestException as e:
            return f"An error occurred while fetching weather data: {str(e)}"

    def search_google(self, query):
        # Implement Google search using self.google_api_key and self.google_cse_id
        return self.google_search(query)  # Reuse the google_search method

