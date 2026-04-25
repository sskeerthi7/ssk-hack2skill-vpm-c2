import os
import json
import datetime
from flask import Flask, render_template, request, jsonify
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# Constants for 2026 Election Data
ELECTION_DATA_2026 = {
    "Phase I": {
        "States": ["Tamil Nadu", "Maharashtra", "Gujarat", "West Bengal"],
        "Poll Date": datetime.date(2026, 4, 23),
        "Counting Date": datetime.date(2026, 5, 4),
        "Status": "Polls Completed. Counting in Progress."
    },
    "Completed": {
        "States": ["Assam", "Kerala", "Puducherry"],
        "Poll Date": datetime.date(2026, 4, 9),
        "Status": "Result Tracking Active."
    },
    "Telangana": {
        "Municipal Poll Date": datetime.date(2026, 2, 11),
        "Next Focus": "GHMC (Hyderabad) Corporations Elections"
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/init', methods=['POST'])
def init_voter():
    data = request.json
    year_of_birth = int(data.get('year_of_birth'))
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
        
    return jsonify(hub_info)

@app.route('/api/chat', methods=['POST'])
def chat():
    query = request.json.get('query')
    if not model:
        return jsonify({"response": "AI Mode offline. Please configure GEMINI_API_KEY."})
    
    prompt = f"As VoterOne, an Indian Election Concierge, answer this query concisely: {query}"
    response = model.generate_content(prompt)
    return jsonify({"response": response.text})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
