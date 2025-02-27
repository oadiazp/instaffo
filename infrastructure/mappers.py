"""
Mappers between domain entities and external data structures.

Mappers are responsible for transforming data between the domain model and
external data structures like Elasticsearch documents.
"""
from typing import Dict, List, Optional
from uuid import UUID

from domain.models import Candidate, Job
from domain.value_objects import Salary, Seniority, Skill


class JobMapper:
    """Mapper between Job domain entity and Elasticsearch document."""

    @staticmethod
    def to_domain(doc_id: str, doc: Dict) -> Job:
        """
        Convert an Elasticsearch document to a Job domain entity.

        Args:
            doc_id: The document ID
            doc: The Elasticsearch document source

        Returns:
            A Job domain entity
        """
        top_skills = [Skill(name=skill) for skill in doc.get('top_skills', [])]
        other_skills = [Skill(name=skill) for skill in doc.get('other_skills', [])]

        seniorities = []
        for seniority_str in doc.get('seniorities', []):
            try:
                seniorities.append(Seniority.from_string(seniority_str))
            except ValueError:
                # Skip invalid seniority values
                pass

        max_salary = Salary(doc['max_salary']) if 'max_salary' in doc else None

        # Handle string IDs by converting them to UUID format or creating a dummy UUID
        try:
            uuid_id = UUID(doc_id)
        except ValueError:
            # For mock data with simple IDs, create a namespaced UUID from the string
            # This ensures we have a valid UUID even with simple string IDs like "1"
            uuid_id = UUID('00000000-0000-0000-0000-{:012d}'.format(int(doc_id)))

        return Job(
            id=uuid_id,
            top_skills=top_skills,
            other_skills=other_skills,
            seniorities=seniorities,
            max_salary=max_salary
        )

    @staticmethod
    def to_document(job: Job) -> Dict:
        """
        Convert a Job domain entity to an Elasticsearch document.

        Args:
            job: The Job domain entity

        Returns:
            An Elasticsearch document representation
        """
        return {
            'top_skills': [str(skill) for skill in job.top_skills],
            'other_skills': [str(skill) for skill in job.other_skills],
            'seniorities': [str(seniority) for seniority in job.seniorities],
            'max_salary': job.max_salary.value if job.max_salary else None
        }


class CandidateMapper:
    """Mapper between Candidate domain entity and Elasticsearch document."""

    @staticmethod
    def to_domain(doc_id: str, doc: Dict) -> Candidate:
        """
        Convert an Elasticsearch document to a Candidate domain entity.

        Args:
            doc_id: The document ID
            doc: The Elasticsearch document source

        Returns:
            A Candidate domain entity
        """
        top_skills = [Skill(name=skill) for skill in doc.get('top_skills', [])]
        other_skills = [Skill(name=skill) for skill in doc.get('other_skills', [])]

        seniority = None
        if 'seniority' in doc:
            try:
                seniority = Seniority.from_string(doc['seniority'])
            except ValueError:
                # Invalid seniority value
                pass

        salary_expectation = Salary(doc['salary_expectation']) if 'salary_expectation' in doc else None

        # Handle string IDs by converting them to UUID format or creating a dummy UUID
        try:
            uuid_id = UUID(doc_id)
        except ValueError:
            # For mock data with simple IDs, create a namespaced UUID from the string
            uuid_id = UUID('00000000-0000-0000-0000-{:012d}'.format(int(doc_id)))

        return Candidate(
            id=uuid_id,
            top_skills=top_skills,
            other_skills=other_skills,
            seniority=seniority,
            salary_expectation=salary_expectation
        )

    @staticmethod
    def to_document(candidate: Candidate) -> Dict:
        """
        Convert a Candidate domain entity to an Elasticsearch document.

        Args:
            candidate: The Candidate domain entity

        Returns:
            An Elasticsearch document representation
        """
        return {
            'top_skills': [str(skill) for skill in candidate.top_skills],
            'other_skills': [str(skill) for skill in candidate.other_skills],
            'seniority': str(candidate.seniority) if candidate.seniority else None,
            'salary_expectation': candidate.salary_expectation.value if candidate.salary_expectation else None
        }