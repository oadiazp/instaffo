"""
API controllers (routes) for the application.

These controllers handle HTTP requests and responses, including request
parsing, validation, and response formatting.
"""
import logging
from typing import Tuple

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from application.dto import MatchFiltersDTO
from infrastructure.service_factory import ServiceFactory
from interface.schemas import (
    CandidateResponseSchema, DocumentQuerySchema, HealthResponseSchema,
    JobResponseSchema, MatchesResponseSchema, MatchingQuerySchema
)

logger = logging.getLogger(__name__)

# Create the controllers
document_controller = Blueprint('documents', __name__)
matching_controller = Blueprint('matching', __name__)
health_controller = Blueprint('health', __name__)

# Initialize dependencies using the service factory
es_client = ServiceFactory.create_elasticsearch_client()
document_service = ServiceFactory.create_document_service(es_client)
matching_application_service = ServiceFactory.create_matching_application_service(es_client)


@health_controller.route('/health', methods=['GET'])
def check_health():
    """Check the health of the application and its dependencies."""
    es_status = False
    es_details = {}

    try:
        es_health = es_client.get_health()
        es_status = es_health.get('status') == 'green'
        es_details = es_health
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

    schema = HealthResponseSchema()
    result = schema.dump(health_status)

    status_code = 200 if es_status else 503
    return jsonify(result), status_code


@document_controller.route('/document', methods=['GET'])
def get_document():
    """Retrieve a document by ID and type."""
    try:
        # Validate request parameters
        schema = DocumentQuerySchema()
        params = schema.load(request.args)

        doc_id = params['id']
        doc_type = params['doc_type']

        # Get document using the document service
        if doc_type == 'job':
            document = document_service.get_job(doc_id)
            if document:
                result = JobResponseSchema().dump(document)
            else:
                return jsonify({'error': f"Job with ID {doc_id} not found"}), 404
        else:  # doc_type == 'candidate'
            document = document_service.get_candidate(doc_id)
            if document:
                result = CandidateResponseSchema().dump(document)
            else:
                return jsonify({'error': f"Candidate with ID {doc_id} not found"}), 404

        return jsonify(result)

    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error retrieving document: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@matching_controller.route('/matches', methods=['POST'])
def find_matches():
    """Find matching documents based on filters."""
    try:
        # Validate request body
        schema = MatchingQuerySchema()
        data = schema.load(request.json)

        # Create filters DTO
        filters = MatchFiltersDTO.from_dict(data['filters'])

        # Find matches using the matching application service
        matches = matching_application_service.find_matches(
            doc_id=data['id'],
            doc_type=data['doc_type'],
            filters=filters
        )

        # Format response
        result = MatchesResponseSchema().dump({'matches': matches})
        return jsonify(result)

    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error finding matches: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500