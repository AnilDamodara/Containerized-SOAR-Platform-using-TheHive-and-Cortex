# Configuration Files Guide

This directory contains all configuration files for the SOC platform components.

## Contents

- **thehive.conf** - TheHive application configuration
- **cortex.conf** - Cortex threat intelligence engine configuration
- **response-policies.yaml** - Automated response policies
- **alert-rules.yaml** - Alert collection rules
- **case-templates.json** - Case templates

## TheHive Configuration (thehive.conf)

Controls all TheHive operational settings.

### Key Sections

#### HTTP Settings
```conf
http.baseUrl = "http://localhost:9000"
http.port = 9000
```

#### Cassandra Database
```conf
cassandra {
  addresses = ["cassandra"]
  port = 9042
  keyspace = "thehive"
  username = ""
  password = ""
}
```

#### Elasticsearch Integration
```conf
elasticsearch {
  host = "elasticsearch"
  port = 9200
  index.nbShards = 5
  index.nbReplicas = 1
}
```

#### Attachment Storage (MinIO)
```conf
attachment {
  provider = "s3"
  s3 {
    endpoint = "http://minio:9000"
    region = "us-east-1"
    bucketName = "thehive-attachments"
    accessKeyId = "minioadmin"
    secretAccessKey = "minioadmin"
  }
}
```

#### Authentication
```conf
auth {
  provider = ["local"]
  session {
    inactivity = 24h
  }
}
```

## Cortex Configuration (cortex.conf)

Controls Cortex threat intelligence engine.

### Key Sections

#### HTTP Settings
```conf
http.port = 9001
http.baseUrl = "http://localhost:9001"
```

#### Database
```conf
database {
  driver = "org.postgresql.Driver"
  url = "jdbc:postgresql://cortex-db:5432/cortex"
  user = "cortex"
  password = "CortexPassword123!"
}
```

#### Analyzer Configuration
```conf
analyzer {
  enabled = [
    "File_Info_Details",
    "File_Type_Magic",
    "MaxMind_GeoIP",
    "VirusTotal",
    "Shodan",
    "URLhaus",
    "PhishTank"
  ]
}
```

#### Docker Integration
```conf
analyzer-docker {
  docker-path = "/usr/bin/docker"
  docker-uri = "unix:///var/run/docker.sock"
  image = "thehiveproject/cortex-analyzers:latest"
  remove-container = true
}
```

## Response Policies (response-policies.yaml)

Defines automated response actions for different threat types.

### Policy Structure
```yaml
policies:
  malware_detected:
    severity: [3, 4]
    actions:
      - isolate_host
      - quarantine_file
      - collect_logs
      - snapshot_host
    
  brute_force:
    severity: [3]
    actions:
      - disable_account
      - reset_password
      - alert_security_team
    
  data_exfiltration:
    severity: [4]
    actions:
      - isolate_host
      - block_ip
      - collect_logs
      - alert_security_team
```

### Adding Custom Policies
```yaml
custom_threat:
  severity: [2, 3, 4]
  actions:
    - action1
    - action2
    - action3
  escalation:
    - condition: "multiple_occurrences"
      action: "manual_review"
```

## Alert Rules (alert-rules.yaml)

Defines rules for alert collection and processing.

### Rule Structure
```yaml
rules:
  - id: "rule_001"
    name: "Malware Detection"
    source: "antivirus"
    condition:
      - field: "event_type"
        operator: "equals"
        value: "malware_detected"
    severity: 4
    actions:
      - create_case
      - enrich_observables
      - execute_response
    
  - id: "rule_002"
    name: "Suspicious Network Activity"
    source: "splunk"
    condition:
      - field: "alert_name"
        operator: "contains"
        value: "unusual"
      - field: "severity"
        operator: "greater_than"
        value: 2
    severity: 3
    actions:
      - create_case
      - investigate
```

## Case Templates (case-templates.json)

Pre-defined templates for different incident types.

### Template Structure
```json
{
  "templates": [
    {
      "id": "security_incident",
      "name": "Security Incident",
      "description": "General security incident template",
      "severity": 2,
      "tlp": 2,
      "tasks": [
        {
          "title": "Initial Investigation",
          "description": "Begin incident investigation"
        },
        {
          "title": "Evidence Collection",
          "description": "Collect forensic evidence"
        },
        {
          "title": "Analysis",
          "description": "Analyze collected evidence"
        },
        {
          "title": "Remediation",
          "description": "Execute remediation steps"
        }
      ],
      "observableTypes": [
        "ip",
        "domain",
        "file",
        "url"
      ]
    },
    {
      "id": "malware_incident",
      "name": "Malware Incident",
      "description": "Malware-related incident template",
      "severity": 3,
      "tlp": 2,
      "tasks": [
        {
          "title": "Containment",
          "description": "Contain malware spread"
        },
        {
          "title": "Analysis",
          "description": "Analyze malware"
        },
        {
          "title": "Eradication",
          "description": "Remove malware"
        },
        {
          "title": "Recovery",
          "description": "Restore systems"
        }
      ]
    }
  ]
}
```

## Environment Variable Configuration

### .env File Location
`docker/.env`

### Required Variables
```bash
# TheHive
THEHIVE_API_KEY=<api-key>
THEHIVE_URL=http://thehive:9000

# Cortex
CORTEX_API_KEY=<api-key>
CORTEX_URL=http://cortex:9001

# Splunk
SPLUNK_URL=https://splunk:8089
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=<password>

# Wazuh
WAZUH_URL=http://wazuh:55000
WAZUH_USERNAME=wazuh
WAZUH_PASSWORD=<password>

# VirusTotal
VIRUSTOTAL_API_KEY=<api-key>

# Dashboard
FLASK_ENV=production
SECRET_KEY=<random-secure-key>
```

### Optional Variables
```bash
# Database
DB_USER=cortex
DB_PASSWORD=<password>
DB_HOST=cortex-db
DB_NAME=cortex

# Email Notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=<email>
SMTP_PASSWORD=<password>
SMTP_FROM=soc@company.com

# Slack Integration
SLACK_WEBHOOK_URL=<webhook-url>
SLACK_CHANNEL=#security-alerts

# Syslog
SYSLOG_HOST=syslog-server
SYSLOG_PORT=514
SYSLOG_PROTOCOL=udp
```

## Loading Configuration

### At Container Startup
Configurations are loaded automatically from:
1. Container environment variables
2. `.env` file
3. Configuration files in `config/` directory
4. Default values

### Override Order (highest to lowest)
1. Command-line arguments
2. Environment variables
3. .env file
4. Configuration files
5. Default values

## Validation

### Check Configuration Syntax
```bash
# TheHive
docker exec thehive curl http://localhost:9000/api/v1/config

# Cortex
docker exec cortex curl http://localhost:9001/api/config
```

### Test Configuration
```bash
# Validate environment
docker-compose config

# Check specific service
docker-compose config --services
```

## Best Practices

1. **Security**
   - Never commit sensitive keys to version control
   - Use `.gitignore` for `.env` files
   - Rotate API keys regularly
   - Use strong passwords

2. **Organization**
   - Keep related settings together
   - Use clear, descriptive names
   - Document non-obvious settings
   - Version control configurations (without secrets)

3. **Maintenance**
   - Review configurations quarterly
   - Update with new features
   - Document changes
   - Test before deployment

4. **Performance**
   - Tune resource settings based on load
   - Monitor configuration impact
   - Adjust timeouts for network conditions
   - Cache appropriate settings

## Troubleshooting

### Configuration Not Applied
```bash
# Verify configuration syntax
docker-compose logs <service> | grep ERROR

# Restart service
docker-compose restart <service>

# Check configuration file
docker exec <service> cat /etc/config/service.conf
```

### Performance Issues
- Review JVM heap settings
- Check database connection pool
- Verify analyzer resources
- Check network timeouts

### Integration Issues
- Verify API keys
- Check credentials
- Test network connectivity
- Review firewall rules

## Support

For configuration help:
- Check service logs
- Review this documentation
- Consult service-specific docs
- Create GitHub issue
