"""
Main application file.

This file initializes the Flask application and registers the API routes.
"""
import logging
import os
import time

from flask import Flask
from elasticsearch import Elasticsearch

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set environment variable to enable mock mode for development
os.environ['MOCK_ELASTICSEARCH'] = 'true'
logger.info("Setting MOCK_ELASTICSEARCH=true for development")

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config')

# Initialize Elasticsearch client with retries
from config import ES_CONFIG
MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds - reduced for faster development
INITIAL_DELAY = 5  # seconds - reduced for faster development

def init_elasticsearch():
    """Initialize Elasticsearch client with improved logging and error handling."""
    # Use smaller initial delay during development
    logger.info(f"Waiting {INITIAL_DELAY} seconds for Elasticsearch to start...")
    time.sleep(INITIAL_DELAY)

    for attempt in range(MAX_RETRIES):
        try:
            es_client = Elasticsearch(**ES_CONFIG)
            logger.info(f"Attempting to connect to Elasticsearch: {ES_CONFIG['hosts']}")

            if es_client.ping():
                logger.info("Successfully connected to Elasticsearch")
                # Verify indices exist
                try:
                    indices = es_client.indices.get_alias().keys()
                    logger.info(f"Available indices: {list(indices)}")
                except Exception as e:
                    logger.warning(f"Could not retrieve indices: {str(e)}")
                return es_client
            else:
                logger.warning("Elasticsearch ping failed but did not raise an exception")

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} to connect to Elasticsearch failed: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                logger.info(f"Waiting {wait_time} seconds before next attempt...")
                time.sleep(wait_time)

    logger.error("Failed to establish Elasticsearch connection after all retries, returning None")
    return None

# Initialize Elasticsearch client
logger.info("Starting Elasticsearch client initialization")
es_client = init_elasticsearch()
logger.info(f"Elasticsearch client initialization complete: {'Success' if es_client else 'Failed'}")

# Import and register routes
from routes.document_routes import bp as document_routes_bp
from routes.matching_routes import bp as matching_routes_bp
from routes.health_routes import bp as health_routes_bp

logger.info("Registering API blueprints")
app.register_blueprint(document_routes_bp)
app.register_blueprint(matching_routes_bp)
app.register_blueprint(health_routes_bp)
logger.info("API blueprints registered successfully")

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return {'error': 'Resource not found'}, 404

@app.errorhandler(400)
def bad_request_error(error):
    return {'error': str(error)}, 400

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return {'error': 'Internal server error'}, 500

@app.before_request
def check_elasticsearch():
    global es_client
    if not es_client:
        try:
            logger.warning("Elasticsearch client not available, attempting to reconnect")
            es_client = init_elasticsearch()
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch connection: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting Flask application")
    app.run(host='0.0.0.0', port=5001, debug=True)