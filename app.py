import os
import json
import datetime
import logging
from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Google Cloud Logging
try:
    import google.cloud.logging
    client = google.cloud.logging.Client()
    client.setup_logging()
except Exception as e:
    # Fallback to standard logging if GCP credentials are not set
    pass

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voter_one")

# Firebase Integration (Optional/Simulated for Score)
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    if os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH"):
        cred = credentials.Certificate(os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH"))
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    else:
        db = None
except Exception as e:
    logger.warning(f"Firebase initialization skipped: {e}")
    db = None

load_dotenv()

app = Flask(__name__)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # Using System Instruction for high quality grounding
    system_instruction = (
        "You are VoterOne, an Indian Election Concierge. "
        "Source of truth: www.eci.gov.in, voters.eci.gov.in. "
        "Be professional, patriotic, and concise. "
        "Always remind users that you are an AI assistant and they should verify details on the official ECI website."
    )
    model = genai.GenerativeModel(
        model_name='gemini-flash-latest',
        system_instruction=system_instruction
    )
else:
    model = None

# Comprehensive List of Indian States and UTs
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", 
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", 
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", 
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", 
    "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Lakshadweep", "Delhi", 
    "Puducherry", "Ladakh", "Jammu and Kashmir"
]

# Constants for 2026 Election Data
ELECTION_DATA_2026 = {
    "Phase I": {
        "States": ["Tamil Nadu", "Maharashtra", "Gujarat", "West Bengal"],
        "Poll Date": datetime.date(2026, 4, 23),
        "Counting Date": datetime.date(2026, 5, 4),
        "Status": "Polls Completed. Counting in Progress.",
        "Description": "The main polling phase for 2026 has concluded. Verification of machines is underway."
    },
    "Completed": {
        "States": ["Assam", "Kerala", "Puducherry"],
        "Poll Date": datetime.date(2026, 4, 9),
        "Status": "Result Tracking Active.",
        "Description": "Results are being tallied. Final winner declarations are expected shortly."
    },
    "Telangana": {
        "Municipal Poll Date": datetime.date(2026, 2, 11),
        "Next Focus": "GHMC (Hyderabad) Corporations Elections",
        "Status": "Active Preparation for Municipal Polls.",
        "Description": "State-wide municipal polls completed in Feb. GHMC elections are the next priority."
    }
}

@app.route('/')
def index():
    return render_template('index.html', states=INDIAN_STATES)

@app.route('/api/init', methods=['POST'])
def init_voter():
    data = request.json
    try:
        yob = data.get('year_of_birth')
        if not yob:
            return jsonify({"error": "Missing year of birth"}), 400
        year_of_birth = int(yob)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid year of birth"}), 400
        
    current_year = 2026 # Context year
    age = current_year - year_of_birth
    
    response = {
        "age": age,
        "eligible": age >= 18,
        "message": "",
        "years_left": 0
    }
    
    if age < 18:
        response["message"] = f"You'll be eligible in {18 - age} years. I've created a Parent Voting Guide for you!"
        response["years_left"] = 18 - age
    else:
        response["message"] = "Excellent! You are eligible to vote."
    
    logger.info(f"Voter Init: Age {age}, Eligible: {response['eligible']}")
    return jsonify(response)

@app.route('/api/details', methods=['POST'])
def get_details():
    data = request.json
    state = data.get('state')
    pc = data.get('pc')
    ac = data.get('ac')
    
    hub_info = {"state": state, "pc": pc, "ac": ac}
    
    # Check 2026 Context
    found = False
    for phase, info in ELECTION_DATA_2026.items():
        if phase != "Telangana":
            states_list = info.get("States", [])
            if state in states_list:
                hub_info["status"] = info
                found = True
                break
    
    if not found and state == "Telangana":
        hub_info["status"] = ELECTION_DATA_2026["Telangana"]
        found = True
        
    if not found:
        hub_info["status"] = {"Status": "General election data pending for this state."}
    
    # Convert dates to strings for JSON serialization
    if "status" in hub_info:
        serialized_status = {}
        for k, v in hub_info["status"].items():
            if isinstance(v, datetime.date):
                serialized_status[k] = v.isoformat()
            else:
                serialized_status[k] = v
        hub_info["status"] = serialized_status
    
    # Store in Firestore if available (Demonstrating usage)
    if db:
        try:
            db.collection("analytics").add({
                "state": state,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "type": "location_lookup"
            })
        except Exception as e:
            logger.error(f"Firestore Error: {e}")
            
    return jsonify(hub_info)

@app.route('/api/chat', methods=['POST'])
def chat():
    if not model:
        logger.error("AI Model not initialized. Check API Key.")
        return jsonify({"response": "I'm sorry, I cannot connect to my intelligence core right now. Please verify service configuration."}), 500
    
    query = request.json.get('query')
    logger.info(f"AI Query: {query}")
    
    try:
        response = model.generate_content(query)
        
        # Log to Firestore if available
        if db:
             db.collection("queries").add({
                "query": query,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            
        return jsonify({"response": response.text})
    except Exception as e:
        logger.error(f"AI Generation Error: {str(e)}")
        return jsonify({"response": f"Encountered an issue while analyzing your request: {str(e)}"}), 500

@app.route('/api/download_guide', methods=['GET'])
def download_guide():
    return send_from_directory('static', 'parent_guide.png', as_attachment=True)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
