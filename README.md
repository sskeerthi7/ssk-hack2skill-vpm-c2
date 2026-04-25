# VoterOne: Your 360° Indian Election Concierge

VoterOne is a smart, dynamic assistant designed to help users navigate the Indian election process. It provides personalized guidance based on eligibility, location-based election data for 2026, and civic awareness tools.

## Vertical
**Indian Election Concierge**

## Approach and Logic
- **Phase 1: Eligibility & Identity**: Validates user age. If under 18, it assumes a "Future Voter" persona and generates a guide for parents. If 18+, it collects location data (State, PC, AC).
- **Phase 2: Workspace Persistence**: Saves details in `voter_profile.json` and maintains a dynamic `ELECTION_HUB.md`.
- **Phase 3: Real-Time 2026 Data**: Uses a built-in database of 2026 election dates for states like Tamil Nadu, Maharashtra, Gujarat, West Bengal, Assam, Kerala, Puducherry, and Telangana.
- **Phase 4: Tools & Awareness**: Provides Booth Finder links and NOTA awareness notes.
- **Gemini Integration**: Uses Google's Gemini 1.5 Flash model to answer complex election-related queries interactively.

## How the Solution Works
1. Run `python app.py`.
2. Enter your year of birth.
3. Follow the prompts to enter your location or receive your future voter mission.
4. Interact with the AI to ask questions about the democratic process.

## Security
- API keys are handled via `.env` file (not committed to the repo).
- A `.gitignore` file is included to prevent accidental leakage of credentials or local data.

## Assumptions
- Age calculation is based on the current year (2026 context).
- States and dates provided are based on the challenge brief for the 2026 window.

## Deployment (Cloud Run)
1. **Push to GitHub**:
   - Create a public repo on GitHub.
   - `git add .`
   - `git commit -m "Initial commit"`
   - `git remote add origin <your-repo-url>`
   - `git push -u origin main`
2. **Deploy to Cloud Run**:
   - Install Google Cloud SDK.
   - Run: `gcloud run deploy voter-one --source . --set-env-vars GEMINI_API_KEY=YOUR_KEY --allow-unauthenticated`
   - The terminal will output a **Service URL**. That is your live link!

## Google Services Integration
- **Gemini API**: Powers interactive Q&A.
- **Cloud Run**: Hosts the application for a live URL.
