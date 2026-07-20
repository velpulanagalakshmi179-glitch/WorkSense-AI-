# WorkSense AI — Architecture

## Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Presentation Layer (Streamlit)                              │
│  app.py + pages/*.py                                         │
│  - Renders UI, handles user input, calls business logic      │
│  - No Groq calls or SQL happen directly in page files         │
└───────────────────────────┬────────────────────────────────┘
                             │
┌───────────────────────────▼────────────────────────────────┐
│  Business Logic Layer (utils/)                               │
│  ┌───────────────┐ ┌───────────────────┐ ┌─────────────────┐ │
│  │ groq_client.py│ │ document_processor │ │ export_utils.py │ │
│  │ generate()    │ │ .py                │ │ export_to_pdf() │ │
│  │ generate_json()│ │ extract_text()    │ │ export_to_txt() │ │
│  └───────┬───────┘ │ chunk_text()       │ └─────────────────┘ │
│          │         └────────────────────┘                    │
│  ┌───────▼─────────────────────────────────────────────────┐ │
│  │ db.py — all SQLite reads/writes go through here          │ │
│  └───────┬─────────────────────────────────────────────────┘ │
└──────────┼───────────────────────────────────────────────────┘
           │
┌──────────▼───────────────┐   ┌───────────────────────────────┐
│  External: Groq API       │   │  Local: SQLite (worksense.db)  │
│  llama-3.3-70b-versatile  │   │  tasks / meetings / documents / │
│  (chat completions,       │   │  risk_flags / productivity_    │
│   JSON mode)               │   │  snapshots                     │
└───────────────────────────┘   └───────────────────────────────┘
```

Prompt templates (`prompts/`) sit alongside `utils/` but are pure string
builders — no side effects, easy to unit test independently of the API.

## Module responsibility map

| Module (page)             | Reads from DB              | Writes to DB              | Calls Groq |
|----------------------------|-----------------------------|-----------------------------|-----------|
| Home (`app.py`)            | stats summary                | —                            | no |
| Meeting Intelligence        | —                             | `meetings`, `tasks`         | yes (JSON) |
| Document Intelligence       | —                             | `documents`                 | yes (JSON + text) |
| AI Assistant                | `meetings`, `documents`      | —                            | yes (text) |
| Email Automation            | —                             | —                            | yes (text) |
| Productivity Analytics      | `tasks`                      | `productivity_snapshots`    | yes (JSON) |
| AI Risk Center              | `tasks`                      | `risk_flags`                | yes (JSON) |
| Smart Task Manager          | `tasks`                      | `tasks`                      | yes (text, priority only) |
| Manager Insights            | `tasks`, `risk_flags`        | —                            | yes (text) |
| Weekly Reports              | `tasks`, `productivity_snapshots` | —                       | yes (text) |
| About                       | —                             | —                            | no |

## Data flow — example: Meeting Intelligence

1. User pastes a transcript in `pages/1_Meeting_Intelligence.py`.
2. Page calls `prompts.meeting_prompts.summary_prompt()` to build the prompt string.
3. Page calls `utils.groq_client.generate_json()`, which hits the Groq chat
   completions endpoint with JSON mode and parses the response.
4. Result renders in the UI; if the user clicks "Add to Tasks," the page
   calls `utils.db.add_task()` for that action item.
5. The full meeting (transcript + summary) is saved via `utils.db.save_meeting()`
   so the AI Assistant page can pull it into its context later.
6. User can export the rendered result via `utils.export_utils.export_to_pdf()`
   or `export_to_txt()`.

Every other module follows the same shape: **UI → prompt builder → groq_client
→ (optional) db.py → UI render → (optional) export_utils**.

## Database schema (SQLite, `worksense.db`)

- `tasks(id, title, owner, priority, status, deadline, source, created_at)`
- `meetings(id, title, raw_text, summary, decisions, created_at)`
- `documents(id, filename, doc_type, extracted_text, summary, created_at)`
- `risk_flags(id, risk_type, description, severity, related_task_id, created_at)`
- `productivity_snapshots(id, week_label, productivity_score, team_efficiency, completed_tasks, pending_tasks, created_at)`

Created automatically by `utils.db.init_db()`, called once at the top of `app.py`.

## Why this shape

- **One Groq entry point (`groq_client.py`).** Swapping providers, models, or
  adding retry/rate-limit logic happens in one file, not nine.
- **DB layer isolated from UI.** Every page imports functions from `db.py`
  instead of writing SQL inline — makes it easy to swap SQLite for Postgres
  later without touching page files.
- **Prompts separated from logic.** Tuning a prompt doesn't require reading
  or risking breaking Streamlit rendering code.

## What this architecture does *not* solve

- No auth/session isolation — this is a single-user local demo, not a
  multi-tenant backend. SQLite has one shared file for whoever runs the app.
- No background jobs/queue — every Groq call is synchronous and blocks the
  Streamlit rerun until it returns.
- No caching layer — repeated identical questions re-hit the Groq API rather
  than reusing a prior answer.
