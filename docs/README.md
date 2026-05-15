# Automated SOC Incident Response System
## Using TheHive, Cortex, Splunk, and Wazuh

## Project Overview

This is a comprehensive automated incident response platform that:
- Collects security alerts from multiple sources (Splunk, Wazuh)
- Automatically creates cases in TheHive
- Enriches indicators with Cortex threat intelligence
- Executes automated response actions
- Provides real-time web-based dashboard for SOC teams

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Alert Sources                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Splunk       │  │ Wazuh        │  │ External APIs    │  │
│  │ Enterprise   │  │ Security     │  │ (Custom)         │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────────┘  │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Alert Collection Service                       │
│  - Continuous monitoring                                    │
│  - Alert aggregation                                        │
│  - Deduplication                                            │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    TheHive                                  │
│  - Case Management                                          │
│  - Alert Creation                                           │
│  - Observable Tracking                                      │
└─────────────────┬───────────────────────────────────────────┘
                  │
         ┌────────┴──────────┐
         ▼                   ▼
┌──────────────────┐  ┌──────────────────┐
│ Cortex           │  │ Response Engine  │
│ - Analyzers      │  │ - Automated      │
│ - Threat Intel   │  │   Actions        │
│ - Enrichment     │  │ - Playbooks      │
└────────┬─────────┘  └──────┬───────────┘
         │                   │
         └───────────┬───────┘
                     ▼
         ┌─────────────────────┐
         │  Web Dashboard      │
         │  - Real-time Stats  │
         │  - Case Management  │
         │  - Response Logs    │
         └─────────────────────┘
```

## System Components

### 1. Alert Collection (`alert_collector.py`)
- **Purpose**: Collects security alerts from multiple sources
- **Sources**: Splunk, Wazuh, Custom APIs
- **Functions**:
  - `TheHiveConnector`: Creates cases and observables in TheHive
  - `SplunkConnector`: Fetches alerts from Splunk
  - `WazuhConnector`: Fetches alerts from Wazuh
  - `AlertProcessor`: Converts alerts to TheHive format

### 2. Threat Enrichment (`threat_enrichment.py`)
- **Purpose**: Enriches observables with threat intelligence
- **Analyzers**: VirusTotal, Shodan, MaxMind GeoIP, URLhaus, PhishTank
- **Functions**:
  - `ThreatEnricher`: Runs Cortex analyzers
  - `ResponderAutomation`: Executes automated responses
  - `CortexConnector`: Connects to Cortex API

### 3. Automated Response (`response_engine.py`)
- **Purpose**: Executes automated incident response actions
- **Actions**:
  - Host isolation
  - IP blocking
  - File quarantine
  - Account disabling
  - Process termination
  - Log collection
  - Forensic snapshots

### 4. Web Dashboard (`app.py` + frontend)
- **Purpose**: Real-time SOC monitoring and management
- **Features**:
  - Dashboard statistics
  - Case management
  - Alert visualization
  - Threat intelligence display
  - Response action logging
  - Reporting and export

## Installation & Setup

### Prerequisites
- Docker & Docker Compose
- 8GB+ RAM
- 50GB+ storage
- Ubuntu 20.04+ or CentOS 7+

### Step 1: Clone or Download Project
```bash
cd /path/to/TheHive
```

### Step 2: Configure Environment Variables
Edit `docker/.env`:
```bash
# TheHive
THEHIVE_API_KEY=your-api-key
THEHIVE_URL=http://thehive:9000

# Splunk
SPLUNK_URL=https://your-splunk:8089
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=password

# Wazuh
WAZUH_URL=http://wazuh:55000
WAZUH_USERNAME=wazuh
WAZUH_PASSWORD=password

# VirusTotal
VIRUSTOTAL_API_KEY=your-vt-api-key
```

### Step 3: Deploy with Docker Compose
```bash
cd docker
docker-compose up -d
```

Wait for all services to be healthy:
```bash
docker-compose ps
```

### Step 4: Access Services
- **TheHive**: http://localhost:9000
- **Cortex**: http://localhost:9001
- **Wazuh**: http://localhost:55000
- **Dashboard**: http://localhost:5000

### Step 5: Initial Configuration

#### TheHive
1. Create admin account
2. Create API key for alert collector
3. Import case templates

#### Cortex
1. Configure analyzers
2. Add VirusTotal API key
3. Configure responders

#### Dashboard
1. Set API keys in environment variables
2. Access at http://localhost:5000

## Usage

### Creating an Alert Manually
```bash
curl -X POST http://localhost:9000/api/v1/alert \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Suspicious Login Attempt",
    "description": "Multiple failed login attempts",
    "severity": 3,
    "tlp": 2,
    "tags": ["splunk", "security"]
  }'
```

### Converting Alert to Case
Click "Convert to Case" on any alert in TheHive UI or Dashboard

### Enriching Observables
Observables are automatically enriched when created in a case through Cortex analyzers

### Automated Response
Responses execute automatically based on:
- Threat type
- Severity level
- Response policies
- Manual triggering via Dashboard

## API Endpoints

### Dashboard API
```
GET  /api/dashboard/stats       - Dashboard statistics
GET  /api/cases                 - List all cases
GET  /api/cases/<case_id>       - Case details
PATCH /api/cases/<case_id>/status - Update case status
GET  /api/alerts                - List all alerts
GET  /api/enrichment            - Threat enrichment jobs
GET  /api/timeline              - Incident timeline
GET  /api/health                - Health check
```

## Automated Response Policies

### Policy: Malware Detected (Severity 3-4)
- ✓ Isolate host
- ✓ Quarantine file
- ✓ Collect logs
- ✓ Create snapshot

### Policy: Brute Force (Severity 3)
- ✓ Disable account
- ✓ Reset password
- ✓ Alert security team

### Policy: Data Exfiltration (Severity 4)
- ✓ Isolate host
- ✓ Block IP
- ✓ Collect logs
- ✓ Alert security team

### Policy: Suspicious Process (Severity 2-3)
- ✓ Create snapshot
- ✓ Monitor closely
- ✓ Collect logs

### Policy: Unauthorized Access (Severity 3-4)
- ✓ Disable account
- ✓ Alert security team
- ✓ Collect logs

## Monitoring & Logs

### Container Logs
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f thehive
docker-compose logs -f cortex
docker-compose logs -f dashboard
docker-compose logs -f alert-collector
```

### Log Locations (inside containers)
- Alert Collector: `/var/log/alert-collector.log`
- Application: Docker stdout/stderr

## Performance Tuning

### Increase Cassandra Memory
Edit `docker-compose.yml`:
```yaml
cassandra:
  environment:
    - CASSANDRA_MAX_HEAP_SIZE=4G
    - CASSANDRA_HEAP_NEWSIZE=800M
```

### Increase Elasticsearch Heap
Edit `docker-compose.yml`:
```yaml
elasticsearch:
  environment:
    - ES_JAVA_OPTS=-Xms2g -Xmx2g
```

### Increase TheHive Memory
Edit `docker-compose.yml`:
```yaml
thehive:
  environment:
    - JVM_OPTS=-Xms2g -Xmx2g
```

## Troubleshooting

### TheHive not starting
```bash
docker-compose logs thehive
# Check Cassandra and Elasticsearch
docker-compose ps
```

### Cortex jobs failing
- Check analyzer availability
- Verify Docker daemon is accessible
- Check job timeout settings

### Dashboard not loading
- Check API keys in environment
- Verify TheHive/Cortex are running
- Check network connectivity

### Alerts not being collected
- Verify Splunk/Wazuh credentials
- Check firewall rules
- Verify API key permissions

## Extending the System

### Adding Custom Analyzers
Place analyzer scripts in Cortex analyzer directory:
```bash
docker exec cortex bash -c "cat /path/to/analyzer/requirements.txt"
```

### Adding Custom Response Actions
Edit `response_engine.py` and add methods:
```python
def _custom_action(self, target: str) -> Dict:
    # Implementation
    return {'success': True, ...}
```

### Adding Alert Sources
Modify `alert_collector.py`:
```python
class CustomAlertConnector:
    def get_alerts(self) -> List[Dict]:
        # Implement custom logic
        pass
```

## Security Considerations

1. **API Key Management**
   - Store in secure vault
   - Rotate regularly
   - Use environment variables

2. **Network Security**
   - Use TLS/SSL for all connections
   - Implement network segmentation
   - Restrict access to dashboard

3. **Database Security**
   - Change default passwords
   - Enable encryption at rest
   - Regular backups

4. **Audit Logging**
   - Enable audit logs in TheHive
   - Monitor API access
   - Track response actions

## Backup & Recovery

### Backup Cassandra
```bash
docker exec cassandra cqlsh -e "SELECT * FROM system_peers" > backup.cql
```

### Backup MinIO
```bash
docker exec minio mc mirror minio/thehive-attachments ./backup/
```

### Restore from Backup
```bash
# Stop containers
docker-compose stop

# Restore data
# ... restore commands ...

# Start containers
docker-compose start
```

## Support & Documentation

- **TheHive Docs**: https://docs.thehive-project.org/
- **Cortex Docs**: https://cortex-docs.readthedocs.io/
- **Splunk Docs**: https://docs.splunk.com/
- **Wazuh Docs**: https://documentation.wazuh.com/

## License

This project integrates open-source and commercial tools. Refer to individual tool licenses.

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request
