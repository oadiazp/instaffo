"""
Repository implementations for domain entities.

These repositories use Elasticsearch to store and retrieve domain entities.
"""
import logging
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from config import CANDIDATES_INDEX, FILTER_CONFIGS, JOBS_INDEX, MIN_MATCHING_SKILLS
from domain.models import Candidate, Job
from domain.repositories import CandidateRepository, JobRepository
from domain.value_objects import MatchScore
from infrastructure.elasticsearch_client import ElasticsearchClient
from infrastructure.mappers import CandidateMapper, JobMapper

logger = logging.getLogger(__name__)


class ElasticsearchJobRepository(JobRepository):
    """Elasticsearch implementation of the JobRepository interface."""
    
    def __init__(self, es_client: ElasticsearchClient):
        self.es_client = es_client
        
    def get_by_id(self, job_id: str) -> Optional[Job]:
        """
        Retrieve a job by its ID.
        
        Args:
            job_id: The ID of the job to retrieve
            
        Returns:
            The Job entity if found, None otherwise
        """
        doc = self.es_client.get_document(JOBS_INDEX, job_id)
        if not doc:
            return None
            
        return JobMapper.to_domain(job_id, doc)
    
    def find_matches_for_candidate(self, candidate_id: str, 
                                  filters: Dict[str, bool]) -> List[Tuple[str, MatchScore]]:
        """
        Find jobs that match a candidate based on specified filters.
        
        Args:
            candidate_id: The ID of the candidate to match
            filters: Dictionary of enabled matching criteria
            
        Returns:
            A list of tuples containing job IDs and their match scores
        """
        # Get candidate details first
        candidate_repo = ElasticsearchCandidateRepository(self.es_client)
        candidate = candidate_repo.get_by_id(candidate_id)
        
        if not candidate:
            raise ValueError(f"Candidate with ID {candidate_id} not found")
            
        # Build query based on enabled filters
        should_queries = []
        
        if filters.get('salary_match'):
            if candidate.salary_expectation:
                should_queries.append({
                    "range": {
                        "max_salary": {
                            "gte": candidate.salary_expectation.value
                        }
                    }
                })
                
        if filters.get('top_skill_match'):
            if candidate.top_skills:
                top_skills = [str(skill) for skill in candidate.top_skills]
                min_should_match = min(len(top_skills), MIN_MATCHING_SKILLS)
                should_queries.append({
                    "terms": {
                        "top_skills": top_skills,
                        "boost": FILTER_CONFIGS['top_skill_match']['weight']
                    },
                    "minimum_should_match": min_should_match
                })
                
        if filters.get('seniority_match'):
            if candidate.seniority:
                should_queries.append({
                    "term": {
                        "seniorities": str(candidate.seniority),
                        "boost": FILTER_CONFIGS['seniority_match']['weight']
                    }
                })
                
        if not should_queries:
            return []
            
        # Execute search
        query = {
            "query": {
                "bool": {
                    "should": should_queries,
                    "minimum_should_match": 1
                }
            }
        }
        
        hits = self.es_client.search(JOBS_INDEX, query)
        
        # Format results
        matches = []
        for hit in hits:
            job_id = hit['_id']
            score = hit['_score']
            matches.append((job_id, MatchScore(score)))
            
        return matches


class ElasticsearchCandidateRepository(CandidateRepository):
    """Elasticsearch implementation of the CandidateRepository interface."""
    
    def __init__(self, es_client: ElasticsearchClient):
        self.es_client = es_client
        
    def get_by_id(self, candidate_id: str) -> Optional[Candidate]:
        """
        Retrieve a candidate by its ID.
        
        Args:
            candidate_id: The ID of the candidate to retrieve
            
        Returns:
            The Candidate entity if found, None otherwise
        """
        doc = self.es_client.get_document(CANDIDATES_INDEX, candidate_id)
        if not doc:
            return None
            
        return CandidateMapper.to_domain(candidate_id, doc)
    
    def find_matches_for_job(self, job_id: str, 
                            filters: Dict[str, bool]) -> List[Tuple[str, MatchScore]]:
        """
        Find candidates that match a job based on specified filters.
        
        Args:
            job_id: The ID of the job to match
            filters: Dictionary of enabled matching criteria
            
        Returns:
            A list of tuples containing candidate IDs and their match scores
        """
        # Get job details first
        job_repo = ElasticsearchJobRepository(self.es_client)
        job = job_repo.get_by_id(job_id)
        
        if not job:
            raise ValueError(f"Job with ID {job_id} not found")
            
        # Build query based on enabled filters
        should_queries = []
        
        if filters.get('salary_match'):
            if job.max_salary:
                should_queries.append({
                    "range": {
                        "salary_expectation": {
                            "lte": job.max_salary.value
                        }
                    }
                })
                
        if filters.get('top_skill_match'):
            if job.top_skills:
                top_skills = [str(skill) for skill in job.top_skills]
                min_should_match = min(len(top_skills), MIN_MATCHING_SKILLS)
                should_queries.append({
                    "terms": {
                        "top_skills": top_skills,
                        "boost": FILTER_CONFIGS['top_skill_match']['weight']
                    },
                    "minimum_should_match": min_should_match
                })
                
        if filters.get('seniority_match'):
            if job.seniorities:
                job_seniorities = [str(seniority) for seniority in job.seniorities]
                should_queries.append({
                    "terms": {
                        "seniority": job_seniorities,
                        "boost": FILTER_CONFIGS['seniority_match']['weight']
                    }
                })
                
        if not should_queries:
            return []
            
        # Execute search
        query = {
            "query": {
                "bool": {
                    "should": should_queries,
                    "minimum_should_match": 1
                }
            }
        }
        
        hits = self.es_client.search(CANDIDATES_INDEX, query)
        
        # Format results
        matches = []
        for hit in hits:
            candidate_id = hit['_id']
            score = hit['_score']
            matches.append((candidate_id, MatchScore(score)))
            
        return matches
