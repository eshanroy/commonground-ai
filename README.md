# CommonGround AI

**Different tastes. Common ground.**

CommonGround AI is an AI-powered group-experience planning prototype designed to help people with different interests discover activities and places that may appeal to everyone in a group.

Instead of recommending experiences based on one person's preferences, CommonGround combines group members' interests, dislikes, location, budget, and occasion to produce a diverse shortlist with transparent compatibility scores and explanations.

## Key Features

- **Group-based planning:** Supports 2–8 group members.
- **Interest and dislike modeling:** Considers individual preferences and negative preferences.
- **Context-aware planning:** Accepts location, budget, and occasion.
- **Transparent compatibility scoring:** Calculates heuristic scores locally and explains preference alignment.
- **Trade-off explanations:** Helps users understand why an activity may suit the group and where preferences may differ.
- **Diverse recommendations:** Produces a shortlist designed to avoid excessive repetition of the same activity category.
- **Qloo-powered place discovery:** Integrates Qloo's API to discover candidate places using resolved interest tags and location-related context.
- **Graceful fallback:** Keeps local activity recommendations available when Qloo discovery encounters handled or unexpected errors.
- **REST API:** Exposes recommendation functionality through FastAPI.
- **Automated tests:** Tests recommendation behavior, scoring, input validation, determinism, and Qloo failure handling.

## What Makes CommonGround AI Different?

Traditional recommendation systems often focus on an individual's preferences. CommonGround AI focuses on the challenge of finding a shared experience for a group whose members may have different tastes.

The prototype combines:

1. **Preference aggregation** — collects interests and dislikes from multiple people.
2. **Compatibility scoring** — estimates how well each activity aligns with the group's preferences.
3. **Explainability** — provides reasons and trade-offs behind recommendations.
4. **Category diversity** — encourages exploration beyond a single activity type.
5. **Cultural place discovery** — uses Qloo to retrieve candidate places associated with relevant interests.

The local compatibility score is a heuristic, not a scientifically validated probability that everyone will enjoy an experience. Qloo place discovery supplies candidate places; it does not, by itself, verify real-time availability or guarantee that every candidate is suitable for the entire group.

## Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, FastAPI, Pydantic |
| Cultural intelligence and place discovery | Qloo API |
| HTTP requests | HTTPX |
| Configuration | Environment variables, python-dotenv |
| Testing | pytest |

## Architecture

```text
Group Members
     |
     v
React + Vite Frontend
     |
     v
FastAPI Backend
     |
     +--------------------------+
     |                          |
     v                          v
Local Compatibility        Qloo Place
Scoring Engine             Discovery
     |                          |
     +------------+-------------+
                  |
                  v
       Recommendations API
                  |
                  v
       Explanations and Results
                  |
                  v
          Frontend UI
```

The local scoring engine and Qloo place discovery have separate responsibilities. Compatibility scores are calculated locally; Qloo provides candidate place data. A Qloo API failure should not prevent the local activity recommendations from being returned when the fallback path is available.

## Requirements

- Python 3.11 or newer, compatible with the installed dependencies
- Node.js and npm
- A Qloo API key for Qloo-powered place discovery
- Git, if you want to clone or version-control the project

## Run Locally on Windows

### 1. Clone or open the project

If you have cloned the repository, open Command Prompt in the project directory.

### 2. Configure the backend

From the project root:

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Create your local environment file from the example:

```cmd
copy .env.example .env
```

Open `backend/.env` and configure the Qloo API key using the variable name specified in `backend/.env.example`.

**Security:** Never commit your real `.env` file or expose your API key in source code, screenshots, logs, or public repositories.

Start the backend:

```cmd
python -m uvicorn main:app --reload
```

The API should be available at:

- API: http://localhost:8000
- Interactive API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 3. Configure and start the frontend

Open a second Command Prompt in the project root:

```cmd
cd frontend
npm install
```

Create the local frontend environment file:

```cmd
copy .env.example .env
```

The frontend API URL can be configured through `VITE_API_BASE_URL`. For local development, use:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Start the development server:

```cmd
npm run dev
```

Open the URL printed by Vite. The default is usually http://localhost:5173.

If that port is already in use, Vite may select another available port.

## Run Tests

From the project root:

```cmd
cd backend
python -m pytest -v
```

The test suite covers core recommendation behavior, score consistency, preference explanations, input validation, result determinism, category diversity, and graceful handling of unexpected Qloo discovery errors.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API welcome response |
| GET | `/health` | Health check |
| POST | `/recommendations` | Generate group recommendations and return Qloo discovery results |

The interactive API documentation at `/docs` can be used to inspect the request schema and test the endpoint.

## Limitations

- Compatibility scores are heuristic estimates and have not been validated against real group satisfaction outcomes.
- Qloo place discovery returns candidate places; it does not guarantee real-time opening hours, reservations, availability, or suitability.
- Candidate-interest match estimates are calculated locally from available metadata. They should not be interpreted as official Qloo compatibility scores.
- Place discovery depends on API configuration, upstream responses, and available data.
- The project is a hackathon prototype, not a production-validated recommendation service.

## Project Status

CommonGround AI currently combines a working local group-recommendation engine with Qloo-powered place discovery, a React frontend, a FastAPI backend, and automated tests.

Future improvements could include stronger group-fairness evaluation, more detailed explanations of conflicting preferences, richer venue verification, and user feedback to evaluate recommendation quality.

## License

No license has been specified yet. Check the repository's license before reusing or distributing the project.
