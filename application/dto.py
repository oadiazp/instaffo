"""
Data Transfer Objects (DTOs) for the application layer.

DTOs are simple objects that carry data between processes. They are used to
transfer data between the application layer and the interface layer.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class JobDTO:
    """Data Transfer Object for Job entities."""
    id: str
    top_skills: List[str]
    other_skills: List[str] = field(default_factory=list)
    seniorities: List[str] = field(default_factory=list)
    max_salary: Optional[int] = None


@dataclass
class CandidateDTO:
    """Data Transfer Object for Candidate entities."""
    id: str
    top_skills: List[str]
    other_skills: List[str] = field(default_factory=list)
    seniority: Optional[str] = None
    salary_expectation: Optional[int] = None


@dataclass
class MatchDTO:
    """Data Transfer Object for match results."""
    id: str
    relevance_score: float


@dataclass
class MatchFiltersDTO:
    """Data Transfer Object for match filters."""
    salary_match: bool = False
    top_skill_match: bool = False
    seniority_match: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, bool]) -> 'MatchFiltersDTO':
        """Create a MatchFiltersDTO from a dictionary."""
        return cls(
            salary_match=data.get('salary_match', False),
            top_skill_match=data.get('top_skill_match', False),
            seniority_match=data.get('seniority_match', False)
        )
