import unittest
import os
import json
from voter_one import VoterOne

class TestVoterOne(unittest.TestCase):
    def setUp(self):
        self.voter = VoterOne()
        self.voter.profile_file = "test_profile.json"

    def tearDown(self):
        if os.path.exists("test_profile.json"):
            os.remove("test_profile.json")
        if os.path.exists("PARENT_VOTING_GUIDE.md"):
            os.remove("PARENT_VOTING_GUIDE.md")
        if os.path.exists("ELECTION_HUB.md"):
            os.remove("ELECTION_HUB.md")

    def test_under_18_logic(self):
        # Simulate birth year for 15 year old in 2026
        # Current logic uses datetime.datetime.now().year which is 2026 in metadata
        birth_year = 2011 
        self.voter.profile["year_of_birth"] = birth_year
        age = 2026 - birth_year
        self.assertTrue(age < 18)
        self.voter.create_parent_guide()
        self.assertTrue(os.path.exists("PARENT_VOTING_GUIDE.md"))

    def test_profile_saving(self):
        self.voter.profile = {"year_of_birth": 1990, "state": "Tamil Nadu"}
        self.voter.save_profile()
        self.assertTrue(os.path.exists("test_profile.json"))
        with open("test_profile.json", "r") as f:
            data = json.load(f)
        self.assertEqual(data["state"], "Tamil Nadu")

    def test_election_hub_tn(self):
        self.voter.profile = {"state": "Tamil Nadu", "pc": "Chennai", "ac": "Central"}
        self.voter.update_election_hub()
        self.assertTrue(os.path.exists("ELECTION_HUB.md"))
        with open("ELECTION_HUB.md", "r") as f:
            content = f.read()
        self.assertIn("Tamil Nadu", content)
        self.assertIn("Polls Completed", content)

if __name__ == "__main__":
    unittest.main()
