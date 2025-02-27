"""
Application services that implement the use cases of the application.

These services coordinate domain objects and repositories to fulfill
specific user requirements.
"""
from typing import Dict, List, Optional

from application.dto import CandidateDTO, JobDTO, MatchDTO, MatchFiltersDTO
from domain.models import Candidate, Job
from domain.repositories import CandidateRepository, JobRepository
from domain.services import MatchingService
from domain.value_objects import Salary, Seniority, Skill


class DocumentService:
    """
    Application service for handling document-related operations.
    
    This service provides methods for retrieving job and candidate documents.
    """
    
    def __init__(self, job_repository: JobRepository, candidate_repository: CandidateRepository):
        self.job_repository = job_repository
        self.candidate_repository = candidate_repository
        
    def get_job(self, job_id: str) -> Optional[JobDTO]:
        """
        Retrieve a job document by ID.
        
        Args:
            job_id: The ID of the job to retrieve
            
        Returns:
            The job document as a DTO, or None if not found
        """
        job = self.job_repository.get_by_id(job_id)
        if not job:
            return None
            
        return JobDTO(
            id=str(job.id),
            top_skills=[str(skill) for skill in job.top_skills],
            other_skills=[str(skill) for skill in job.other_skills],
            seniorities=[str(seniority) for seniority in job.seniorities],
            max_salary=job.max_salary.value if job.max_salary else None
        )
        
    def get_candidate(self, candidate_id: str) -> Optional[CandidateDTO]:
        """
        Retrieve a candidate document by ID.
        
        Args:
            candidate_id: The ID of the candidate to retrieve
            
        Returns:
            The candidate document as a DTO, or None if not found
        """
        candidate = self.candidate_repository.get_by_id(candidate_id)
        if not candidate:
            return None
            
        return CandidateDTO(
            id=str(candidate.id),
            top_skills=[str(skill) for skill in candidate.top_skills],
            other_skills=[str(skill) for skill in candidate.other_skills],
            seniority=str(candidate.seniority) if candidate.seniority else None,
            salary_expectation=candidate.salary_expectation.value if candidate.salary_expectation else None
        )


class MatchingApplicationService:
    """
    Application service for matching jobs and candidates.
    
    This service provides methods for finding matches between jobs and candidates.
    """
    
    def __init__(self, job_repository: JobRepository, candidate_repository: CandidateRepository, 
                 matching_service: MatchingService):
        self.job_repository = job_repository
        self.candidate_repository = candidate_repository
        self.matching_service = matching_service
        
    def find_matches(self, doc_id: str, doc_type: str, filters: MatchFiltersDTO) -> List[MatchDTO]:
        """
        Find matching documents based on the specified filters.
        
        Args:
            doc_id: The ID of the source document
            doc_type: The type of the source document ('job' or 'candidate')
            filters: The matching filters to apply
            
        Returns:
            A list of matching documents with their relevance scores
        """
        filters_dict = {
            'salary_match': filters.salary_match,
            'top_skill_match': filters.top_skill_match,
            'seniority_match': filters.seniority_match
        }
        
        if all(not value for value in filters_dict.values()):
            raise ValueError("At least one filter must be enabled")
        
        if doc_type == 'job':
            matches = self.matching_service.find_matching_candidates_for_job(
                self.job_repository, self.candidate_repository, doc_id, filters_dict
            )
        elif doc_type == 'candidate':
            matches = self.matching_service.find_matching_jobs_for_candidate(
                self.candidate_repository, self.job_repository, doc_id, filters_dict
            )
        else:
            raise ValueError(f"Invalid document type: {doc_type}")
            
        return [MatchDTO(id=match_id, relevance_score=score) for match_id, score in matches]
