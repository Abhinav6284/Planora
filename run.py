import os
import sys
from datetime import datetime
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app(os.getenv('FLASK_CONFIG', 'default'))


@app.shell_context_processor
def make_shell_context():
    return {'db': db}


def test_db_connection():
    """Test database connection - SQLAlchemy 2.0 compatible"""
    try:
        with app.app_context():
            # Test connection using SQLAlchemy 2.0 syntax
            with db.engine.connect() as connection:
                # Test basic connection
                result = connection.execute(text('SELECT 1')).fetchone()
                print("✅ PostgreSQL connection successful!")

                # Show database version
                result = connection.execute(text('SELECT version()')).fetchone()
                print(f"✅ PostgreSQL version: {result[0]}")

                # List tables
                result = connection.execute(text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
                )).fetchall()
                tables = [r[0] for r in result] if result else []
                print(f"✅ Tables in database: {tables}")

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False
    return True


if __name__ == '__main__':
    print("🔍 Testing database connection...")
    if test_db_connection():
        print("🚀 Starting Planora API server...")
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        print("❌ Failed to connect to database. Check your configuration.")
        print("\n📋 Troubleshooting steps:")
        print("1. Verify PostgreSQL is running")
        print("2. Check your .env file database credentials")
        print("3. Ensure the database 'planora_db' exists")
        print("4. Test connection: psql -U postgres -h localhost -d planora_db")
