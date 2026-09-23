# HealthBot — Multilingual Health Assistant for Telegram

## Overview

HealthBot is a lightweight health information chatbot built for India and designed to answer basic public-health questions in a simple, accessible way. It runs on Telegram, understands short user messages, and responds with information on symptoms, prevention, vaccines, and outbreak-related updates.

The project addresses a common problem: many people search for health guidance in fragmented ways, and the information is often scattered across sources or not available in local languages. HealthBot provides a simple interface for asking questions like:

- dengue symptoms
- how to prevent malaria
- vaccines at 6 months
- outbreak in Coimbatore

It is designed to be fast, offline-friendly, low-cost, and easy to run locally or in a small deployment.

---

## Problem

People often need quick answers to basic health questions, but:

- health information is not always available in the language they use
- they may not know which symptoms or prevention steps matter most
- vaccine schedules and disease awareness can be confusing
- local outbreak information is often hard to access quickly

This project solves that by combining:

- Telegram messaging as a familiar frontend
- simple rule-based intent detection instead of heavy ML infrastructure
- structured knowledge files for symptoms and prevention
- vaccine schedule data for Indian children
- WHO RSS feed integration for disease alerts
- translation support for major Indian languages

---

## Solution

HealthBot acts as a conversational health assistant that:

1. receives Telegram messages through a webhook
2. detects the language and intent
3. extracts key entities like disease, age, district, or state
4. looks up relevant knowledge from local JSON files
5. returns a concise response in the user’s language when possible
6. optionally shares outbreak information from a WHO feed

This makes it useful for:

- public-health awareness
- community health outreach
- educational chatbots
- small-scale local deployments without large cloud costs

---

## What the project does

### Core features

- Telegram bot interface
- disease symptom answers
- prevention guidance
- vaccine schedule for India by child age in months
- outbreak-related status information based on WHO RSS feeds
- multilingual detection for English, Tamil, Hindi, and Bengali
- offline translation support using Argos Translate package installation
- lightweight rate limiting and health checks
- local JSON-based knowledge storage

### Example user inputs

- hi
- dengue symptoms
- how to prevent malaria
- vaccine schedule 6 months
- outbreak in Coimbatore
- any outbreak in Tamil Nadu

---

## Technology stack

### Backend

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic and Pydantic Settings
- Python-dotenv

### Messaging and webhook integration

- Telegram Bot API
- HTTPX for outbound API calls

### NLP / intent detection

- rule-based NLU using regex and keyword matching
- disease/entity extraction for symptoms, age, district, and state

### Knowledge and data sources

- local JSON files under backend/kb/
- WHO RSS feed for outbreak updates
- feedparser for RSS parsing

### Translation

- Argos Translate for local/offline translation support
- language detection heuristics for Tamil, Hindi, Bengali, and English

### Infra / optional services

- Redis for optional rate limiting
- Docker Compose for local orchestration
- Valkey for local Redis-compatible service in Docker

### Testing

- pytest
- FastAPI TestClient

---

## Architecture

The system is built as a simple three-layer application:

1. Entry layer: Telegram and REST API
2. Business logic layer: NLU, translation, and response generation
3. Data layer: local JSON knowledge, WHO RSS, and optional Redis

```text
┌──────────────────────────────────────────────────────────────┐
│                        Telegram Client                         │
│          User sends message: "dengue symptoms"              │
└───────────────────────┬──────────────────────────────────────┘
                        │ HTTPS webhook
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                   FastAPI Application Layer                  │
│   - /tg/webhook: receives Telegram updates                    │
│   - /kb/*: knowledge base endpoints                          │
│   - /live, /ready: health endpoints                          │
│   - Rate limiting middleware                                 │
│   - Logging middleware                                       │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                  Intelligence & Response Layer               │
│   - detect_lang(): language detection                        │
│   - translate(): local translation to/from English           │
│   - classify_intent(): regex-based intent matching           │
│   - extract_entities(): disease, age, district, state        │
│   - process_message(): creates the final reply               │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                     Data & External Services                  │
│   - faq_health.json: disease symptoms & prevention         │
│   - vaccine_schedule_india.json: India immunization data     │
│   - WHO RSS: outbreak feed                                   │
│   - Redis: optional rate-limit storage                       │
│   - Telegram Bot API: sendMessage response                  │
└──────────────────────────────────────────────────────────────┘
```

### Project components and responsibilities

#### 1. FastAPI app entry point

File: backend/app/main.py

- creates the FastAPI application
- configures middleware for logging and rate limiting
- registers routers for health, KB, and Telegram APIs
- primes the WHO cache during startup via the lifespan hook

#### 2. Health API

File: backend/app/api/health.py

- /live checks whether the service is running
- /ready verifies readiness of core dependencies like Redis and WHO RSS feed
- useful for deployment checks and monitoring

#### 3. Knowledge API

File: backend/app/api/kb.py

- exposes endpoints for:
  - disease symptoms
  - prevention advice
  - vaccine schedule
  - outbreak status
- returns structured answers from JSON knowledge sources

#### 4. Telegram webhook API

File: backend/app/api/telegram.py

- receives updates from Telegram through the webhook
- extracts message text and chat id
- passes text through the processing pipeline
- sends a reply back to Telegram using sendMessage
- supports webhook registration and lookup via Telegram APIs

#### 5. Intent and entity detection

File: backend/app/services/nlu.py

- matches intents such as greet, symptoms, prevention, vaccines, and outbreak checks
- extracts important entities like disease name, age in months, district, or state
- uses regex rules rather than a large ML model, making it lightweight and easy to run locally

#### 6. Knowledge base service

File: backend/app/services/kb.py

- loads JSON files from backend/kb/
- converts disease names into symptom and prevention answers
- resolves the closest vaccine schedule point based on the user’s age

#### 7. Outbreak service

File: backend/app/services/outbreaks.py

- fetches WHO Disease Outbreak News RSS data
- caches results for a configured TTL
- prepares a friendly public-health status response

#### 8. Translation layer

File: backend/app/services/translator.py

- detects Hindi/Tamil/Bengali/English patterns using heuristics
- translates short Indian-language text to English for interpretation
- translates the reply back to the user’s language when possible

#### 9. Config and settings

File: backend/app/config.py

- declares app settings from environment variables
- manages Telegram token, Redis URL, WHO RSS feed URL, and rate-limit values
- centralizes configuration for the project

#### 10. Middleware and safety

Files:
- backend/app/middleware/logging.py
- backend/app/middleware/rate_limit.py

- logs incoming requests and system events
- protects APIs with basic IP-based rate limiting
- prevents abuse while keeping the service simple and portable

---

## End-to-end request flow

### Flow 1: Telegram message arrives

1. A user sends a message to the Telegram bot.
2. Telegram posts the update to the configured webhook URL.
3. The request hits the FastAPI endpoint at /tg/webhook.

### Flow 2: Message processing

1. The message text is extracted from the Telegram payload.
2. detect_lang() checks whether the message is in English, Hindi, Tamil, or Bengali.
3. If the message is not in English, translate() sends it to English for analysis.
4. classify_intent() determines the user’s purpose.
5. extract_entities() pulls out disease, age, district, or state values.

### Flow 3: Response generation

1. The backend picks the relevant handler:
   - symptoms
   - prevention
   - vaccine schedule
   - outbreak status
   - greeting
   - fallback
2. The service reads from the local JSON knowledge base or WHO feed.
3. A response is generated as a plain-text message.
4. If needed, the answer is translated back into the user’s language.

### Flow 4: Bot reply

1. The reply is sent to Telegram using the sendMessage API endpoint.
2. The user sees the answer in the chat window.

---

## Data and knowledge architecture

### Local knowledge files

The bot uses static data files instead of a database:

- backend/kb/faq_health.json
  - stores disease names and related symptom/prevention content
- backend/kb/vaccine_schedule_india.json
  - stores vaccine information by age in months for Indian children

This keeps the project simple to deploy and easy to modify without a DB service.

### WHO outbreak data

The outbreak part is not hardcoded. It fetches the WHO Disease Outbreak News RSS feed, caches it, and then formats a simple response suitable for chat use.

This makes the bot useful for public-health awareness without a separate data pipeline.

### Why the design stays lightweight

This project intentionally avoids heavy infrastructure like:

- full ML/NLU servers
- cloud database dependencies
- external API charges for translation or messaging
- enterprise observability stacks

It is designed as a practical small-scale health assistant that is easy to run and easy to understand.

---

## Project structure

```text
healthbot-proto/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── health.py
│   │   │   ├── kb.py
│   │   │   └── telegram.py
│   │   ├── middleware/
│   │   │   ├── logging.py
│   │   │   └── rate_limit.py
│   │   ├── services/
│   │   │   ├── kb.py
│   │   │   ├── nlu.py
│   │   │   ├── outbreaks.py
│   │   │   └── translator.py
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── __init__.py
│   ├── kb/
│   │   ├── faq_health.json
│   │   └── vaccine_schedule_india.json
│   ├── tests/
│   │   ├── test_kb.py
│   │   ├── test_nlu.py
│   │   └── test_telegram.py
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .env
├── docker-compose.yml
├── README.md
├── run_healthbot.ps1
└── eval/
    ├── eval_set.csv
    └── evaluate.py
```

---

## Prerequisites

Before running the app locally, make sure you have:

- Python 3.11+
- pip
- a Telegram bot token from BotFather
- access to a terminal / PowerShell
- optionally Docker Desktop if using container-based setup

---

## Configuration

Create a file named `.env` in the `backend/` folder.

Example:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCDEF...your-token
REDIS_URL=
```

### Environment variables

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from BotFather |
| `REDIS_URL` | No | Use Redis if available; empty value falls back to in-memory behavior |
| `LOG_LEVEL` | No | Logging level, default is INFO |
| `ENV` | No | Runtime environment, default is development |

---

## Local setup

### 1) Open terminal in the backend folder

```powershell
cd "C:\Users\MOHAN\careconnect-ai\healthbot-proto\backend"
```

### 2) Create venv (Windows)

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```powershell
pip install -r requirements.txt
```

### 4) Create environment file

```powershell
"TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN" | Set-Content .env
"REDIS_URL=" | Add-Content .env
```

### 5) Start the API server

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You should see output similar to:

```text
INFO:     Started server process
INFO:     Application startup complete.
```

---

## Health checks

Once the app is running, you can confirm it is alive:

```powershell
Invoke-RestMethod http://localhost:8000/live
```

Example response:

```json
{"status":"alive","version":"1.0.0","services":{"redis":"unknown","who":"unknown"}}
```

---

## Public webhook setup

Telegram requires a public HTTPS URL for the webhook. Since your local app runs on `localhost`, you need a tunneling tool.

### Option 1: localtunnel (easy free option)

In a second terminal:

```powershell
npx --yes localtunnel --port 8000
```

Example output:

```text
your url is: https://tasty-guests-thank.loca.lt
```

Then register the webhook:

```powershell
Invoke-RestMethod "http://localhost:8000/tg/set_webhook?url=https://tasty-guests-thank.loca.lt/tg/webhook"
```

### Option 2: ngrok

```powershell
ngrok http 8000
```

Then set the webhook URL to the ngrok HTTPS URL.

---

## Telegram testing

Open Telegram and search for your bot username, for example:

- @mohan_health_ai_bot

Then send:

- hi
- dengue symptoms
- vaccine schedule 6 months
- outbreak in Coimbatore
- malaria prevention

The bot should respond from the FastAPI backend through the webhook flow.

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/live` | health/liveness check |
| GET | `/ready` | readiness check |
| GET | `/kb/symptoms` | disease symptom lookup |
| GET | `/kb/prevention` | prevention advice |
| GET | `/kb/vaccine/schedule` | vaccine schedule by age |
| GET | `/kb/outbreak/status` | outbreak status lookup |
| POST | `/tg/webhook` | Telegram webhook endpoint |
| GET | `/tg/set_webhook` | configure Telegram webhook |
| GET | `/tg/webhook_info` | inspect webhook state |
| POST | `/dev/webhook` | internal dev/test endpoint |

Example:

```powershell
Invoke-RestMethod "http://localhost:8000/kb/symptoms?disease=dengue"
```

---

## Docker setup

The project includes a Docker Compose file for a simple local deployment.

```powershell
cd "C:\Users\MOHAN\careconnect-ai\healthbot-proto"
docker-compose up --build
```

This starts:

- the backend FastAPI app
- a Redis/Valkey service

---

## Testing

Run the automated tests:

```powershell
cd "C:\Users\MOHAN\careconnect-ai\healthbot-proto\backend"
pytest -q
```

The codebase includes tests for:

- NLU intent classification
- entity extraction
- Telegram webhook behavior
- translation fallback behavior
- knowledge-base lookups

---

## Known limitations

This version is intentionally lightweight and designed for fast local use. Some limitations include:

- rule-based intent detection instead of a full ML pipeline
- disease and prevention content is based on static knowledge files
- translation is heuristic and best suited for short user queries
- outbreak updates depend on WHO RSS availability and freshness

---

## Future improvements

Possible next improvements:

- add more diseases and symptom entries
- improve intent detection with Rasa or another NLP engine
- add persistent storage and analytics
- add multi-language response quality evaluation
- support WhatsApp or SMS channels in addition to Telegram
- add a better admin dashboard for logs and health checks

---

## License

MIT

---

## Summary

HealthBot is a simple, affordable, and practical public-health chatbot for India. It combines messaging, rule-based AI, local knowledge files, and a lightweight web API to provide useful, accessible answers for common health questions. The project is designed to be easy to run locally, easy to extend, and low-cost to deploy.
#   T e l e g r a m _ h e a l t h _ a i _ b o t  
 