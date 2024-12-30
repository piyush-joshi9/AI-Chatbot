import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from chatbot import Chatbot
from flask_cors import CORS
#from waitress import serve

# Create Flask app first
app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

# Get API keys
openweathermap_api_key = os.getenv("OPENWEATHERMAP_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
google_cse_id = os.getenv("GOOGLE_CSE_ID")

# Debugging: Print API keys to check if they are loaded
print("Weather API Key:", openweathermap_api_key)
print("Google API Key:", google_api_key)
print("Google CSE ID:", google_cse_id)

# Check if credentials are loaded
if not openweathermap_api_key or not google_api_key or not google_cse_id:
    app.logger.warning("One or more API credentials not found. Please check your .env file.")

# Initialize chatbot with all credentials
chatbot = Chatbot(openweathermap_api_key, google_api_key, google_cse_id)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
            
        user_message = request.json.get('message')
        if not user_message or not isinstance(user_message, str):
            return jsonify({'error': 'Message is required and must be a string'}), 400
            
        response = chatbot.get_response(user_message)
        return jsonify({'response': response})
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({'error': 'An internal server error occurred'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # Use this for development
    app.run(debug=True, port=5000, use_reloader=False)
    
    # Uncomment the following lines for production
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=5000)

