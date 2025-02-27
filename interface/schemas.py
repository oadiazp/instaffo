"""
Request/response schemas for the API.

These schemas are used to validate and parse incoming requests and to
format outgoing responses.
"""
from marshmallow import Schema, fields, validate

from config import VALID_SENIORITIES


class DocumentQuerySchema(Schema):
    """Schema for document retrieval requests."""
    id = fields.String(required=True)
    doc_type = fields.String(required=True, validate=validate.OneOf(['job', 'candidate']))


class MatchingFiltersSchema(Schema):
    """Schema for matching filters."""
    salary_match = fields.Boolean(required=False, default=False)
    top_skill_match = fields.Boolean(required=False, default=False)
    seniority_match = fields.Boolean(required=False, default=False)


class MatchingQuerySchema(Schema):
    """Schema for matching requests."""
    id = fields.String(required=True)
    doc_type = fields.String(required=True, validate=validate.OneOf(['job', 'candidate']))
    filters = fields.Nested(MatchingFiltersSchema, required=True)


class JobResponseSchema(Schema):
    """Schema for job responses."""
    top_skills = fields.List(fields.String(), required=True)
    other_skills = fields.List(fields.String(), required=False)
    seniorities = fields.List(fields.String(validate=validate.OneOf(VALID_SENIORITIES)), required=False)
    max_salary = fields.Integer(required=False)


class CandidateResponseSchema(Schema):
    """Schema for candidate responses."""
    top_skills = fields.List(fields.String(), required=True)
    other_skills = fields.List(fields.String(), required=False)
    seniority = fields.String(validate=validate.OneOf(VALID_SENIORITIES), required=False)
    salary_expectation = fields.Integer(required=False)


class MatchResponseSchema(Schema):
    """Schema for match responses."""
    id = fields.String(required=True)
    relevance_score = fields.Float(required=True)


class MatchesResponseSchema(Schema):
    """Schema for matches responses."""
    matches = fields.List(fields.Nested(MatchResponseSchema), required=True)


class HealthResponseSchema(Schema):
    """Schema for health check responses."""
    status = fields.String(required=True)
    elasticsearch = fields.Dict(required=True)
