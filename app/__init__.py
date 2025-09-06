from flask import Flask, render_template, request, make_response
from flask_cors import CORS
from datetime import datetime
from .extensions import db, migrate, jwt, limiter
from .config import config


def create_app(config_name='default'):
    # ✅ Correctly point to the folders in the parent directory
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # Import models
    with app.app_context():
        from .models.user import User
        from .models.task import Task

    # Register API blueprints
    from .api.auth import bp as auth_bp
    from .api.tasks import bp as tasks_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')

    # Routes
    @app.route('/')
    def landing_page():
        return render_template('landing.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/register')
    def register_page():
        return render_template('register.html')

    @app.route('/test')
    def test_page():
        return render_template('test_api.html')

    # API Routes
    @app.route('/api')
    def api_home():
        return {'message': 'Planora API is running!', 'version': '1.0.0'}

    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': str(datetime.utcnow())}

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found', 'message': 'Endpoint not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "*")
            response.headers.add('Access-Control-Allow-Methods', "*")
            return response

    return app