"""
Repository interfaces for domain entities.

Repositories abstract data access from the domain layer, providing collection-like
interfaces for accessing and persisting domain objects.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from domain.models import Candidate, Job
from domain.value_objects import MatchScore


class JobRepository(ABC):
    """Repository interface for Job entities."""
    
    @abstractmethod
    def get_by_id(self, job_id: str) -> Optional[Job]:
        """Retrieve a job by its ID."""
        pass
    
    @abstractmethod
    def find_matches_for_candidate(self, candidate_id: str, 
                                  filters: Dict[str, bool]) -> List[Tuple[str, MatchScore]]:
        """
        Find jobs that match a candidate based on specified filters.
        
        Returns a list of tuples containing job IDs and their match scores.
        """
        pass


class CandidateRepository(ABC):
    """Repository interface for Candidate entities."""
    
    @abstractmethod
    def get_by_id(self, candidate_id: str) -> Optional[Candidate]:
        """Retrieve a candidate by its ID."""
        pass
    
    @abstractmethod
    def find_matches_for_job(self, job_id: str, 
                            filters: Dict[str, bool]) -> List[Tuple[str, MatchScore]]:
        """
        Find candidates that match a job based on specified filters.
        
        Returns a list of tuples containing candidate IDs and their match scores.
        """
        pass
