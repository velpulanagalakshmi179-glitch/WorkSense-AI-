"""
SQLite persistence layer.

The master prompt's spec implied persistent state (productivity scores over
time, task lists, weekly reports) with no database in the stack. Streamlit's
session_state resets per session, so anything that needs to survive a
refresh or be shared across pages goes through here instead.
"""
import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "worksense.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                organization TEXT,
                role TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                owner TEXT,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Pending',
                deadline TEXT,
                source TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # We drop the old table for this migration to avoid ALTER TABLE complexities in SQLite
        c.execute("DROP TABLE IF EXISTS meetings")
        c.execute("""
            CREATE TABLE meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                raw_text TEXT,
                summary TEXT,
                decisions TEXT,
                action_items TEXT,
                deadlines TEXT,
                productivity_score INTEGER,
                risks TEXT,
                manager_insights TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                doc_type TEXT,
                extracted_text TEXT,
                summary TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS risk_flags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                risk_type TEXT,
                description TEXT,
                severity TEXT,
                related_task_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS productivity_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_label TEXT,
                productivity_score INTEGER,
                team_efficiency INTEGER,
                completed_tasks INTEGER,
                pending_tasks INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                action_type TEXT,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS executive_briefs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


# --- Task helpers -----------------------------------------------------

def add_task(title, owner=None, priority="Medium", deadline=None, source=None):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO tasks (title, owner, priority, deadline, source) VALUES (?, ?, ?, ?, ?)",
            (title, owner, priority, deadline, source),
        )


def get_tasks(status=None):
    with get_conn() as conn:
        if status:
            rows = conn.execute("SELECT * FROM tasks WHERE status = ? ORDER BY id DESC", (status,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


def update_task_status(task_id, status):
    with get_conn() as conn:
        conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))

def get_upcoming_deadlines(limit=5):
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM tasks WHERE status != 'Completed' AND deadline IS NOT NULL AND deadline != '' AND deadline != 'None' AND deadline != 'Not specified' ORDER BY deadline ASC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

def delete_task(task_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))


# --- Meeting / document helpers ---------------------------------------

def save_meeting(title, raw_text, summary, decisions, action_items="[]", deadlines="[]", productivity_score=0, risks="[]", manager_insights=""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO meetings (title, raw_text, summary, decisions, action_items, deadlines, productivity_score, risks, manager_insights) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (title, raw_text, summary, decisions, action_items, deadlines, productivity_score, risks, manager_insights),
        )

def get_meetings(search_query="", date_filter=None):
    with get_conn() as conn:
        query_str = "SELECT * FROM meetings WHERE 1=1"
        params = []
        
        if search_query:
            query_str += " AND (title LIKE ? OR summary LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
            
        if date_filter:
            # SQLite DATE() extracts just the date part (YYYY-MM-DD)
            query_str += " AND DATE(created_at) = ?"
            params.append(str(date_filter))
            
        query_str += " ORDER BY id DESC"
        rows = conn.execute(query_str, params).fetchall()
        return [dict(r) for r in rows]

def delete_meeting(meeting_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))


def save_document(filename, doc_type, extracted_text, summary):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO documents (filename, doc_type, extracted_text, summary) VALUES (?, ?, ?, ?)",
            (filename, doc_type, extracted_text, summary),
        )


def get_all_context_text(limit=10):
    """Pulls recent meeting + document text for the AI Assistant's context window."""
    with get_conn() as conn:
        meetings = conn.execute(
            "SELECT title, raw_text FROM meetings ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        docs = conn.execute(
            "SELECT filename, extracted_text FROM documents ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in meetings], [dict(r) for r in docs]


# --- Risk helpers -------------------------------------------------------

def add_risk_flag(risk_type, description, severity, related_task_id=None):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO risk_flags (risk_type, description, severity, related_task_id) VALUES (?, ?, ?, ?)",
            (risk_type, description, severity, related_task_id),
        )


def get_risk_flags():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM risk_flags ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


def clear_risk_flags():
    with get_conn() as conn:
        conn.execute("DELETE FROM risk_flags")


# --- Productivity snapshots ---------------------------------------------

def save_productivity_snapshot(week_label, score, efficiency, completed, pending):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO productivity_snapshots
               (week_label, productivity_score, team_efficiency, completed_tasks, pending_tasks)
               VALUES (?, ?, ?, ?, ?)""",
            (week_label, score, efficiency, completed, pending),
        )


def get_productivity_history():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM productivity_snapshots ORDER BY id ASC").fetchall()
        return [dict(r) for r in rows]


def get_stats_summary():
    """Used by the Home dashboard's stat cards."""
    with get_conn() as conn:
        n_tasks = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        n_pending = conn.execute("SELECT COUNT(*) FROM tasks WHERE status != 'Completed'").fetchone()[0]
        n_meetings = conn.execute("SELECT COUNT(*) FROM meetings").fetchone()[0]
        n_docs = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        n_risks = conn.execute("SELECT COUNT(*) FROM risk_flags").fetchone()[0]
        return {
            "total_tasks": n_tasks,
            "pending_tasks": n_pending,
            "meetings_analyzed": n_meetings,
            "documents_processed": n_docs,
            "open_risks": n_risks,
        }

# --- Reports helpers ------------------------------------------------

def save_report(title, content):
    with get_conn() as conn:
        conn.execute("INSERT INTO reports (title, content) VALUES (?, ?)", (title, content))

def get_reports():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM reports ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

def delete_report(report_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM reports WHERE id = ?", (report_id,))

# --- Executive Brief helpers ------------------------------------------------

def save_executive_brief(title, content):
    with get_conn() as conn:
        conn.execute("INSERT INTO executive_briefs (title, content) VALUES (?, ?)", (title, content))

def get_executive_briefs(search_query=""):
    with get_conn() as conn:
        if search_query:
            query = f"%{search_query}%"
            rows = conn.execute("SELECT * FROM executive_briefs WHERE title LIKE ? OR content LIKE ? ORDER BY id DESC", (query, query)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM executive_briefs ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

def get_latest_executive_brief():
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM executive_briefs ORDER BY id DESC LIMIT 1").fetchone()
        return dict(row) if row else None

def delete_executive_brief(brief_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM executive_briefs WHERE id = ?", (brief_id,))

def get_executive_stats():
    """Calculates all metrics needed for the Executive Brief."""
    with get_conn() as conn:
        n_meetings = conn.execute("SELECT COUNT(*) FROM meetings").fetchone()[0]
        # Productivity Average
        prod_avg_row = conn.execute("SELECT AVG(productivity_score) FROM meetings").fetchone()
        prod_avg = round(prod_avg_row[0] or 0, 1)
        # Total tasks
        n_tasks = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        # High Priority Tasks
        high_priority_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE priority = 'High' AND status != 'Completed'").fetchone()[0]
        # Pending Tasks
        pending_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE status != 'Completed'").fetchone()[0]
        # Risks Identified
        risks_identified = conn.execute("SELECT COUNT(*) FROM risk_flags").fetchone()[0]
        
        return {
            "total_meetings": n_meetings,
            "productivity_average": prod_avg,
            "total_tasks": n_tasks,
            "high_priority_tasks": high_priority_tasks,
            "pending_tasks": pending_tasks,
            "risks_identified": risks_identified
        }

def get_reports_dashboard_stats():
    """Calculates metrics for the Reports Dashboard."""
    with get_conn() as conn:
        n_meetings = conn.execute("SELECT COUNT(*) FROM meetings").fetchone()[0]
        
        # Calculate Productivity Average from meetings
        prod_avg_row = conn.execute("SELECT AVG(productivity_score) FROM meetings").fetchone()
        prod_avg = round(prod_avg_row[0] or 0, 1)
        
        # High Risk Meetings (meetings where risks is not empty array)
        high_risk_meetings = conn.execute("SELECT COUNT(*) FROM meetings WHERE risks != '[]' AND risks IS NOT NULL").fetchone()[0]
        
        # Pending Tasks
        pending_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE status != 'Completed'").fetchone()[0]
        
        return {
            "total_meetings": n_meetings,
            "productivity_average": prod_avg,
            "high_risk_meetings": high_risk_meetings,
            "pending_tasks": pending_tasks
        }

# --- User / Auth helpers ------------------------------------------------

def create_user(name, email, password_hash, organization=None, role=None):
    with get_conn() as conn:
        try:
            conn.execute(
                "INSERT INTO users (name, email, password_hash, organization, role) VALUES (?, ?, ?, ?, ?)",
                (name, email, password_hash, organization, role)
            )
            return True
        except sqlite3.IntegrityError:
            # Email already exists
            return False

def get_user_by_email(email):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None

def update_user_password(email, new_password_hash):
    with get_conn() as conn:
        conn.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_password_hash, email))

# --- Activity Log helpers -----------------------------------------------

def log_activity(user_email, action_type, description):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO activity_log (user_email, action_type, description) VALUES (?, ?, ?)",
            (user_email, action_type, description)
        )

def get_recent_activity(limit=10):
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM activity_log ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

def get_emails_generated_count():
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM activity_log WHERE action_type = 'Email Generated'").fetchone()[0]


