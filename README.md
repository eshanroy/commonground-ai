# CommonGround AI

**Different tastes. Common ground.**

*Your group. Your tastes. One plan.*

CommonGround AI is an AI-powered group-experience planning prototype that helps people with different interests discover activities and places that may appeal to everyone in their group.

Instead of recommending experiences based on one person's preferences, CommonGround combines group members' interests, dislikes, location, budget, and occasion to generate a diverse shortlist with transparent compatibility scores and explanations.

The project combines a local recommendation engine with **Qloo Taste AI API integration** for place discovery and an agentic workflow that plans discovery, evaluates results, and broadens the search when necessary.

## Live Demo

- **Live application:** https://commonground-ai.vercel.app/
- **Backend API:** https://commonground-ai-api.onrender.com
- **API documentation:** https://commonground-ai-api.onrender.com/docs
- **Health check:** https://commonground-ai-api.onrender.com/health
- **GitHub repository:** https://github.com/eshanroy/commonground-ai

## Key Features

- **Group-based planning:** Supports groups of 2–8 members.
- **Interest and dislike modeling:** Considers individual preferences and things members would rather avoid.
- **Context-aware recommendations:** Uses location, budget, and occasion to shape suggestions.
- **Transparent compatibility scoring:** Calculates heuristic compatibility scores locally and explains preference alignment.
- **Trade-off explanations:** Highlights mismatches and areas where members may need to compromise.
- **Recommendation diversity:** Produces a shortlist of activity concepts across different categories.
- **Qloo-powered place discovery:** Uses Qloo's API to retrieve candidate places associated with resolved interests and location-related context.
- **Agentic discovery planning:** Prioritizes shared interests when available and otherwise combines the group's interests.
- **Result evaluation and adaptive search:** Evaluates discovery results and can broaden the search when the initial available results are insufficient.
- **Graceful fallback:** Preserves local activity recommendations when Qloo discovery is unavailable.
- **REST API:** Exposes functionality through FastAPI.
- **Automated tests:** Tests recommendation behavior, planning, evaluation, retry decisions, input validation, determinism, and fallback behavior.

## What Makes CommonGround AI Different?

Many recommendation systems focus primarily on an individual's preferences. CommonGround AI focuses on a different problem: finding an experience for a group whose members may have different tastes.

The project combines five main ideas:

1. **Preference aggregation** — gathers interests and dislikes from multiple group members.
2. **Compatibility scoring** — estimates how well activity concepts align with the group's stated preferences and budget.
3. **Explainability** — provides reasons, individual matches, and trade-offs behind recommendations.
4. **Category diversity** — encourages exploration beyond a single activity type.
5. **Cultural place discovery** — uses Qloo to retrieve candidate places associated with relevant interests.

The agentic component adds a planning-and-evaluation loop to place discovery. It selects an initial search strategy, evaluates the returned candidates, and broadens the search when results are insufficient and further discovery is possible.

This workflow makes the application more than a static list of recommendations: it uses the outcome of one discovery attempt to inform its next action.

## How the Agent Works

The CommonGround Group Planning Agent follows a structured workflow:

1. **Understand the group:** Collect the group's interests, dislikes, location, budget, and occasion.
2. **Create a discovery plan:** Identify interests shared by every member. If shared interests exist, prioritize them; otherwise, use the combined group interests.
3. **Execute discovery:** Send the planned interests through the Qloo-powered place-discovery flow.
4. **Evaluate results:** Assess discovery status and the number of candidates returned.
5. **Adapt when needed:** If discovery is available but produces fewer than the minimum candidate target, broaden the search to the combined group interests when that differs from the initial search.
6. **Return results:** Provide discovery results and execution metadata while preserving local activity recommendations if Qloo is unavailable.

The API response exposes the agent's plan, attempts, evaluation, and status so that its behavior can be inspected.

The current evaluation uses discovery status and candidate count as a simple sufficiency check. It does not establish venue quality, real-time availability, group satisfaction, or an official Qloo compatibility score.

## Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, FastAPI |
| Data validation | Pydantic |
| Cultural intelligence and place discovery | Qloo Taste AI API |
| HTTP requests | HTTPX |
| Configuration | Environment variables, python-dotenv |
| Testing | pytest |
| Frontend hosting | Vercel |
| Backend hosting | Render |

## Architecture

```text
Group Members
      |
      v
React + Vite Frontend
      |
      v
FastAPI Recommendations API
      |
      +----------------------------+
      |                            |
      v                            v
Local Recommendation         CommonGround Group
Scoring Engine               Planning Agent
      |                            |
      |                            v
      |                     Discovery Planning
      |                            |
      |                            v
      |                     Qloo Place Discovery
      |                            |
      |                            v
      |                     Evaluate Results
      |                            |
      |                     +------+------+
      |                     |             |
      |                     v             v
      |                  Sufficient    Broaden Search
      |                     |             |
      |                     +------+------+
      |                            |
      +-------------+--------------+
                    |
                    v
          Recommendations Response
                    |
                    v
        Explanations, Places, and
           Agent Execution Metadata
                    |
                    v
              Frontend UI
```

The local recommendation engine and Qloo discovery have separate responsibilities:

- The local engine calculates activity compatibility scores and explanations.
- Qloo supplies candidate place data through its API.
- The agent coordinates discovery planning, evaluation, and conditional broadening.
- The fallback path keeps local activity recommendations available when Qloo discovery fails.

## Project Structure

The main components are organized as follows:

```text
CommonGround-AI/
├── backend/
│   ├── main.py
│   ├── agent.py
│   ├── models.py
│   ├── recommendations.py
│   ├── qloo_client.py
│   ├── qloo_recommendations.py
│   ├── requirements.txt
│   ├── .env.example
│   └── tests/
│       ├── test_agent.py
│       ├── test_recommendations.py
│       └── ...
├── frontend/
│   ├── src/
│   │   └── App.jsx
│   ├── package.json
│   └── ...
├── .gitignore
├── LICENSE
└── README.md
```

*The structure above highlights the main components; individual files may vary as the project evolves.*

## Requirements

- Python 3.11 or newer, compatible with the installed dependencies
- Node.js and npm
- A Qloo API key for Qloo-powered place discovery
- Git, if you want to clone the repository

## Run Locally on Windows

### 1. Clone the repository

Open Command Prompt and run:

```cmd
git clone https://github.com/eshanroy/commonground-ai.git
cd CommonGround-AI
```

### 2. Configure and start the backend

From the project root:

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Create the local environment file from the example:

```cmd
copy .env.example .env
```

Open `backend/.env` and configure the Qloo API key using the variable name specified in `backend/.env.example`. Keep the configured Qloo API URL from the example unless your environment requires a different supported endpoint.

Start the backend:

```cmd
python -m uvicorn main:app --reload
```

The backend should be available at:

- API root: http://localhost:8000
- Interactive API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 3. Configure and start the frontend

Open a second Command Prompt window and navigate to the project root:

```cmd
cd frontend
npm install
```

Create or edit `frontend/.env` and set the backend URL:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Start the frontend:

```cmd
npm run dev
```

Open the local URL printed by Vite, usually:

http://localhost:5173

If that port is already in use, Vite may select another available port.

### Security

- Never commit `.env` files containing credentials.
- Never hardcode a real Qloo API key into frontend code.
- Keep API keys and other secrets on the backend.
- The repository's `.gitignore` excludes environment files and local development artifacts.

## Run Tests

From the project root:

```cmd
cd backend
.venv\Scripts\activate
python -m pytest tests -v
```

The test suite covers core recommendation behavior, scoring, preference explanations, input validation, deterministic results, agent planning and evaluation, adaptive discovery decisions, and graceful Qloo failure handling.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API welcome response |
| GET | `/health` | Health check |
| POST | `/recommendations` | Generate activity recommendations, perform Qloo discovery, and return agent execution metadata |

### Recommendations endpoint

Send a `POST` request to `/recommendations` with a JSON body containing the group's location, budget, occasion, and members.

Example request:

```json
{
  "location": "Bengaluru",
  "budget": "moderate",
  "occasion": "weekend",
  "members": [
    {
      "name": "Alex",
      "interests": ["food", "culture"],
      "dislikes": ["nightlife"]
    },
    {
      "name": "Sam",
      "interests": ["food", "music"],
      "dislikes": ["hiking"]
    }
  ]
}
```

The API returns local activity recommendations, Qloo discovery results, and agent metadata, including the selected discovery strategy, attempts, and evaluation.

Use the interactive documentation at `/docs` to inspect the current request schema and test the endpoint.

## Recommendation Scoring and Transparency

CommonGround's activity compatibility scores are calculated by the local scoring engine. Explanations describe individual preference matches, shared interests, complementary interests, budget alignment, and potential trade-offs.

These scores are heuristic estimates. They are not scientifically validated probabilities that a group will enjoy an activity.

Place discovery uses Qloo candidate data and available metadata. The interest-relevance estimate displayed for a candidate is calculated locally from metadata such as names and tags. It is **not an official Qloo compatibility score**.

The project also does not claim that candidate places have verified current operating status, prices, opening hours, reservation availability, or suitability for every member of a group.

## Limitations

- Compatibility scores have not been validated against real group satisfaction outcomes.
- Agent evaluation currently relies on discovery status and candidate count rather than a learned quality or satisfaction model.
- Search broadening is limited to the available discovery strategies and retry budget.
- Qloo results depend on API configuration, upstream responses, and available data.
- Place candidates are not guaranteed to have verified real-time availability or suitability.
- The project is a hackathon prototype and has not been validated as a production-grade recommendation service.

## Future Improvements

Potential next steps include:

- Stronger group-fairness metrics to avoid consistently compromising for the same members.
- More nuanced explanations of conflicting interests and preferences.
- Improved venue verification and up-to-date availability checks.
- User feedback to evaluate recommendation quality and group satisfaction.
- More advanced agent strategies and evaluation criteria.
- Additional monitoring, observability, and production-readiness improvements.

## Project Status

CommonGround AI combines a React frontend, FastAPI backend, local group-compatibility scoring, Qloo-powered place discovery, an agentic planning-and-evaluation workflow, and automated tests.

The application is deployed, and its source code is publicly available.

## License

This project is licensed under the **MIT License**. See the [`LICENSE`](LICENSE) file for details.
