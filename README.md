# WorkSense AI 🧠

> **"AI-Powered Enterprise Productivity & Meeting Intelligence Platform"**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=flat&logo=streamlit)
![Groq AI](https://img.shields.io/badge/AI-Groq%20LLaMA-orange?style=flat)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat&logo=sqlite)
![Plotly](https://img.shields.io/badge/Data%20Viz-Plotly-purple?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Hackathon](https://img.shields.io/badge/Hackathon-Project-yellow?style=flat)

---

## Overview

WorkSense AI is an Enterprise SaaS platform that helps organizations transform meetings, documents, reports, and workplace communication into actionable business insights using AI. 

The platform combines multiple AI-powered workplace tools into one intelligent dashboard, serving as a centralized hub to supercharge your team's operational efficiency.

---

## Problem Statement

Organizations face numerous challenges when tracking operational workflows and communications:
- Manual meeting notes taking hours to compile.
- Missed deadlines due to untracked action items.
- Poor task tracking and decentralized assignments.
- Unstructured documents trapping valuable insights.
- Inefficient follow-up emails eating into productive time.
- Lack of executive insights and fragmented visibility.
- Overall low productivity across cross-functional teams.

---

## Our Solution

WorkSense AI solves these problems by injecting ultra-fast AI inference (powered by Groq) directly into your daily operational pipelines. 

By combining the following intelligent modules, WorkSense AI acts as your ultimate operational co-pilot:
- ✔ **AI Meeting Intelligence**
- ✔ **AI Workplace Assistant**
- ✔ **Document Intelligence**
- ✔ **Executive Dashboard**
- ✔ **Executive Brief Generator**
- ✔ **Business Impact Analysis**
- ✔ **Productivity Analytics**
- ✔ **Email Automation**
- ✔ **Meeting History**
- ✔ **Reports Dashboard**

---

## Features

### Authentication
- Secure Login
- Signup
- Forgot Password
- Protected Sessions
- SQLite Authentication

---

### Dashboard
- Executive Dashboard
- KPI Cards
- Productivity Score
- Charts
- Timeline
- Recent Activity
- AI Insights

---

### Meeting Intelligence
- Meeting Summarization
- Action Item Extraction
- Deadline Detection
- Decision Detection
- Risk Detection
- Productivity Score
- Manager Insights

---

### AI Workplace Assistant
- Context-aware AI Chat
- General AI Conversation
- Suggested Prompts
- Chat History
- Clear Chat
- Reads Meeting History
- Reads Documents
- Reads Reports

---

### Document Intelligence
- Upload PDF
- AI Summary
- Key Insights
- Question Answering
- Search

---

### Email Automation
- Professional Email Generator
- Follow-up Email
- Reminder Email

---

### Executive Intelligence
- Executive Brief
- Business Impact Analysis
- AI Recommendations
- Executive Summary

---

### Reports
- Meeting History
- Search
- Filters
- Download PDF
- Report Viewer

---

### Analytics
- Plotly Charts
- Meeting Health Score
- Productivity Dashboard
- Risk Dashboard

---

## User Workflow

**Login**
↓
**Dashboard**
↓
**Meeting Intelligence**
↓
**Save Meeting**
↓
**AI Assistant**
↓
**Executive Brief**
↓
**Reports**
↓
**Analytics**

---

## System Architecture

**User**
↓
**Authentication**
↓
**Dashboard**
↓
**AI Engine (Groq LLaMA)**
↓
**Meeting Intelligence | Document Intelligence | AI Assistant**
↓
**SQLite Database**
↓
**Reports & Analytics**

---

## Technology Stack

**Frontend**
- Streamlit
- HTML
- CSS
- JavaScript

**Backend**
- Python

**AI**
- Groq API (LLaMA Models)

**Database**
- SQLite

**Libraries**
- Plotly
- Pandas
- PyPDF2
- python-docx
- ReportLab
- python-dotenv

---

## UI Highlights

We have completely overhauled the platform to look and feel like a modern Flask + Bootstrap Enterprise application:
- ✔ Premium Enterprise SaaS Design
- ✔ Interactive Dashboard
- ✔ Modern Sidebar
- ✔ AI Chat Interface
- ✔ Responsive Layout
- ✔ Hover Animations
- ✔ Glassmorphism Cards
- ✔ Professional Color Palette
- ✔ Clean Typography

---

## Folder Structure

```text
WorkSense_AI/
├── app.py                         # Main entry point & Executive Dashboard
├── requirements.txt               # Dependencies
├── README.md                      # Project documentation
├── assets/
│   └── style.css                  # Global UI theme and styling overrides
├── prompts/
│   ├── dashboard_prompts.py       
│   ├── document_prompts.py        
│   ├── email_prompts.py           
│   ├── executive_prompts.py       
│   └── meeting_prompts.py         
├── utils/
│   ├── auth.py                    # Session management
│   ├── db.py                      # SQLite database operations
│   ├── document_processor.py      # PDF, DOCX, and TXT parsing
│   ├── export_utils.py            # PDF and TXT export functionality
│   └── groq_client.py             # LLM inference API wrapper
└── pages/
    ├── 1_Meeting_Intelligence.py  
    ├── 2_Document_Intelligence.py 
    ├── 4_Email_Automation.py      
    ├── 5_Analytics.py             
    ├── 6_Risk_Center.py           
    ├── 7_Task_Manager.py          
    ├── 8_Manager_Insights.py      
    ├── 9_Weekly_Reports.py        
    ├── 11_Meeting_History.py      
    ├── 12_Reports_Dashboard.py    
    ├── 13_Executive_Brief.py      
    └── 14_AI_Assistant.py         
```

---

## Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/WorkSense_AI.git
   cd WorkSense_AI
   ```

2. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create .env**
   Create a `.env` file in the root directory:
   ```text
   GROQ_API_KEY=YOUR_API_KEY
   ```

4. **Run**
   ```bash
   streamlit run app.py
   ```

---

## Screenshots

- **Login**
  ![Login Placeholder](#)
- **Dashboard**
  ![Dashboard Placeholder](#)
- **Meeting Intelligence**
  ![Meeting Intelligence Placeholder](#)
- **AI Assistant**
  ![AI Assistant Placeholder](#)
- **Document Intelligence**
  ![Document Intelligence Placeholder](#)
- **Executive Brief**
  ![Executive Brief Placeholder](#)
- **Reports**
  ![Reports Placeholder](#)
- **Analytics**
  ![Analytics Placeholder](#)

---

## Future Scope

- Microsoft Teams Integration
- Slack Integration
- Zoom Integration
- Google Meet Integration
- Google Calendar Sync
- Outlook Calendar
- Jira Integration
- Asana Integration
- Voice Assistant
- Mobile App
- Cloud Deployment
- Multi-user Collaboration
- Role-Based Access Control
- Multi-language Support

---

## Business Impact

WorkSense AI empowers organizations by strategically driving transformation in operational workflows. It helps enterprises:
- ✔ **Increase Productivity**: Automate note-taking and assignment extraction instantly.
- ✔ **Reduce Manual Work**: Eliminate hours spent formatting reports and action lists.
- ✔ **Improve Collaboration**: Break down data silos and sync team objectives.
- ✔ **Better Decision Making**: Utilize deep AI-driven analytics and manager insights.
- ✔ **Track Deadlines**: Extract and monitor project deadlines from conversations organically.
- ✔ **AI-powered Executive Reporting**: Automatically convert daily activities into high-level briefs.
- ✔ **Workplace Automation**: Save time via intelligent follow-up email generation.

---

## Why WorkSense AI?

Unlike traditional, single-purpose meeting tools, **WorkSense AI** combines:
- Meeting Intelligence
- Document Intelligence
- AI Assistant
- Executive Reporting
- Analytics
- Email Automation
- Business Insights

...into **one unified Enterprise AI platform**, operating securely via a local SQLite database and powered by ultra-low-latency Groq AI logic. 

---

## Authors

- **[Your Name]** - [GitHub Link]
- **[Team Member]** - [GitHub Link]

---

## License

MIT License
