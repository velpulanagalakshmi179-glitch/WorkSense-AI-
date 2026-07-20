# WorkSense AI

An Enterprise SaaS-style workplace intelligence assistant.

## Overview
WorkSense AI takes unstructured inputs (meeting transcripts, long documents, and task lists) and processes them using the Groq API to generate actionable intelligence. It provides:
- Meeting Intelligence (Action items, decisions, summaries, risks)
- Document Intelligence (Summaries, Q&A)
- AI Workplace Assistant (Context-aware chat)
- Analytics & Reports

## Architecture
- **Frontend**: Flask + Bootstrap 5 + AJAX (Fetch API) for real-time interactions
- **Backend**: Flask + SQLite
- **AI Integration**: Groq API (Llama 3 / Mixtral models via `groq_client.py`)
- **Data Persistence**: SQLite (`worksense.db`)
- **Visualizations**: Plotly.js natively integrated via JSON payloads

## Setup
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file from `.env.example` and add your `GROQ_API_KEY`
4. Run the application locally: `python flask_run.py`

## Deployment
This app is ready to deploy on standard PAAS platforms like Heroku or Render.
Use the included `Procfile` or `render.yaml` to deploy.
- **Render**: Connect the repo to Render and it will auto-deploy using `render.yaml`.
- **Gunicorn**: The WSGI entry point is `flask_app:create_app()`.

## License
MIT License
