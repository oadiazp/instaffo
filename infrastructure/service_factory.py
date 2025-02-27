"""
Service factory for creating and initializing application services.

This factory helps with dependency injection and service initialization.
"""
from application.services import DocumentService, MatchingApplicationService
from domain.services import MatchingService
from infrastructure.elasticsearch_client import ElasticsearchClient
from infrastructure.elasticsearch_service import ElasticsearchService
from infrastructure.repositories import ElasticsearchCandidateRepository, ElasticsearchJobRepository


class ServiceFactory:
    """Factory for creating and initializing application services."""

    @staticmethod
    def create_elasticsearch_client() -> ElasticsearchClient:
        """Create and initialize the Elasticsearch client."""
        return ElasticsearchClient()

    @staticmethod
    def create_elasticsearch_service(es_client: ElasticsearchClient) -> ElasticsearchService:
        """Create and initialize the Elasticsearch service."""
        return ElasticsearchService(es_client)

    @staticmethod
    def create_job_repository(es_client: ElasticsearchClient) -> ElasticsearchJobRepository:
        """Create and initialize the job repository."""
        return ElasticsearchJobRepository(es_client)

    @staticmethod
    def create_candidate_repository(es_client: ElasticsearchClient) -> ElasticsearchCandidateRepository:
        """Create and initialize the candidate repository."""
        return ElasticsearchCandidateRepository(es_client)

    @staticmethod
    def create_matching_service() -> MatchingService:
        """Create and initialize the matching domain service."""
        return MatchingService()

    @staticmethod
    def create_document_service(es_client: ElasticsearchClient) -> DocumentService:
        """Create and initialize the document application service."""
        job_repository = ServiceFactory.create_job_repository(es_client)
        candidate_repository = ServiceFactory.create_candidate_repository(es_client)
        return DocumentService(job_repository, candidate_repository)

    @staticmethod
    def create_matching_application_service(es_client: ElasticsearchClient) -> MatchingApplicationService:
        """Create and initialize the matching application service."""
        job_repository = ServiceFactory.create_job_repository(es_client)
        candidate_repository = ServiceFactory.create_candidate_repository(es_client)
        matching_service = ServiceFactory.create_matching_service()
        return MatchingApplicationService(job_repository, candidate_repository, matching_service)