import os
import json
import datetime
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

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

class VoterOne:
    def __init__(self):
        self.profile = {}
        self.profile_file = "voter_profile.json"
        self.current_year = datetime.datetime.now().year
        self.today = datetime.date.today()

    def greet(self):
        print("\n" + "="*50)
        print("Namaste! I am VoterOne, your 360° Indian Election Concierge.")
        print("Let's get you ready for the democratic process.")
        print("="*50 + "\n")

    def get_user_profile(self):
        try:
            year_of_birth = int(input("To start, what is your year of birth? "))
            age = self.current_year - year_of_birth
            self.profile["year_of_birth"] = year_of_birth
            
            if age < 18:
                years_left = 18 - age
                print(f"\nYou're a future voter! You'll be eligible in {years_left} years.")
                print("For now, your mission is to ensure your parents vote. I've created 'PARENT_VOTING_GUIDE.md' for you.")
                self.create_parent_guide()
                self.save_profile()
                return False
            else:
                print("\nExcellent! You are eligible to vote.")
                self.profile["state"] = input("Please enter your State: ").strip()
                self.profile["pc"] = input("Enter your Parliamentary Constituency (PC): ").strip()
                self.profile["ac"] = input("Enter your Assembly Constituency (AC): ").strip()
                self.save_profile()
                self.update_election_hub()
                return True
        except ValueError:
            print("Please enter a valid year.")
            return self.get_user_profile()

    def save_profile(self):
        with open(self.profile_file, "w") as f:
            json.dump(self.profile, f, indent=4)
        print(f"\n[System] Profile saved to {self.profile_file}")

    def create_parent_guide(self):
        content = """# PARENT_VOTING_GUIDE.md
## Your Mission: Ensure Your Parents Vote!

As a future voter, you play a crucial role in our democracy. Use this checklist to help your parents:

- [ ] Check Voter ID status on electoralsearch.eci.gov.in
- [ ] Locate the Polling Booth
- [ ] Ensure they have a valid ID card
- [ ] Mark the calendar for the Poll Day
- [ ] Post-vote: Check for the ink mark!

*Democracy depends on every single vote.*
"""
        with open("PARENT_VOTING_GUIDE.md", "w") as f:
            f.write(content)
        print("[System] PARENT_VOTING_GUIDE.md created.")

    def update_election_hub(self):
        state = self.profile.get("state")
        hub_content = f"# ELECTION_HUB.md\n\n## Location: {state}, {self.profile.get('pc')}, {self.profile.get('ac')}\n\n"
        
        # Logic for 2026 Context
        found_data = False
        for phase, info in ELECTION_DATA_2026.items():
            if phase != "Telangana" and state in info["States"]:
                hub_content += f"### Real-Time 2026 Election Status: {state}\n"
                hub_content += f"- **Poll Date:** {info.get('Poll Date')}\n"
                hub_content += f"- **Counting Date:** {info.get('Counting Date', 'N/A')}\n"
                hub_content += f"- **Current Status:** {info['Status']}\n\n"
                found_data = True
                break
        
        if not found_data and state == "Telangana":
            info = ELECTION_DATA_2026["Telangana"]
            hub_content += "### Real-Time 2026 Election Status: Telangana\n"
            hub_content += f"- **State-wide Municipal Polls:** {info['Municipal Poll Date']} (Completed)\n"
            if "city" in self.profile.get("pc", "").lower() or "hyderabad" in self.profile.get("pc", "").lower():
                 hub_content += f"- **Focus:** {info['Next Focus']}\n\n"
            else:
                 hub_content += "- **Next Focus:** Stay tuned for local body updates.\n\n"
            found_data = True

        if not found_data:
            hub_content += "### General Election Info\n- Stay tuned for upcoming election dates in your region.\n\n"

        hub_content += "## Tools & Resources\n"
        hub_content += "- **Booth Finder:** Find your polling booth at [electoralsearch.eci.gov.in](https://electoralsearch.eci.gov.in)\n"
        hub_content += "  *Instructions:* Use your EPIC number from your Voter ID card to find the exact location.\n\n"
        
        hub_content += "## Civic Awareness\n"
        hub_content += "> **Civic Note:** NOTA (None of the Above) is a tactical tool for dissent. "
        hub_content += "It allows you to express that no candidate meets your expectations. "
        hub_content += "The ballot is the ultimate equalizer in society. Your voice matters.\n"

        with open("ELECTION_HUB.md", "w") as f:
            f.write(hub_content)
        print("[System] ELECTION_HUB.md updated based on your location.")

    def ask_ai(self, query):
        if not model:
            return "I am currently in local mode. Please set GEMINI_API_KEY in .env for full AI capabilities."
        
        prompt = f"As VoterOne, an Indian Election Concierge, answer this user query about elections: {query}. Keep it professional and helpful."
        response = model.generate_content(prompt)
        return response.text

def main():
    voter = VoterOne()
    voter.greet()
    is_eligible = voter.get_user_profile()
    
    if is_eligible:
        print("\n" + "-"*30)
        print("I'm here to help with any questions. (Type 'exit' to quit)")
        while True:
            query = input("\nYou: ")
            if query.lower() in ['exit', 'quit']:
                break
            print("\nVoterOne:", voter.ask_ai(query))

if __name__ == "__main__":
    main()
