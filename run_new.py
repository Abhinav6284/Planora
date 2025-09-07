import sys
import os
from flask import Flask, render_template

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__,
            static_folder=os.path.join(basedir, './static/'),
            template_folder=os.path.join(basedir, './templates/'))


@app.route('/test')
def test():
    """A test route to confirm the environment is working."""
    return {
        'message': 'Flask is working correctly!',
        'python_executable': sys.executable,
        'static_folder_path': app.static_folder,
        'template_folder_path': app.template_folder
    }


if __name__ == '__main__':
    print("--- Planora Server Starting ---")
    print("\n=== Registered Routes ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:25s} {rule.methods} {rule}")
    print("=" * 40)

    # Run the app
    app.run(debug=True, port=5001)
