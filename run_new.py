import sys
from flask import Flask, render_template

# ✅ Debug: Show which Python is being used
print(f"🐍 Python executable: {sys.executable}")
print(f"📦 Python path: {sys.path[0]}")

# Create clean Flask app
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/test')
def test():
    return {
        'message': 'Flask is working in virtual environment!',
        'python_executable': sys.executable,
        'static_folder': app.static_folder,
        'template_folder': app.template_folder
    }


if __name__ == '__main__':
    print(f"📁 Static folder: {app.static_folder}")
    print(f"📁 Template folder: {app.template_folder}")

    # Debug routes
    print("\n=== REGISTERED ROUTES ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:20s} {rule}")
    print("=" * 40)

    app.run(debug=True, port=5001)
