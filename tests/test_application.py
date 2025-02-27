
import pytest
from application.services import MatchingService
from domain.models import Job, Candidate
from domain.value_objects import Salary, Seniority, Skills

class MockRepository:
    def get_job(self, job_id):
        return Job("1", Skills(["Python"]), Seniority.SENIOR, Salary(75000))
    
    def get_candidate(self, candidate_id):
        return Candidate("1", Skills(["Python"]), Seniority.SENIOR, Salary(70000))
    
    def find_matches(self, entity, filters):
        return [{"id": "2", "score": 0.8}]

def test_matching_service():
    """Test matching service functionality"""
    service = MatchingService(MockRepository())
    
    # Test job matching
    matches = service.find_matches("1", "job", {"salary_match": True})
    assert len(matches) == 1
    assert matches[0]["id"] == "2"
    
    # Test invalid document type
    with pytest.raises(ValueError):
        service.find_matches("1", "invalid", {})
