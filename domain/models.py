"""
Domain entities for the job matching system.

This module contains the core business entities that represent the key concepts
in our domain: jobs and candidates.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID

from domain.value_objects import Salary, Seniority, Skill


@dataclass
class Job:
    """
    Job entity representing a job posting.
    
    A job has a collection of required skills, acceptable seniority levels,
    and maximum salary offered.
    """
    id: UUID
    top_skills: List[Skill]
    other_skills: List[Skill] = field(default_factory=list)
    seniorities: List[Seniority] = field(default_factory=list)
    max_salary: Salary = None

    def matches_candidate_salary(self, candidate_salary_expectation: Salary) -> bool:
        """Check if the job's max salary meets or exceeds candidate's expectation."""
        if not self.max_salary or not candidate_salary_expectation:
            return False
        return self.max_salary.value >= candidate_salary_expectation.value

    def matches_candidate_seniority(self, candidate_seniority: Seniority) -> bool:
        """Check if the job accepts the candidate's seniority level."""
        if not self.seniorities or not candidate_seniority:
            return False
        return candidate_seniority in self.seniorities

    def skill_match_score(self, candidate_skills: List[Skill]) -> float:
        """
        Calculate a matching score based on skill overlap.
        
        Returns a value between 0 and 1, representing the proportion of the job's
        top skills that match the candidate's skills.
        """
        if not self.top_skills or not candidate_skills:
            return 0.0
            
        matching_skills = set(self.top_skills).intersection(set(candidate_skills))
        return len(matching_skills) / len(self.top_skills)


@dataclass
class Candidate:
    """
    Candidate entity representing a job seeker.
    
    A candidate has a set of skills, a seniority level, and a salary expectation.
    """
    id: UUID
    top_skills: List[Skill]
    other_skills: List[Skill] = field(default_factory=list)
    seniority: Seniority = None
    salary_expectation: Salary = None

    def matches_job_salary(self, job_max_salary: Salary) -> bool:
        """Check if the candidate's salary expectation is met by the job's max salary."""
        if not self.salary_expectation or not job_max_salary:
            return False
        return job_max_salary.value >= self.salary_expectation.value

    def matches_job_seniority(self, job_seniorities: List[Seniority]) -> bool:
        """Check if the candidate's seniority level is accepted by the job."""
        if not self.seniority or not job_seniorities:
            return False
        return self.seniority in job_seniorities

    def skill_match_score(self, job_top_skills: List[Skill]) -> float:
        """
        Calculate a matching score based on skill overlap.
        
        Returns a value between 0 and 1, representing the proportion of the job's
        top skills that match the candidate's skills.
        """
        if not job_top_skills or not self.top_skills:
            return 0.0
            
        all_candidate_skills = set(self.top_skills + self.other_skills)
        matching_skills = set(job_top_skills).intersection(all_candidate_skills)
        return len(matching_skills) / len(job_top_skills)
