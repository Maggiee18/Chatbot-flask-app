from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
from datetime import datetime
import pytz
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure Gemini Flash API
try:
    genai.configure(api_key="AIzaSyBQ0i1YjBrNNpde8H9pXb0uWPhJ-N975gc")
    # Load the Gemini Flash model
    model = genai.GenerativeModel("gemini-1.5-flash")
    logger.info("Successfully configured Gemini API")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    model = None

def get_current_time():
    """Get the current time in IST with proper timezone handling"""
    current_timestamp = time.time()
    utc_time = datetime.fromtimestamp(current_timestamp, tz=pytz.UTC)
    ist_time = utc_time.astimezone(pytz.timezone('Asia/Kolkata'))
    return ist_time

def get_ai_response(prompt):
    """Get response from AI model with proper error handling"""
    if model is None:
        logger.error("Gemini model is not initialized")
        return None
        
    try:
        logger.debug(f"Sending prompt to Gemini: {prompt}")
        response = model.generate_content(prompt)
        logger.debug(f"Received response from Gemini: {response.text}")
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error getting AI response: {str(e)}")
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.json.get("message", "").strip()
        if not user_input:
            return jsonify({"reply": "Please enter a message."}), 400

        logger.debug(f"Received user input: {user_input}")

        # Get current time in Indian timezone
        current_time = get_current_time()
        
        # Handle greetings
        if any(greeting in user_input.lower() for greeting in ["hi", "hello", "hey", "greetings"]):
            return jsonify({
                "reply": "Hello! I'm your AI assistant. I can help you with various questions, tell you the time and date, and engage in conversation. How can I assist you today?",
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            })

        # For other queries, try the AI model
        ai_response = get_ai_response(user_input)
        if ai_response:
            return jsonify({
                "reply": ai_response,
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            })
        else:
            return jsonify({
                "reply": "I apologize, but I'm having trouble processing your request right now. Could you please try rephrasing your question or ask something else?",
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "reply": "I apologize, but I encountered an error. Please try again in a moment.",
            "timestamp": get_current_time().strftime("%Y-%m-%d %H:%M:%S %Z")
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
