"""
Document retrieval routes for the API.

These routes provide endpoints for retrieving job and candidate documents.
"""
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
import logging

from infrastructure.service_factory import ServiceFactory
from interface.schemas import DocumentQuerySchema, JobResponseSchema, CandidateResponseSchema

logger = logging.getLogger(__name__)
bp = Blueprint('documents', __name__)

# Initialize dependencies using the service factory
es_client = ServiceFactory.create_elasticsearch_client()
document_service = ServiceFactory.create_document_service(es_client)

@bp.route('/document', methods=['GET'])
def get_document():
    """Retrieve a document by ID and type."""
    try:
        # Validate request parameters
        schema = DocumentQuerySchema()
        params = schema.load(request.args)

        doc_id = params['id']
        doc_type = params['doc_type']

        # Get document based on type
        if doc_type == 'job':
            document = document_service.get_job(doc_id)
            if document:
                result = JobResponseSchema().dump(document)
            else:
                return jsonify({'error': f"Job with ID {doc_id} not found"}), 404
        elif doc_type == 'candidate':
            document = document_service.get_candidate(doc_id)
            if document:
                result = CandidateResponseSchema().dump(document)
            else:
                return jsonify({'error': f"Candidate with ID {doc_id} not found"}), 404
        else:
            return jsonify({'error': f"Invalid document type: {doc_type}"}), 400

        return jsonify(result)

    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error retrieving document: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500