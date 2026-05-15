# Quick Start Guide
## Get the SOC Platform Running in 5 Minutes

## 1. Prerequisites Check
```bash
# Verify Docker
docker --version
# Expected: Docker version 20.10+

# Verify Docker Compose
docker-compose --version
# Expected: Docker Compose version 2.0+
```

## 2. Download/Clone Project
```bash
cd /opt
git clone <repository> soc-platform
cd soc-platform
```

## 3. Configure Environment (2 minutes)
```bash
cd docker
nano .env

# Minimal required configuration:
THEHIVE_API_KEY=your-api-key
SPLUNK_URL=https://your-splunk:8089
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=password
WAZUH_URL=http://your-wazuh:55000
VIRUSTOTAL_API_KEY=your-vt-key
```

## 4. Start Services (1 minute)
```bash
docker-compose up -d

# Wait for services to start
sleep 60

# Check status
docker-compose ps
```

## 5. Access Services
```
TheHive:   http://localhost:9000
Cortex:    http://localhost:9001
Dashboard: http://localhost:5000
Wazuh:     http://localhost:55000
```

## 6. Initial Setup (2 minutes)

### TheHive Setup
1. Navigate to http://localhost:9000
2. Create admin account
3. Create API key in Settings > Users
4. Copy API key to .env as THEHIVE_API_KEY

### Dashboard Setup
1. Navigate to http://localhost:5000
2. Dashboard should load automatically
3. Check "Overview" for statistics

## Quick Test

### Create Test Alert
```bash
curl -X POST http://localhost:9000/api/v1/alert \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Alert",
    "description": "Test alert for verification",
    "severity": 2,
    "tlp": 2,
    "type": "alert",
    "source": "test"
  }'
```

### View Dashboard
- Open http://localhost:5000
- Check statistics
- View recent alerts

## Common Ports
- 9000 - TheHive
- 9001 - Cortex
- 9001 - MinIO
- 9042 - Cassandra
- 9200 - Elasticsearch
- 5000 - Web Dashboard
- 5432 - PostgreSQL
- 55000 - Wazuh

## Verify All Services Running
```bash
docker-compose ps

# All services should show "Up" or "healthy"
```

## View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f thehive
docker-compose logs -f dashboard
docker-compose logs -f alert-collector
```

## Stop Services
```bash
docker-compose stop
```

## Restart Services
```bash
docker-compose restart
```

## Full Cleanup
```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v
```

## Troubleshooting

### Services show "Restarting"
```bash
docker-compose logs | grep ERROR
# Check error messages and resolve issues
```

### Can't access dashboard
```bash
# Check if port 5000 is free
netstat -tlnp | grep 5000

# Check dashboard logs
docker-compose logs dashboard
```

### API key not working
```bash
# Generate new key in TheHive UI
# Update .env file
# Restart alert collector
docker-compose restart alert-collector
```

## Next Steps
1. Read full documentation: `/docs/README.md`
2. Configure alert sources
3. Set up response policies
4. Create case templates
5. Configure notifications

## Need Help?
- Check logs: `docker-compose logs`
- Review documentation: `/docs/`
- Check playbooks: `/playbooks/`
