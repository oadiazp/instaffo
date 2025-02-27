"""
Matching routes for finding compatible jobs and candidates.

These routes provide endpoints for finding matches between jobs and candidates
based on specified criteria.
"""
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
import logging

from application.dto import MatchFiltersDTO
from infrastructure.service_factory import ServiceFactory
from interface.schemas import MatchingQuerySchema

logger = logging.getLogger(__name__)
bp = Blueprint('matching', __name__)

# Initialize dependencies using the service factory
es_client = ServiceFactory.create_elasticsearch_client()
matching_service = ServiceFactory.create_matching_application_service(es_client)

@bp.route('/matches', methods=['POST'])
def find_matches():
    """Find matching documents based on filters."""
    try:
        # Validate request body
        schema = MatchingQuerySchema()
        data = schema.load(request.json)

        # Create filters DTO
        filters = MatchFiltersDTO.from_dict(data['filters'])

        # Find matches
        matches = matching_service.find_matches(
            doc_id=data['id'],
            doc_type=data['doc_type'],
            filters=filters
        )

        return jsonify({'matches': matches})

    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error finding matches: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500