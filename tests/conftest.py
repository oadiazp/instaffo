"""
Pytest configuration and fixtures
"""
import pytest
from unittest.mock import Mock, patch
from elasticsearch import Elasticsearch
from app import app
from services.elasticsearch_service import ElasticsearchService

@pytest.fixture
def test_client():
    """Flask test client fixture."""
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_es_client():
    """Mock Elasticsearch client fixture."""
    mock_client = Mock(spec=Elasticsearch)
    # Mock successful connection
    mock_client.ping.return_value = True
    mock_client.cluster.health.return_value = {
        'status': 'green',
        'number_of_nodes': 1,
        'active_shards': 5
    }
    return mock_client

@pytest.fixture
def es_service(mock_es_client):
    """ElasticsearchService fixture with mocked client."""
    return ElasticsearchService(mock_es_client)

# Sample test data
@pytest.fixture
def sample_job():
    return {
        'top_skills': ['Python', 'JavaScript', 'React'],
        'other_skills': ['Node.js', 'Docker'],
        'seniorities': ['midlevel', 'senior'],
        'max_salary': 75000
    }

@pytest.fixture
def sample_candidate():
    return {
        'top_skills': ['Python', 'React', 'Node.js'],
        'other_skills': ['Docker', 'Kubernetes'],
        'seniority': 'senior',
        'salary_expectation': 70000
    }
