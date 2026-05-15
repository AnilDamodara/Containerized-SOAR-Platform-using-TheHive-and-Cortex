# API Integration Guide
## Complete API Reference for SOC Platform

## Table of Contents
1. [Dashboard API](#dashboard-api)
2. [TheHive API](#thehive-api)
3. [Cortex API](#cortex-api)
4. [Alert Collector API](#alert-collector-api)
5. [Response Engine API](#response-engine-api)
6. [Authentication](#authentication)
7. [Error Handling](#error-handling)

## Dashboard API

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### 1. Dashboard Statistics
**GET** `/dashboard/stats`

Get overall dashboard statistics and metrics.

**Response:**
```json
{
  "total_cases": 25,
  "new_cases": 3,
  "open_cases": 12,
  "closed_cases": 13,
  "total_alerts": 45,
  "new_alerts": 5,
  "severity_distribution": {
    "1": 10,
    "2": 20,
    "3": 10,
    "4": 5
  },
  "mttr": 4.5
}
```

#### 2. List Cases
**GET** `/cases?limit=100`

Get all cases with optional filtering.

**Parameters:**
- `limit` (int): Maximum number of cases (default: 100)
- `status` (string): Filter by status (New, InProgress, Resolved)
- `severity` (int): Filter by severity (1-4)

**Response:**
```json
[
  {
    "id": "case-123",
    "caseId": 1,
    "title": "Suspicious Network Activity",
    "description": "Detected unusual network traffic",
    "severity": 3,
    "status": "InProgress",
    "createdAt": "2024-01-15T10:30:00Z",
    "owner": "analyst1",
    "tags": ["network", "suspicious"]
  }
]
```

#### 3. Get Case Details
**GET** `/cases/<case_id>`

Get detailed information about a specific case.

**Response:**
```json
{
  "case": {
    "id": "case-123",
    "title": "Suspicious Network Activity",
    "description": "Details...",
    "severity": 3,
    "status": "InProgress",
    "observables": 5,
    "tasks": 3
  },
  "observables": [
    {
      "id": "obs-1",
      "dataType": "ip",
      "data": "192.168.1.100",
      "message": "Suspicious IP",
      "enrichment": {
        "virustotal": { "positives": 5, "total": 72 },
        "geolocation": { "country": "US" }
      }
    }
  ]
}
```

#### 4. Update Case Status
**PATCH** `/cases/<case_id>/status`

Update the status of a case.

**Request Body:**
```json
{
  "status": "Resolved"
}
```

**Valid Status Values:**
- New
- InProgress
- Resolved

**Response:**
```json
{
  "id": "case-123",
  "status": "Resolved",
  "updatedAt": "2024-01-15T11:00:00Z"
}
```

#### 5. List Alerts
**GET** `/alerts?limit=100`

Get all active alerts.

**Response:**
```json
[
  {
    "id": "alert-456",
    "title": "Malware Detection",
    "description": "Potential malware detected",
    "severity": 4,
    "source": "antivirus",
    "createdAt": "2024-01-15T10:15:00Z",
    "status": "New"
  }
]
```

#### 6. Threat Intelligence Jobs
**GET** `/enrichment`

Get active threat enrichment jobs.

**Response:**
```json
[
  {
    "id": "job-789",
    "analyzer": "VirusTotal",
    "data": "file_hash_here",
    "status": "Success",
    "report": {
      "positives": 5,
      "total": 72,
      "vendors": [...],
      "analysis_date": "2024-01-15"
    }
  }
]
```

#### 7. Incident Timeline
**GET** `/timeline`

Get timeline of all incidents.

**Response:**
```json
[
  {
    "id": "case-123",
    "title": "Incident Name",
    "date": "2024-01-15T10:30:00Z",
    "severity": 3,
    "status": "Resolved"
  }
]
```

#### 8. Health Check
**GET** `/health`

Check if dashboard API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T11:00:00Z"
}
```

## TheHive API

### Base URL
```
http://localhost:9000/api/v1
```

### Authentication
```
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

### Common Endpoints

#### Create Case
**POST** `/case`

```bash
curl -X POST http://localhost:9000/api/v1/case \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Security Incident",
    "description": "Incident description",
    "severity": 3,
    "tlp": 2,
    "status": "New",
    "tags": ["incident", "security"],
    "template": "Security Incident"
  }'
```

#### Create Alert
**POST** `/alert`

```bash
curl -X POST http://localhost:9000/api/v1/alert \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Security Alert",
    "description": "Alert description",
    "severity": 2,
    "tlp": 2,
    "type": "external",
    "source": "splunk",
    "sourceRef": "alert-12345"
  }'
```

#### Get Cases
**GET** `/case?sort=-createdAt&limit=100`

#### Get Case by ID
**GET** `/case/<case_id>`

#### Update Case
**PATCH** `/case/<case_id>`

```bash
curl -X PATCH http://localhost:9000/api/v1/case/case-123 \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "InProgress",
    "severity": 3
  }'
```

#### Create Observable
**POST** `/case/<case_id>/observable`

```bash
curl -X POST http://localhost:9000/api/v1/case/case-123/observable \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "dataType": "ip",
    "data": "192.168.1.100",
    "message": "Source IP",
    "tlp": 2
  }'
```

#### Get Observables
**GET** `/case/<case_id>/observable`

#### Add Comment
**POST** `/case/<case_id>/comment`

```bash
curl -X POST http://localhost:9000/api/v1/case/case-123/comment \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Investigation findings..."
  }'
```

## Cortex API

### Base URL
```
http://localhost:9001/api
```

### Authentication
```
Authorization: Bearer <API_KEY>
```

#### Get Analyzers
**GET** `/analyzer`

#### Run Analyzer
**POST** `/analyzer/<analyzer_name>/run`

```bash
curl -X POST http://localhost:9001/api/analyzer/VirusTotal/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "file_hash_here",
    "dataType": "file",
    "tlp": 2
  }'
```

#### Get Job Status
**GET** `/job/<job_id>`

#### Get Job Result
**GET** `/job/<job_id>/result`

## Alert Collector API

### Internal API (for integration)

#### Process Splunk Alert
```python
from alert_collector import SplunkConnector

splunk = SplunkConnector(
    url="https://splunk:8089",
    username="admin",
    password="password"
)

alerts = splunk.get_security_alerts()
```

#### Process Wazuh Alert
```python
from alert_collector import WazuhConnector

wazuh = WazuhConnector(
    url="http://wazuh:55000",
    username="wazuh",
    password="password"
)

alerts = wazuh.get_alerts(severity=3)
```

#### Send to TheHive
```python
from alert_collector import TheHiveConnector

thehive = TheHiveConnector(
    url="http://thehive:9000",
    api_key="your-api-key"
)

case = thehive.create_case({
    "title": "Alert Title",
    "severity": 3,
    "description": "Description"
})
```

## Response Engine API

### Internal API (for automation)

#### Execute Response Action
```python
from response_engine import ResponseEngine, ResponseAction

engine = ResponseEngine()

result = engine.execute_response(
    ResponseAction.ISOLATE_HOST,
    target="hostname",
    parameters={"reason": "malware_detected"}
)
```

#### Get Applicable Policies
```python
from response_engine import ResponsePolicy

policy = ResponsePolicy()

actions = policy.get_policy(
    threat_type="malware_detected",
    severity=4
)
```

## Authentication

### API Key Generation

#### TheHive
1. Login to TheHive UI
2. Settings > Users
3. Click on your user
4. Add API Key
5. Copy and use the key

#### Cortex
1. Login to Cortex UI
2. Settings > Users
3. Create new API key
4. Copy and use the key

### Using API Keys

```bash
# Header method
curl -H "Authorization: Bearer YOUR_API_KEY" http://api-endpoint

# Query parameter method
curl "http://api-endpoint?key=YOUR_API_KEY"
```

## Error Handling

### HTTP Status Codes
- `200 OK`: Successful request
- `201 Created`: Resource created
- `204 No Content`: Successful with no response
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Missing or invalid API key
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "error": "error message",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-15T11:00:00Z"
}
```

### Common Errors

#### Invalid API Key
```json
{
  "error": "Unauthorized",
  "code": "INVALID_API_KEY"
}
```

#### Resource Not Found
```json
{
  "error": "Case not found",
  "code": "CASE_NOT_FOUND"
}
```

#### Invalid Parameters
```json
{
  "error": "Invalid severity value",
  "code": "INVALID_PARAMETER",
  "details": {
    "field": "severity",
    "message": "Must be 1-4"
  }
}
```

## Rate Limiting

- Dashboard API: 100 requests/minute
- TheHive API: 1000 requests/hour
- Cortex API: 500 requests/hour

## Webhooks

### Register Webhook
```bash
curl -X POST http://localhost:9000/api/v1/case/webhook \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-endpoint.com/webhook",
    "events": ["case:created", "case:updated"],
    "secret": "webhook-secret"
  }'
```

### Webhook Events
- `case:created` - New case created
- `case:updated` - Case updated
- `case:closed` - Case closed
- `comment:added` - Comment added to case
- `observable:added` - Observable added

## SDK Examples

### Python
```python
import requests

API_KEY = "your-api-key"
THEHIVE_URL = "http://localhost:9000"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Create case
response = requests.post(
    f"{THEHIVE_URL}/api/v1/case",
    headers=headers,
    json={
        "title": "Test Case",
        "severity": 2
    }
)

case = response.json()
print(f"Case created: {case['id']}")
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

const API_KEY = "your-api-key";
const THEHIVE_URL = "http://localhost:9000";

const headers = {
  "Authorization": `Bearer ${API_KEY}`,
  "Content-Type": "application/json"
};

// Create case
axios.post(`${THEHIVE_URL}/api/v1/case`, {
  title: "Test Case",
  severity: 2
}, { headers })
  .then(res => console.log(`Case created: ${res.data.id}`))
  .catch(err => console.error(err));
```

## Best Practices

1. **API Key Security**
   - Never hardcode API keys
   - Use environment variables
   - Rotate keys regularly
   - Use separate keys per service

2. **Rate Limiting**
   - Implement backoff strategy
   - Cache responses when possible
   - Use batch operations

3. **Error Handling**
   - Always check HTTP status codes
   - Implement retry logic
   - Log all API calls

4. **Performance**
   - Use pagination for large results
   - Filter results server-side when possible
   - Implement caching

## Support

For API issues:
- Check logs: `docker-compose logs <service>`
- Review API documentation
- Create GitHub issue with error details
