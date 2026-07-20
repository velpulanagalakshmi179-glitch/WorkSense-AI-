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

    # Register Blueprints
    from .blueprints.auth import auth_bp
    from .blueprints.dashboard import dashboard_bp
    from .blueprints.meetings import meetings_bp
    from .blueprints.documents import documents_bp
    from .blueprints.assistant import assistant_bp
    from .blueprints.reports import reports_bp
    from .blueprints.email import email_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(meetings_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(assistant_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(email_bp)

    @app.route('/')
    def index():
        if not session.get("logged_in"):
            return redirect(url_for('auth.login'))
        return redirect(url_for('dashboard.index'))

    return app
