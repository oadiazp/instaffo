"""
Unit tests for ElasticsearchService
"""
import pytest
from unittest.mock import Mock, patch
from elasticsearch.exceptions import NotFoundError
from services.elasticsearch_service import ElasticsearchService
from config import JOBS_INDEX, CANDIDATES_INDEX

def test_check_connection_success(es_service, mock_es_client):
    """Test successful connection check."""
    assert es_service.check_connection() is True
    mock_es_client.cluster.health.assert_called_once()

def test_check_connection_failure(mock_es_client):
    """Test connection check failure."""
    mock_es_client.cluster.health.side_effect = Exception("Connection failed")
    service = ElasticsearchService(mock_es_client)
    assert service.check_connection() is False

def test_get_document_success(es_service, mock_es_client, sample_job):
    """Test successful document retrieval."""
    mock_es_client.get.return_value = {'_source': sample_job}
    
    result = es_service.get_document('1', 'job')
    assert result == sample_job
    mock_es_client.get.assert_called_once_with(index=JOBS_INDEX, id='1')

def test_get_document_not_found(es_service, mock_es_client):
    """Test document not found scenario."""
    mock_es_client.get.side_effect = NotFoundError(404, "Document not found")
    
    with pytest.raises(ValueError, match="Job with ID 1 not found"):
        es_service.get_document('1', 'job')

def test_find_matches_with_salary_filter(es_service, mock_es_client, sample_job):
    """Test finding matches with salary filter."""
    mock_es_client.search.return_value = {
        'hits': {
            'hits': [
                {'_id': '1', '_score': 0.8},
                {'_id': '2', '_score': 0.6}
            ]
        }
    }
    
    filters = {'salary_match': True}
    matches = es_service.find_matches('1', 'job', filters)
    
    assert len(matches) == 2
    assert matches[0]['id'] == '1'
    assert matches[0]['relevance_score'] == 0.8
    mock_es_client.search.assert_called_once()

def test_find_matches_no_filters(es_service):
    """Test finding matches with no filters enabled."""
    filters = {'salary_match': False, 'top_skill_match': False, 'seniority_match': False}
    
    with pytest.raises(ValueError, match="At least one filter must be enabled"):
        es_service.find_matches('1', 'job', filters)

def test_build_salary_query_job(es_service):
    """Test building salary query for job document."""
    job = {'max_salary': 75000}
    query = es_service._build_salary_query(job, 'job')
    
    assert query['range']['salary_expectation']['lte'] == 75000

def test_build_salary_query_candidate(es_service):
    """Test building salary query for candidate document."""
    candidate = {'salary_expectation': 70000}
    query = es_service._build_salary_query(candidate, 'candidate')
    
    assert query['range']['max_salary']['gte'] == 70000

def test_build_skills_query(es_service):
    """Test building skills query."""
    doc = {'top_skills': ['Python', 'JavaScript']}
    query = es_service._build_skills_query(doc)
    
    assert 'terms' in query
    assert query['terms']['top_skills'] == ['Python', 'JavaScript']

def test_build_seniority_query_job(es_service):
    """Test building seniority query for job."""
    job = {'seniorities': ['midlevel', 'senior']}
    query = es_service._build_seniority_query(job, 'job')
    
    assert 'terms' in query
    assert query['terms']['seniority'] == ['midlevel', 'senior']

def test_build_seniority_query_candidate(es_service):
    """Test building seniority query for candidate."""
    candidate = {'seniority': 'senior'}
    query = es_service._build_seniority_query(candidate, 'candidate')
    
    assert 'term' in query
    assert query['term']['seniorities'] == 'senior'
