
import pytest
from domain.models import Job, Candidate
from domain.value_objects import Salary, Seniority, Skills

def test_job_creation():
    """Test job entity creation and validation"""
    job = Job(
        id="1",
        top_skills=Skills(["Python", "JavaScript"]),
        seniority=Seniority.SENIOR,
        max_salary=Salary(75000)
    )
    assert job.id == "1"
    assert "Python" in job.top_skills
    assert job.seniority == Seniority.SENIOR
    assert job.max_salary.value == 75000

def test_candidate_creation():
    """Test candidate entity creation and validation"""
    candidate = Candidate(
        id="1",
        top_skills=Skills(["Python", "JavaScript"]),
        seniority=Seniority.SENIOR,
        salary_expectation=Salary(70000)
    )
    assert candidate.id == "1"
    assert "Python" in candidate.top_skills
    assert candidate.seniority == Seniority.SENIOR
    assert candidate.salary_expectation.value == 70000

def test_salary_validation():
    """Test salary value object validation"""
    with pytest.raises(ValueError):
        Salary(-1000)
    
    salary = Salary(50000)
    assert salary.value == 50000

def test_skills_validation():
    """Test skills value object validation"""
    with pytest.raises(ValueError):
        Skills([])
    
    skills = Skills(["Python", "JavaScript"])
    assert len(skills) == 2
    assert "Python" in skills
