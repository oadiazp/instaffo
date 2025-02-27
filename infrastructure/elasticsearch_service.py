"""
Elasticsearch service for the job matching system.

This service provides functionality to interact with the Elasticsearch cluster
and perform operations related to job and candidate documents.
"""
import logging
from typing import Dict, List, Optional

from elasticsearch.exceptions import NotFoundError, ConnectionError

from config import (
    JOBS_INDEX, CANDIDATES_INDEX, MIN_MATCHING_SKILLS,
    FILTER_CONFIGS
)
from domain.value_objects import MatchScore

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """
    Service for interacting with Elasticsearch.
    
    This service provides methods for retrieving documents and finding matches
    based on various criteria.
    """
    
    def __init__(self, es_client):
        self.es = es_client
        
    def check_connection(self) -> bool:
        """
        Check if Elasticsearch connection is healthy.
        
        Returns:
            True if the connection is healthy, False otherwise
        """
        try:
            health = self.es.cluster.health()
            logger.info(f"Elasticsearch cluster status: {health['status']}")
            return True
        except ConnectionError as e:
            logger.error(f"Failed to connect to Elasticsearch: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking ES connection: {str(e)}")
            return False
            
    def get_document(self, doc_id: str, doc_type: str) -> Dict:
        """
        Retrieve a document by ID and type.
        
        Args:
            doc_id: The ID of the document to retrieve
            doc_type: The type of the document ('job' or 'candidate')
            
        Returns:
            The document source
            
        Raises:
            ValueError: If the document is not found or has an invalid format
            ConnectionError: If the Elasticsearch service is not available
        """
        if not self.check_connection():
            raise ConnectionError("Elasticsearch service is not available")
            
        index = JOBS_INDEX if doc_type == 'job' else CANDIDATES_INDEX
        try:
            logger.debug(f"Fetching {doc_type} document with ID: {doc_id}")
            result = self.es.get(index=index, id=doc_id)
            
            if '_source' not in result:
                raise ValueError(f"Invalid document format for {doc_type} with ID {doc_id}")
                
            return result['_source']
            
        except NotFoundError:
            logger.warning(f"{doc_type.capitalize()} with ID {doc_id} not found")
            raise ValueError(f"{doc_type.capitalize()} with ID {doc_id} not found")
        except Exception as e:
            logger.error(f"Error fetching document: {str(e)}")
            raise
            
    def find_matches(self, doc_id: str, doc_type: str, filters: Dict[str, bool]) -> List[Dict]:
        """
        Find matching documents based on filters.
        
        Args:
            doc_id: The ID of the source document
            doc_type: The type of the source document ('job' or 'candidate')
            filters: The matching filters to apply
            
        Returns:
            A list of matching documents with their relevance scores
            
        Raises:
            ValueError: If no filters are enabled or the source document is not found
            ConnectionError: If the Elasticsearch service is not available
        """
        if not self.check_connection():
            raise ConnectionError("Elasticsearch service is not available")
            
        source_index = JOBS_INDEX if doc_type == 'job' else CANDIDATES_INDEX
        target_index = CANDIDATES_INDEX if doc_type == 'job' else JOBS_INDEX
        
        try:
            # Get source document
            source_doc = self.get_document(doc_id, doc_type)
            
            # Build query based on enabled filters
            should_queries = []
            
            if filters.get('salary_match'):
                should_queries.append(self._build_salary_query(source_doc, doc_type))
                
            if filters.get('top_skill_match'):
                should_queries.append(self._build_skills_query(source_doc))
                
            if filters.get('seniority_match'):
                should_queries.append(self._build_seniority_query(source_doc, doc_type))
                
            if not should_queries:
                raise ValueError("At least one filter must be enabled")
                
            # Execute search
            query = {
                "query": {
                    "bool": {
                        "should": should_queries,
                        "minimum_should_match": 1
                    }
                }
            }
            
            logger.debug(f"Executing search query: {query}")
            results = self.es.search(
                index=target_index,
                body=query,
                _source=False,
                size=100  # Limit results to prevent overwhelming response
            )
            
            # Format results
            matches = []
            for hit in results['hits']['hits']:
                matches.append({
                    'id': hit['_id'],
                    'relevance_score': hit['_score']
                })
                
            return matches
            
        except Exception as e:
            logger.error(f"Error finding matches: {str(e)}")
            raise
            
    def _build_salary_query(self, source_doc: Dict, doc_type: str) -> Dict:
        """
        Build salary matching query based on document schema.
        
        Args:
            source_doc: The source document
            doc_type: The type of the source document ('job' or 'candidate')
            
        Returns:
            The salary matching query
            
        Raises:
            ValueError: If required salary fields are missing
        """
        try:
            if doc_type == 'job':
                # For jobs, find candidates with salary_expectation <= job's max_salary
                return {
                    "range": {
                        "salary_expectation": {
                            "lte": source_doc['max_salary']
                        }
                    }
                }
            else:
                # For candidates, find jobs with max_salary >= candidate's salary_expectation
                return {
                    "range": {
                        "max_salary": {
                            "gte": source_doc['salary_expectation']
                        }
                    }
                }
        except KeyError as e:
            logger.error(f"Missing salary field in document: {e}")
            raise ValueError(f"Missing required salary field: {e}")
            
    def _build_skills_query(self, source_doc: Dict) -> Dict:
        """
        Build skills matching query based on document schema.
        
        Args:
            source_doc: The source document
            
        Returns:
            The skills matching query
            
        Raises:
            ValueError: If the source document has no top skills
        """
        try:
            top_skills = source_doc.get('top_skills', [])
            if not top_skills:
                raise ValueError("Source document has no top skills")
                
            min_should_match = min(len(top_skills), MIN_MATCHING_SKILLS)
            return {
                "terms": {
                    "top_skills": top_skills,
                    "boost": FILTER_CONFIGS['top_skill_match']['weight']
                },
                "minimum_should_match": min_should_match
            }
        except Exception as e:
            logger.error(f"Error building skills query: {str(e)}")
            raise
            
    def _build_seniority_query(self, source_doc: Dict, doc_type: str) -> Dict:
        """
        Build seniority matching query based on document schema.
        
        Args:
            source_doc: The source document
            doc_type: The type of the source document ('job' or 'candidate')
            
        Returns:
            The seniority matching query
            
        Raises:
            ValueError: If required seniority fields are missing
        """
        try:
            if doc_type == 'job':
                # For jobs, match candidate's seniority against job's seniorities array
                seniorities = source_doc.get('seniorities', [])
                if not seniorities:
                    raise ValueError("Job document has no seniorities defined")
                return {
                    "terms": {
                        "seniority": seniorities,
                        "boost": FILTER_CONFIGS['seniority_match']['weight']
                    }
                }
            else:
                # For candidates, match candidate's single seniority against job's seniorities array
                seniority = source_doc.get('seniority')
                if not seniority:
                    raise ValueError("Candidate document has no seniority defined")
                return {
                    "term": {
                        "seniorities": seniority,
                        "boost": FILTER_CONFIGS['seniority_match']['weight']
                    }
                }
        except KeyError as e:
            logger.error(f"Missing seniority field in document: {e}")
            raise ValueError(f"Missing required seniority field: {e}")
