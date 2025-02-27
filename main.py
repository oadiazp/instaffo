"""
Main entry point for the application.

This file imports the Flask application and runs it.
"""
from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)