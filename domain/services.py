"""
Domain services for the job matching system.

Domain services encapsulate business logic that doesn't naturally belong to a
single entity or value object.
"""
from typing import Dict, List, Tuple

from domain.models import Candidate, Job
from domain.repositories import CandidateRepository, JobRepository
from domain.value_objects import MatchScore


class MatchingService:
    """
    Domain service responsible for matching jobs with candidates.
    
    This service implements the core business logic for determining
    compatibility between jobs and candidates based on skills, seniority,
    and salary expectations.
    """
    
    @staticmethod
    def calculate_job_candidate_match(job: Job, candidate: Candidate,
                                     filters: Dict[str, bool]) -> MatchScore:
        """
        Calculate the match score between a job and a candidate based on enabled filters.
        
        Args:
            job: The job to match
            candidate: The candidate to match
            filters: Dictionary of enabled matching criteria
            
        Returns:
            A score between 0 and 1 indicating the match quality
        """
        score_components = []
        weights = []
        
        # Calculate skill match score if enabled
        if filters.get('top_skill_match', False):
            skill_score = job.skill_match_score(candidate.top_skills)
            score_components.append(skill_score)
            weights.append(2.0)  # Higher weight for skills
            
        # Calculate seniority match if enabled
        if filters.get('seniority_match', False) and job.matches_candidate_seniority(candidate.seniority):
            score_components.append(1.0)  # Full score for seniority match
            weights.append(1.5)  # Medium weight for seniority
            
        # Calculate salary match if enabled
        if filters.get('salary_match', False) and job.matches_candidate_salary(candidate.salary_expectation):
            score_components.append(1.0)  # Full score for salary match
            weights.append(1.0)  # Standard weight for salary
            
        # If no filters enabled or no matches, return 0
        if not score_components:
            return MatchScore(0.0)
            
        # Calculate weighted average
        total_weight = sum(weights)
        weighted_score = sum(s * w for s, w in zip(score_components, weights)) / total_weight
        
        return MatchScore(weighted_score)

    def find_matching_jobs_for_candidate(self, candidate_repository: CandidateRepository,
                                        job_repository: JobRepository, candidate_id: str,
                                        filters: Dict[str, bool]) -> List[Tuple[str, MatchScore]]:
        """
        Find jobs that match a candidate based on specified filters.
        
        This is a higher-level domain service that coordinates between repositories
        to implement the matching logic.
        """
        # Get candidate details
        candidate = candidate_repository.get_by_id(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate with ID {candidate_id} not found")
            
        # Use job repository to find potential matches
        matches = job_repository.find_matches_for_candidate(candidate_id, filters)
        
        return matches

    def find_matching_candidates_for_job(self, job_repository: JobRepository,
                                        candidate_repository: CandidateRepository,
                                        job_id: str, filters: Dict[str, bool]) -> List[Tuple[str, MatchScore]]:
        """
        Find candidates that match a job based on specified filters.
        
        This is a higher-level domain service that coordinates between repositories
        to implement the matching logic.
        """
        # Get job details
        job = job_repository.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job with ID {job_id} not found")
            
        # Use candidate repository to find potential matches
        matches = candidate_repository.find_matches_for_job(job_id, filters)
        
        return matches
