import os
from typing import Dict, List

# Elasticsearch configuration
ES_HOST = os.getenv('ES_HOST', '0.0.0.0')  # Use 0.0.0.0 instead of localhost
ES_PORT = int(os.getenv('ES_PORT', 9200))

# Index names
JOBS_INDEX = 'jobs'
CANDIDATES_INDEX = 'candidates'

# Search configuration
MIN_MATCHING_SKILLS = 2

# Filter configurations
FILTER_CONFIGS: Dict[str, Dict] = {
    'salary_match': {
        'enabled': True,
        'weight': 1.0
    },
    'top_skill_match': {
        'enabled': True,
        'weight': 2.0
    },
    'seniority_match': {
        'enabled': True,
        'weight': 1.5
    }
}

# Elasticsearch connection settings
ES_CONFIG = {
    'hosts': [f"http://{ES_HOST}:{ES_PORT}"],
    'verify_certs': False,
    'retry_on_timeout': True,
    'max_retries': 5,
    'request_timeout': 60,
    'sniff_on_start': False
}

# Valid seniorities for validation
VALID_SENIORITIES: List[str] = [
    'none', 'junior', 'midlevel', 'senior', 'lead', 'principal'
]