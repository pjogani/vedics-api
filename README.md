# Vedics App – Vedic Astrology Companion & API

Welcome to **Vedics**, your personal Vedic astrology companion! This repository contains the **backend** services that power the Vedics App, built with **Django 5**, **Django REST Framework**, **Celery**, and a modular architecture for extensibility. Below you’ll find an overview of its main features, technical design, and instructions for local development and deployment.

---

## Table of Contents

1. [Overview](#overview)  
2. [Key Features](#key-features)  
   - [Today’s Readings](#1-todays-readings)  
   - [Comprehensive Life Predictions](#2-comprehensive-life-predictions)  
   - [AI Chat Assistant](#3-ai-chat-assistant)  
3. [Project Structure](#project-structure)  
4. [Technical Architecture](#technical-architecture)  
   - [Core Apps](#core-apps)  
   - [New Apps](#new-apps)  
5. [Installation & Local Development](#installation--local-development)  
   - [Prerequisites](#prerequisites)  
   - [Environment Variables](#environment-variables)  
   - [Run Locally](#run-locally)  
   - [Database Migrations & Superuser](#database-migrations--superuser)  
   - [Celery Worker](#celery-worker)  
6. [Usage & API Endpoints](#usage--api-endpoints)  
7. [Internationalization (i18n)](#internationalization-i18n)  
8. [Testing & Linting](#testing--linting)  
9. [Contributing](#contributing)  
10. [License](#license)  
11. [Contact & Support](#contact--support)  

---

## Overview

**Vedics** is designed to provide personalized astrology insights and predictions. By combining ancient Vedic wisdom with modern Large Language Model (LLM) capabilities, users can:

- Register with accurate birth details (date, time, place).
- Receive daily and long-term astrological predictions.
- Consult with an AI-powered assistant for personalized guidance.
- Manage subscriptions or multiple family members (organizations).
- Enjoy multi-language responses and chat with the assistant in a preferred language.

The backend in this repository handles all data storage, user authentication, chat sessions, daily predictions, and advanced i18n support for global usage.

---

## Key Features

### 1. Today’s Readings
- **Daily** personalized insights (e.g., fortune level, favorable times, recommended activities).
- Automatically updated each day, potentially via **Celery** scheduled tasks.
- Quick glimpses on the user’s dashboard, with notifications/alerts if desired.

### 2. Comprehensive Life Predictions
A suite of in-depth predictions covering multiple life domains, including:

- **Core Personality & Life Path**  
  Natural strengths, weaknesses, past life influences, and social patterns.

- **Career & Wealth**  
  Career success, business vs. job suitability, foreign opportunities, wealth accumulation phases.

- **Relationships & Marriage**  
  Relationship traits, marriage timing, partner compatibility, and potential challenges.

- **Health & Wellbeing**  
  Health sensitivity areas, long-term outlook, recommended lifestyle changes, and remedies.

- **Challenges & Remedies**  
  Identification of key challenges along with spiritual practices, mantras, or gemstone recommendations.

- **Major Life Periods**  
  Early life (0–30 years), mid-life (31–60 years), and later years (60+). Key transitions and life events.

### 3. AI Chat Assistant
- Chat-based interface to ask follow-up questions about astrology, predictions, or spiritual practices.
- **LLM integration** (e.g., OpenAI), returning responses in the user’s **preferred language**.
- Conversations are stored (Conversation, Message models), preserving an ongoing user history.

---

## Project Structure

Below is a high-level overview of the repository’s structure (folders omitted for brevity):

```
vedics-api/
├── assistant/        # AI chat, conversation models/views
├── core/             # Shared logic, config, base permissions, organizations, users, etc.
├── profiles/         # User birth info, preferences, dynamic questions
├── predictions/      # Manages daily & major reading generation, Celery tasks
├── subscriptions/    # (Optional) Subscription tiers, linking organizations to plans
├── utils/            # Utility code (history, etc.)
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
└── README.md
```

### Key Folders

- **core/**  
  Contains foundational apps and modules:  
  - `core.users`: Custom user model (UUID primary key), user CRUD, token auth  
  - `core.organizations`: Multi-tenant/family logic (Organization, Team, Membership)  
  - `core.config`: Django Configurations (for local vs. production settings)  
  - `core.mixins`, `core.permissions`, `core.exceptions`  
  - `core.conduit`: Generic external API call logic & request logging

- **assistant/**  
  Chat feature for user–assistant conversations, message logs, and LLM integration.

- **profiles/**  
  Detailed user Vedic info (birth chart data, personalization Q&A).

- **predictions/**  
  Celery tasks and endpoints to generate daily or comprehensive life predictions.

- **subscriptions/** (optional)  
  Subscription plan definitions, a subscription linking an organization to a plan, etc.

- **utils/**  
  Various utilities like historical tracking (with `django-simple-history`) or custom logic used across apps.

---

## Technical Architecture

### Core Apps

1. **core.users**  
   - A custom **User** model with UUID as `id`.  
   - Automatic token creation upon user registration.  

2. **core.organizations**  
   - Models: `Organization`, `Team`, `TeamMembership` for grouping users into “families” or “teams.”  
   - Owners or superusers can manage org details, roles, seats, etc.  

3. **core.conduit**  
   - Generic endpoints and code to handle external service calls (e.g., logging, tokens).  
   - Potentially reusable if you integrate other external APIs beyond the LLM.  

### New Apps

1. **profiles**  
   - **UserProfile** storing date/time/place of birth, lat/long, phone, and `preferred_language`.  
   - Optional `ProfileQuestion` & `ProfileAnswer` for dynamic onboarding or preference capturing.

2. **predictions**  
   - **Prediction** model storing daily or major readings.  
   - **Services** to generate birth charts and interpret them (Skyfield for astronomy, LLM for interpretation).  
   - **Celery tasks** that create or update predictions daily.

3. **assistant**  
   - **Conversation** and **Message** models for storing AI chat logs.  
   - A `ConversationManager` class manages user messages, builds system prompts, and calls the LLM.  

4. **subscriptions** (optional)  
   - If subscription tiers matter: `SubscriptionPlan`, `Subscription` (organization → plan).  
   - Signals can auto-assign “free” plans to newly created organizations.

---

## Installation & Local Development

### Prerequisites

- **Docker** and **Docker Compose**  
- (Optional) A **virtual environment** if running outside Docker.  
- An **OpenAI API key** (or similar) if using actual LLM calls (set `OPENAI_API_KEY` env variable).

### Environment Variables

Common environment variables:  
- `DJANGO_SECRET_KEY` – The Django secret key.  
- `DJANGO_DEBUG` – Whether to run in debug mode (`True` / `False`).  
- `DATABASE_URL` – Hostname for the DB (default: `postgres`).  
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` – Credentials for PostgreSQL.  
- `CELERY_BROKER_URL` – Points to `redis://redis:6379/0` by default.  
- `OPENAI_API_KEY` – Your LLM API key if needed.  

### Run Locally

1. **Clone the repo**:
   ```bash
   git clone https://github.com/<your-username>/vedics-api.git
   cd vedics-api
   ```

2. **Build & start containers**:
   ```bash
   docker-compose up --build
   ```
   This starts:
   - **web**: Django dev server on `0.0.0.0:8000`
   - **postgres**: PostgreSQL on `localhost:5432`
   - **redis**: Redis cache/broker
   - **worker**: Celery worker
   - **docs**: MkDocs for local docs (on `0.0.0.0:8001`)

### Database Migrations & Superuser

- **Apply migrations**:
  ```bash
  docker-compose run --rm web python manage.py migrate
  ```
- **Create a superuser**:
  ```bash
  docker-compose run --rm web python manage.py createsuperuser
  ```
- Then visit [http://localhost:8000/admin/](http://localhost:8000/admin/) to log in to the Django Admin.

### Celery Worker

The `worker` service automatically starts a Celery worker for background tasks. If you need to run it manually:
```bash
docker-compose run --rm worker python -m celery -A core worker -l info
```

---

## Usage & API Endpoints

- **User Registration**: `POST /api/v1/users/`
- **Profile**: `GET /api/v1/profiles/`, `POST /api/v1/profiles/`
- **Assistant (Chat)**: `POST /api/v1/assistant/chat/`
- **Predictions**:  
  - Daily readings might be available at `GET /api/v1/predictions/daily/`
  - Comprehensive predictions are typically fetched or created via Celery tasks.
- **Organizations**: `GET /api/v1/organizations/`, `POST /api/v1/organizations/` (if multi-user/family context is used).

For detailed documentation, see the [docs folder](./docs) or run the `docs` service:
```bash
docker-compose up docs
# Then visit http://localhost:8001
```
Or view DRF’s Swagger/OpenAPI:
```
GET /api/schema/swagger-ui/
```

---

## Internationalization (i18n)

- Users can set `preferred_language` in their profile.
- The **assistant** (LLM) or daily predictions can respond in that language if properly configured.
- You may also configure Django’s standard `LocaleMiddleware` for further text translations.

---

## Testing & Linting

**Run tests**:
```bash
docker-compose run --rm web pytest
```
**Lint and format** with [black](https://github.com/psf/black) and [isort](https://github.com/PyCQA/isort):
```bash
docker-compose run --rm web black .
docker-compose run --rm web isort .
```

---

## Contributing

1. **Fork** the repository and create a new branch.
2. **Commit** your changes with clear descriptions.
3. **Open a Pull Request** to the main branch.
4. Ensure your PR passes all tests and lint checks.

Contributions are welcome, whether bug fixes, new features, or documentation improvements. Feel free to open issues for suggestions or problems encountered.

---

## License

Vedics AI Inc. 2025

---

## Contact & Support

- **Email**: [support@vedics.ai](mailto:support@vedics.ai)
- **In-app Chat**: For quick queries regarding usage
- **Documentation**: [API docs](./docs) for more endpoints and usage examples
- **GitHub Issues**: Open an issue for bugs, feature requests, or general discussion

Thank you for exploring Vedics! May your astrological journey be insightful and enriching.  
_**Sarve Bhavantu Sukhinah (May all be happy).**_