from flask import Flask, render_template, request, make_response
from flask_cors import CORS
from datetime import datetime
from .extensions import db, migrate, jwt, limiter
from .config import config


def create_app(config_name='default'):
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    # Configure CORS for the API
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Import models
    with app.app_context():
        from .models.user import User
        from .models.task import Task
        from .models.project import Project
        from .models.category import Category
        from .models.focus_session import FocusSession

    from .api.auth import bp as auth_bp
    from .api.tasks import bp as tasks_bp
    from .api.dashboard import bp as dashboard_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

    @app.route('/')
    def landing_page():
        return render_template('landing.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/register')
    def register_page():
        return render_template('register.html')

    @app.route('/dashboard')
    def dashboard_page():
        return render_template('dashboard.html')

    return app
