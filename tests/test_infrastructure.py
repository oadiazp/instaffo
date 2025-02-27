
import pytest
from unittest.mock import Mock
from infrastructure.repositories import ElasticsearchRepository
from domain.models import Job, Candidate
from domain.value_objects import Salary, Seniority, Skills

def test_elasticsearch_repository():
    """Test elasticsearch repository implementation"""
    mock_es = Mock()
    mock_es.get.return_value = {
        "_source": {
            "top_skills": ["Python"],
            "seniority": "senior",
            "max_salary": 75000
        }
    }
    
    repository = ElasticsearchRepository(mock_es)
    
    # Test job retrieval
    job = repository.get_job("1")
    assert isinstance(job, Job)
    assert "Python" in job.top_skills
    assert job.seniority == Seniority.SENIOR
    
    # Test search functionality
    mock_es.search.return_value = {
        "hits": {
            "hits": [
                {"_id": "1", "_score": 0.8}
            ]
        }
    }
    
    matches = repository.find_matches(job, {"salary_match": True})
    assert len(matches) == 1
    assert matches[0]["id"] == "1"
