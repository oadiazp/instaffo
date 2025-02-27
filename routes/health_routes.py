"""
Health check routes for monitoring the application.

These routes provide endpoints for checking the health of the application and its dependencies.
"""
from flask import Blueprint, jsonify
import logging

from infrastructure.service_factory import ServiceFactory

logger = logging.getLogger(__name__)
bp = Blueprint('health', __name__)

# Initialize dependencies using the service factory
es_client = ServiceFactory.create_elasticsearch_client()
es_service = ServiceFactory.create_elasticsearch_service(es_client)

@bp.route('/health', methods=['GET'])
def check_health():
    """Check the health of the application and its dependencies."""
    es_status = False
    es_details = {}

    try:
        if es_client and es_client.ping():
            cluster_health = es_client.get_health()
            es_status = True
            es_details = {
                'status': cluster_health['status'],
                'number_of_nodes': cluster_health.get('number_of_nodes', 'N/A'),
                'active_shards': cluster_health.get('active_shards', 'N/A')
            }
    except Exception as e:
        logger.error(f"Error checking Elasticsearch health: {str(e)}")
        es_details = {'error': str(e)}

    health_status = {
        'status': 'healthy' if es_status else 'unhealthy',
        'elasticsearch': {
            'connected': es_status,
            'details': es_details
        }
    }

    status_code = 200 if es_status else 503
    return jsonify(health_status), status_code