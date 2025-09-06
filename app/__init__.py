from flask import Flask
from .extensions import db, migrate, jwt, cors, limiter
from .config import config


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)

    # Import models to ensure they're registered
    from .models import User, Task, Category, FocusSession

    # Register API blueprints
    from .api.auth import bp as auth_bp
    from .api.tasks import bp as tasks_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')

    # Basic route
    @app.route('/')
    def index():
        return {'message': 'Planora API is running!', 'version': '1.0.0'}

    # Health check
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'timestamp': str(datetime.utcnow())}

    return app
