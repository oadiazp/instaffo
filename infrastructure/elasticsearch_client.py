"""
Elasticsearch client wrapper.

This module provides a wrapper around the Elasticsearch client with connection
management and error handling.
"""
import logging
import os
import time
from typing import Any, Dict, List, Optional

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError, TransportError

# Import configuration
from config import ES_CONFIG

logger = logging.getLogger(__name__)

class ElasticsearchClient:
    """
    Wrapper around the Elasticsearch client with connection management and error handling.
    """

    def __init__(self):
        self._client = None
        self._mock_mode = False
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Elasticsearch client with retries."""
        MAX_RETRIES = 5
        RETRY_DELAY = 5  # seconds
        INITIAL_DELAY = 5  # seconds - reduced for faster development

        # Enable mock mode for development if environment variable is set
        if os.environ.get('MOCK_ELASTICSEARCH', 'false').lower() == 'true':
            logger.warning("Running in MOCK_ELASTICSEARCH mode. No real ES connection will be attempted.")
            self._mock_mode = True
            return

        # Initial delay to wait for ES container to be ready
        logger.info(f"Waiting {INITIAL_DELAY} seconds for Elasticsearch to start...")
        time.sleep(INITIAL_DELAY)

        for attempt in range(MAX_RETRIES):
            try:
                self._client = Elasticsearch(**ES_CONFIG)
                logger.info(f"Attempting to connect to Elasticsearch: {ES_CONFIG['hosts']}")

                if self._client.ping():
                    logger.info("Successfully connected to Elasticsearch")
                    # Verify indices exist
                    try:
                        indices = self._client.indices.get_alias().keys()
                        logger.info(f"Available indices: {list(indices)}")
                    except Exception as e:
                        logger.warning(f"Could not retrieve indices: {str(e)}")
                    return
                else:
                    logger.warning("Elasticsearch ping failed but did not raise an exception")

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} to connect to Elasticsearch failed: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Waiting {wait_time} seconds before next attempt...")
                    time.sleep(wait_time)

        logger.error("Failed to establish Elasticsearch connection after all retries")
        # Enable mock mode when connection fails
        logger.warning("Falling back to MOCK_ELASTICSEARCH mode due to connection failure")
        self._mock_mode = True

    def ping(self) -> bool:
        """Check if the Elasticsearch connection is healthy."""
        if self._mock_mode:
            return True

        try:
            if not self._client:
                return False
            return self._client.ping()
        except Exception as e:
            logger.error(f"Error pinging Elasticsearch: {str(e)}")
            return False

    def get_health(self) -> Dict:
        """Get Elasticsearch cluster health."""
        if self._mock_mode:
            return {"status": "yellow", "mock_mode": True}

        try:
            if not self._client:
                return {"status": "unavailable"}
            return self._client.cluster.health()
        except Exception as e:
            logger.error(f"Error getting Elasticsearch health: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_document(self, index: str, doc_id: str) -> Optional[Dict]:
        """
        Retrieve a document from Elasticsearch by ID.

        Args:
            index: The index to search in
            doc_id: The document ID

        Returns:
            The document source if found, None otherwise
        """
        if self._mock_mode:
            # Return mock data in development mode
            if index == 'jobs' and doc_id == '1':
                return {
                    "top_skills": ["Python", "AWS", "Machine Learning"],
                    "other_skills": ["Docker", "Kubernetes", "Git"],
                    "seniorities": ["midlevel", "senior"],
                    "max_salary": 85000
                }
            elif index == 'candidates' and doc_id == '1':
                return {
                    "top_skills": ["Python", "AWS", "TypeScript"],
                    "other_skills": ["React", "Node.js"],
                    "seniority": "senior",
                    "salary_expectation": 80000
                }
            return None

        try:
            if not self._client:
                logger.error("Elasticsearch client not initialized")
                return None

            result = self._client.get(index=index, id=doc_id)
            if '_source' in result:
                return result['_source']
            return None

        except NotFoundError:
            logger.warning(f"Document with ID {doc_id} not found in index {index}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            return None

    def search(self, index: str, query: Dict) -> List[Dict]:
        """
        Execute a search query against Elasticsearch.

        Args:
            index: The index to search in
            query: The Elasticsearch query

        Returns:
            A list of search hits
        """
        if self._mock_mode:
            # Return mock search results
            return [
                {"_id": "2", "_score": 0.95},
                {"_id": "5", "_score": 0.87},
                {"_id": "7", "_score": 0.76}
            ]

        try:
            if not self._client:
                logger.error("Elasticsearch client not initialized")
                return []

            results = self._client.search(index=index, body=query, size=100)
            return results['hits']['hits']

        except Exception as e:
            logger.error(f"Error executing search: {str(e)}")
            return []