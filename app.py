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

        # Handle time-related queries
        if any(phrase in user_input.lower() for phrase in ["what time", "current time", "time now", "time is it"]):
            time_str = current_time.strftime("%I:%M:%S %p")
            date_str = current_time.strftime("%B %d, %Y")
            return jsonify({
                "reply": f"The current time is {time_str} IST on {date_str}",
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            })
        
        # Handle date-related queries
        if any(phrase in user_input.lower() for phrase in ["date", "today's date", "what's the date"]):
            formatted_date = current_time.strftime("Today is %B %d, %Y")
            return jsonify({
                "reply": formatted_date,
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            })

        # Handle specific queries with predefined responses
        if "horror movie" in user_input.lower():
            return jsonify({
                "reply": "Here are some great horror movie recommendations:\n1. The Conjuring\n2. Get Out\n3. Hereditary\n4. The Babadook\n5. A Quiet Place\nWould you like more specific recommendations based on your preferences?",
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            })

        if "prime minister of india" in user_input.lower():
            return jsonify({
                "reply": "The current Prime Minister of India is Narendra Modi. He has been serving as the Prime Minister since May 26, 2014.",
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            })

        if "tell me a story" in user_input.lower():
            return jsonify({
                "reply": "Here's a short story:\n\n'The Last Light'\n\nIn a small coastal town, an old lighthouse keeper named Thomas had been tending to his light for 40 years. One stormy night, as the waves crashed against the rocks, he noticed something unusual in the beam of his light. A ship, unlike any he had seen before, was approaching the harbor. As it drew closer, he realized it was the same ship that had disappeared 40 years ago, the night he first became the keeper. The ship's crew waved to him, their faces frozen in time, as they passed by the lighthouse and vanished into the mist...",
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            })

        if "how do i learn programming" in user_input.lower():
            return jsonify({
                "reply": "Here's a structured approach to learning programming:\n\n1. Start with the basics:\n   - Choose a beginner-friendly language (Python is recommended)\n   - Learn basic concepts (variables, loops, conditions)\n   - Practice with simple exercises\n\n2. Follow a structured course:\n   - FreeCodeCamp\n   - Codecademy\n   - Coursera\n   - edX\n\n3. Build projects:\n   - Start with small projects\n   - Gradually increase complexity\n   - Build a portfolio\n\n4. Join communities:\n   - Stack Overflow\n   - GitHub\n   - Programming forums\n\n5. Practice regularly:\n   - Code daily\n   - Solve coding challenges\n   - Read other people's code\n\nWould you like more specific guidance for any of these steps?",
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
