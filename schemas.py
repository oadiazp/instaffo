from marshmallow import Schema, fields, validate
from config import VALID_SENIORITIES

class DocumentQuerySchema(Schema):
    id = fields.String(required=True)
    doc_type = fields.String(required=True, validate=validate.OneOf(['job', 'candidate']))

class MatchingFiltersSchema(Schema):
    salary_match = fields.Boolean(required=False, default=False)
    top_skill_match = fields.Boolean(required=False, default=False)
    seniority_match = fields.Boolean(required=False, default=False)

class MatchingQuerySchema(Schema):
    id = fields.String(required=True)
    doc_type = fields.String(required=True, validate=validate.OneOf(['job', 'candidate']))
    filters = fields.Nested(MatchingFiltersSchema, required=True)
