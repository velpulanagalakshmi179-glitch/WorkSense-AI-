from flask import Flask, redirect, url_for, session
from flask_session import Session
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configure session
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-key-fallback")
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_PERMANENT"] = False
    Session(app)

    # Initialize Database
    from utils.db import init_db
    init_db()

    # Register Blueprints
    from .blueprints.auth import auth_bp
    from .blueprints.dashboard import dashboard_bp
    from .blueprints.meetings import meetings_bp
    from .blueprints.documents import documents_bp
    from .blueprints.assistant import assistant_bp
    from .blueprints.reports import reports_bp
    from .blueprints.email import email_bp

    from .blueprints.analytics import analytics_bp
    from .blueprints.profile import profile_bp
    from .blueprints.risk import risk_bp
    from .blueprints.tasks import tasks_bp
    from .blueprints.insights import insights_bp
    from .blueprints.weekly import weekly_bp
    from .blueprints.about import about_bp
    from .blueprints.executive import executive_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(meetings_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(assistant_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(risk_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(insights_bp)
    app.register_blueprint(weekly_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(executive_bp)

    @app.route('/')
    def index():
        if not session.get("logged_in"):
            return redirect(url_for('auth.login'))
        return redirect(url_for('dashboard.index'))

    return app
