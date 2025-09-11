import os
from app import create_app

# Load the appropriate configuration from environment variable
# Defaults to 'development' if not set
config_name = os.getenv('FLASK_CONFIG', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # The host='0.0.0.0' makes the server accessible from other devices on your network
    # The port can be any available port, 5000 is the default for Flask
    app.run(host='0.0.0.0', port=5000)
