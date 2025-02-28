# Job/Candidate Matching API

A Flask-based API service for retrieving and matching job/candidate documents from Elasticsearch indices using Domain-Driven Design (DDD) architecture.

## Project Overview

This API service allows you to:

- Retrieve job and candidate documents from Elasticsearch
- Find matching jobs for a candidate based on customizable criteria
- Find matching candidates for a job based on customizable criteria
- Monitor the health of the service and its dependencies

The system uses a mock mode when Elasticsearch is not available, allowing for development and testing without a live Elasticsearch instance.

## Architecture

This project follows Domain-Driven Design (DDD) principles with a clear separation of concerns:

### Layers

1. **Domain Layer** - Core business logic and entities
   - Domain entities (Job, Candidate)
   - Value objects (Skill, Seniority, Salary)
   - Domain services (MatchingService)
   - Repository interfaces

2. **Application Layer** - Use case implementations
   - Application services (DocumentService, MatchingApplicationService)
   - Data Transfer Objects (DTOs)

3. **Infrastructure Layer** - Technical concerns
   - Repository implementations
   - External service integrations (Elasticsearch)
   - Mappers between domain entities and external data structures

4. **Interface Layer** - User interface components
   - Controllers/routes
   - Request/response schemas
   - Input validation

## Project Structure

```
├── application/            # Application layer
│   ├── __init__.py
│   ├── dto.py              # Data Transfer Objects
│   └── services.py         # Application services
├── domain/                 # Domain layer
│   ├── __init__.py
│   ├── models.py           # Domain entities
│   ├── repositories.py     # Repository interfaces
│   ├── services.py         # Domain services
│   └── value_objects.py    # Value objects
├── infrastructure/         # Infrastructure layer
│   ├── __init__.py
│   ├── elasticsearch_client.py  # Elasticsearch client wrapper
│   ├── elasticsearch_service.py # Elasticsearch service
│   ├── mappers.py          # Entity-document mappers
│   ├── repositories.py     # Repository implementations
│   └── service_factory.py  # Service factory (DI container)
├── interface/              # Interface layer
│   ├── __init__.py
│   ├── controllers.py      # Controllers
│   └── schemas.py          # Request/response schemas
├── routes/                 # API routes
│   ├── __init__.py
│   ├── document_routes.py  # Document routes
│   ├── health_routes.py    # Health check routes
│   └── matching_routes.py  # Matching routes
├── tests/                  # Test suite
│   └── ...
├── app.py                  # Main application file
├── config.py               # Configuration
└── main.py                 # Entry point
```

## API Endpoints

### Health Check

Check the health of the API and its dependencies.

```
GET /health
```

**Response:**

```json
{
  "elasticsearch": {
    "connected": true,
    "details": {
      "status": "yellow",
      "mock_mode": true
    }
  },
  "status": "healthy"
}
```

### Document Retrieval

Retrieve a job or candidate document by ID.

```
GET /document?id={id}&doc_type={doc_type}
```

**Parameters:**
- `id` (required): The document ID
- `doc_type` (required): The document type, either "job" or "candidate"

**Example Response (Job):**

```json
{
  "top_skills": ["Python", "AWS", "Machine Learning"],
  "other_skills": ["Docker", "Kubernetes", "Git"],
  "seniorities": ["midlevel", "senior"],
  "max_salary": 85000
}
```

**Example Response (Candidate):**

```json
{
  "top_skills": ["Python", "AWS", "TypeScript"],
  "other_skills": ["React", "Node.js"],
  "seniority": "senior",
  "salary_expectation": 80000
}
```

### Matching

Find matching documents based on specified filters.

```
POST /matches
```

**Request Body:**

```json
{
  "id": "1",
  "doc_type": "job",
  "filters": {
    "salary_match": true,
    "top_skill_match": true,
    "seniority_match": true
  }
}
```

**Parameters:**
- `id` (required): The source document ID
- `doc_type` (required): The source document type, either "job" or "candidate"
- `filters` (required): The matching filters to apply:
  - `salary_match`: Match based on salary compatibility
  - `top_skill_match`: Match based on top skills
  - `seniority_match`: Match based on seniority levels

**Example Response:**

```json
{
  "matches": [
    {
      "id": "2",
      "relevance_score": 0.95
    },
    {
      "id": "5",
      "relevance_score": 0.87
    },
    {
      "id": "7",
      "relevance_score": 0.76
    }
  ]
}
```

## Testing the API

You can test the API using curl commands:

### Health Check
```bash
curl -X GET "http://localhost:5000/health" -H "Content-Type: application/json"
```

### Document Retrieval
```bash
# Get a job document
curl -X GET "http://localhost:5000/document?id=1&doc_type=job" -H "Content-Type: application/json"

# Get a candidate document
curl -X GET "http://localhost:5000/document?id=1&doc_type=candidate" -H "Content-Type: application/json"
```

### Matching
```bash
# Find candidates matching a job
curl -X POST "http://localhost:5000/matches" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "1",
    "doc_type": "job",
    "filters": {
      "salary_match": true,
      "top_skill_match": true,
      "seniority_match": true
    }
  }'

# Find jobs matching a candidate
curl -X POST "http://localhost:5000/matches" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "1",
    "doc_type": "candidate",
    "filters": {
      "salary_match": true,
      "top_skill_match": true,
      "seniority_match": true
    }
  }'
```

## Development Mode

The API includes a mock mode for development without a live Elasticsearch instance. To enable this mode, set the environment variable:

```
MOCK_ELASTICSEARCH=true
```

In mock mode, the API simulates Elasticsearch responses, providing predefined documents and search results.

## Running the Application

To start the application:

```bash
python main.py
```

The API will be available at http://localhost:5000.
