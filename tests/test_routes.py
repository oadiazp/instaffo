"""
Integration tests for API routes
"""
import json
import pytest
from unittest.mock import patch

def test_health_check(test_client, mock_es_client):
    """Test health check endpoint."""
    with patch('app.es_client', mock_es_client):
        response = test_client.get('/health')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'healthy'
        assert data['elasticsearch']['connected'] is True

def test_get_document_success(test_client, mock_es_client, sample_candidate):
    """Test successful document retrieval."""
    mock_es_client.get.return_value = {'_source': sample_candidate}
    
    with patch('app.es_client', mock_es_client):
        response = test_client.get('/document?id=1&doc_type=candidate')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['top_skills'] == sample_candidate['top_skills']
        assert data['seniority'] == sample_candidate['seniority']

def test_get_document_not_found(test_client, mock_es_client):
    """Test document not found scenario."""
    mock_es_client.get.side_effect = ValueError("Document not found")
    
    with patch('app.es_client', mock_es_client):
        response = test_client.get('/document?id=999&doc_type=job')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert 'error' in data

def test_find_matches_success(test_client, mock_es_client):
    """Test successful match finding."""
    mock_response = {
        'hits': {
            'hits': [
                {'_id': '1', '_score': 0.8},
                {'_id': '2', '_score': 0.6}
            ]
        }
    }
    mock_es_client.get.return_value = {'_source': {'top_skills': ['Python'], 'seniority': 'senior'}}
    mock_es_client.search.return_value = mock_response
    
    with patch('app.es_client', mock_es_client):
        request_data = {
            'id': '1',
            'doc_type': 'job',
            'filters': {
                'salary_match': True,
                'top_skill_match': True,
                'seniority_match': False
            }
        }
        response = test_client.post('/matches',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert len(data['matches']) == 2
        assert data['matches'][0]['id'] == '1'
        assert data['matches'][0]['relevance_score'] == 0.8

def test_find_matches_validation_error(test_client):
    """Test match finding with invalid request data."""
    request_data = {
        'id': '1',
        'doc_type': 'invalid_type',  # Invalid document type
        'filters': {
            'salary_match': True
        }
    }
    response = test_client.post('/matches',
                              data=json.dumps(request_data),
                              content_type='application/json')
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert 'error' in data
