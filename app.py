# app.py

import os
from flask import Flask, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from app.models.user import User
from app.extensions import db, jwt

load_dotenv()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

    from app.config import config
    app.config.from_object(config[config_name])

    from app.extensions import db, jwt
    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints for API routes
    from app.api.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    @app.route('/')
    def index():
        return render_template('landing.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register_page():
        from flask import request, redirect, flash
        import requests
        if request.method == 'POST':
            api_url = request.url_root + 'api/auth/register'
            response = requests.post(api_url, json=request.form.to_dict())

            if response.status_code == 201:
                return redirect(url_for('dashboard'))
            else:
                flash('Registration failed')

        return render_template('register.html')

    @app.route('/login')
    def login_page():
        """Login page for a user"""
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        """Dashboard page - protected route"""
        # This route should be protected by JWT
        return render_template('dashboard.html', user_name="Test User")

    @app.route('/logout')
    def logout():
        """Logout handler"""
        return redirect(url_for('index'))

    # Finally, return the app instance
    return app


if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        # This will create the database tables based on your User model
        # Import the model to make it available
        db.create_all()
        print("Database tables created/updated.")

    print("🚀 Planora App Starting...")
    print("🌐 Visit: http://localhost:5000")

    # Run the app
    app.run(debug=True, port=5000)
