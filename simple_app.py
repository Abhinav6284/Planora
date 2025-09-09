#!/usr/bin/env python3
"""Simple test server for UI development"""

from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/terms')
def terms_page():
    return render_template('terms.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)