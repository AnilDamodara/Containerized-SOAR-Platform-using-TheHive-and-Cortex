# Deployment & Setup Guide
## Automated SOC Incident Response System

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Step-by-Step Installation](#step-by-step-installation)
4. [Configuration](#configuration)
5. [Verification](#verification)
6. [Production Hardening](#production-hardening)

## Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04 LTS or CentOS 7+
- **RAM**: Minimum 16GB, Recommended 32GB+
- **Storage**: Minimum 100GB, Recommended 500GB+ SSD
- **CPU**: 8 cores minimum, 16+ recommended
- **Network**: 1Gbps connection
- **Internet**: Access to VirusTotal and other APIs

### Software Requirements
- Docker: 20.10+
- Docker Compose: 2.0+
- Git
- curl/wget
- SSH client

### API Keys Required
- VirusTotal API Key
- Splunk credentials
- Wazuh credentials
- TheHive admin access

## Pre-Deployment Checklist

- [ ] Hardware meets requirements
- [ ] Docker installed and running
- [ ] Network connectivity verified
- [ ] Firewall rules configured
- [ ] API keys obtained
- [ ] Storage path writable
- [ ] Backup strategy planned

## Step-by-Step Installation

### Phase 1: Environment Preparation

#### 1.1 Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### 1.2 Install Docker
```bash
# Add Docker repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

#### 1.3 Install Docker Compose (v1)
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

#### 1.4 Add User to Docker Group
```bash
sudo usermod -aG docker $USER
newgrp docker
```

#### 1.5 Create Project Directory
```bash
mkdir -p /opt/soc-platform
cd /opt/soc-platform
```

### Phase 2: Project Setup

#### 2.1 Clone Project
```bash
# Using git
git clone <repository-url> .

# OR Copy manually
cp -r /path/to/TheHive/* .
```

#### 2.2 Verify Directory Structure
```bash
ls -la

# Expected structure:
# config/
# dashboards/
# docker/
# docs/
# playbooks/
# scripts/
```

#### 2.3 Create Data Directories
```bash
mkdir -p ./data/{cassandra,elasticsearch,minio,cortex-db}
sudo chown -R 1000:1000 ./data
```

### Phase 3: Configuration

#### 3.1 Configure Environment
```bash
cd docker
cp .env.example .env  # or create from scratch

# Edit .env with your values
nano .env
```

#### 3.2 Update .env File
```bash
# TheHive Configuration
THEHIVE_API_KEY=your-secure-api-key-here
THEHIVE_URL=http://thehive:9000

# Splunk Configuration
SPLUNK_URL=https://your-splunk-server.com:8089
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=your-splunk-password

# Wazuh Configuration
WAZUH_USERNAME=wazuh
WAZUH_PASSWORD=your-wazuh-password

# VirusTotal
VIRUSTOTAL_API_KEY=your-virustotal-key

# Security
SECRET_KEY=generate-strong-random-key-here
```

#### 3.3 Generate Secure Keys
```bash
# Generate SECRET_KEY for Flask
python3 -c "import secrets; print(secrets.token_hex(32))"

# Generate API keys for other services
openssl rand -hex 32
```

### Phase 4: Deployment

#### 4.1 Pre-deployment Verification
```bash
# Check Docker daemon
docker ps

# Verify Docker Compose
docker-compose --version

# Check disk space
df -h

# Check available memory
free -h
```

#### 4.2 Build Images
```bash
docker-compose build
```

#### 4.3 Start Services
```bash
# Start all services
docker-compose up -d

# Alternative: Start with logs
docker-compose up

# Start in background with logs
nohup docker-compose up > docker.log 2>&1 &
```

#### 4.4 Wait for Services
```bash
# Check service status
docker-compose ps

# Wait for all services to be healthy (5-10 minutes)
watch docker-compose ps

# View logs
docker-compose logs -f
```

#### 4.5 Verify Startup
```bash
# Check logs for errors
docker-compose logs

# Test connectivity
curl http://localhost:9000     # TheHive
curl http://localhost:9001     # Cortex
curl http://localhost:5000/api/health  # Dashboard
```

### Phase 5: Initial Configuration

#### 5.1 Access TheHive
```
URL: http://your-server:9000
- Create admin account
- Set password
- Create API key
- Import case templates
```

#### 5.2 Configure TheHive API Key
```bash
# Get API key from TheHive UI
# Settings > Users > Add Key

# Update .env
THEHIVE_API_KEY=<generated-key>

# Restart alert collector
docker-compose restart alert-collector
```

#### 5.3 Access Cortex
```
URL: http://your-server:9001
- Create admin account
- Configure analyzers
- Add VirusTotal API key
- Test analyzer functionality
```

#### 5.4 Configure Dashboard
```bash
# API keys are loaded from .env
# Dashboard auto-connects if .env is correct

# Test connectivity
curl http://localhost:5000/api/dashboard/stats
```

## Configuration

### Alert Sources Configuration

#### Splunk Integration
```bash
# In docker/.env:
SPLUNK_URL=https://your-splunk:8089
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=password

# Verify connection:
docker-compose logs alert-collector | grep Splunk
```

#### Wazuh Integration
```bash
# In docker/.env:
WAZUH_URL=http://your-wazuh:55000
WAZUH_USERNAME=wazuh
WAZUH_PASSWORD=password

# Verify connection:
docker-compose logs alert-collector | grep Wazuh
```

### Cortex Analyzer Configuration

```bash
# Access Cortex UI
# http://your-server:9001

# Configure analyzers:
# 1. VirusTotal
# 2. Shodan
# 3. MaxMind GeoIP
# 4. URLhaus
# 5. PhishTank
```

### Response Policy Configuration

Edit `scripts/response_engine.py`:
```python
# Add custom policies:
{
    'threat_type': {
        'severity': [3, 4],
        'actions': ['action1', 'action2']
    }
}
```

## Verification

### Health Checks

#### 1. Service Health
```bash
docker-compose ps

# All should show "healthy" or "Up"
```

#### 2. Database Connectivity
```bash
# Cassandra
docker exec cassandra cqlsh cassandra -e "SELECT * FROM system.peers"

# PostgreSQL
docker exec cortex-db psql -U cortex -d cortex -c "SELECT 1"

# Elasticsearch
curl http://localhost:9200/_cluster/health
```

#### 3. API Connectivity
```bash
# TheHive
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:9000/api/v1/case

# Cortex
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:9001/api/analyzer

# Dashboard
curl http://localhost:5000/api/health
```

#### 4. Alert Collection
```bash
# Check logs
docker-compose logs alert-collector | tail -20

# Should show "Starting alert collection" every 5 minutes
```

## Production Hardening

### 1. Security Hardening

#### TLS/SSL Configuration
```bash
# Generate certificates
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Update docker-compose.yml to use HTTPS
```

#### Firewall Rules
```bash
sudo ufw enable
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 9000/tcp    # TheHive
sudo ufw allow 9001/tcp    # Cortex
sudo ufw allow 5000/tcp    # Dashboard
sudo ufw allow 55000/tcp   # Wazuh
sudo ufw deny incoming
```

#### Update Passwords
```bash
# Change all default passwords
# - TheHive admin password
# - Cassandra credentials
# - PostgreSQL credentials
# - Wazuh credentials
# - Splunk credentials
```

### 2. Data Protection

#### Enable Encryption
```yaml
# In docker-compose.yml
elasticsearch:
  environment:
    - xpack.security.enabled=true
```

#### Configure Backups
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec cassandra cqlsh -e "SELECT * FROM system" > backup_$DATE.cql
```

### 3. Monitoring & Logging

#### Enable Audit Logging
```bash
# In TheHive configuration
audit {
  enabled = true
  log {
    file = "/var/log/thehive/audit.log"
  }
}
```

#### Configure Log Aggregation
```bash
# Send logs to centralized location
# Update docker-compose.yml logging driver
```

### 4. Performance Tuning

#### JVM Heap Sizes
```yaml
thehive:
  environment:
    - JVM_OPTS=-Xms2g -Xmx4g

cortex:
  environment:
    - JVM_OPTS=-Xms1g -Xmx2g
```

#### Database Tuning
```yaml
cassandra:
  environment:
    - CASSANDRA_HEAP_SIZE=4G
    - CASSANDRA_MEMTABLE_HEAP_SPACE_IN_MB=2048
```

### 5. High Availability

#### Load Balancing
```nginx
# Configure nginx reverse proxy for HA
upstream thehive {
    server thehive1:9000;
    server thehive2:9000;
}
```

#### Database Replication
```bash
# Configure Cassandra replication
# Replication factor: 3
```

## Troubleshooting

### Common Issues

#### 1. Services Won't Start
```bash
# Check logs
docker-compose logs

# Check resource availability
docker stats

# Increase memory if needed
```

#### 2. Database Connection Errors
```bash
# Restart databases
docker-compose restart cassandra elasticsearch

# Check connectivity
docker-compose exec cassandra cqlsh cassandra
```

#### 3. API Key Issues
```bash
# Verify API key in TheHive
# Generate new key if needed
# Update .env and restart services
```

#### 4. Analyzer Jobs Failing
```bash
# Check Docker daemon
docker ps

# Check analyzer logs
docker-compose logs cortex

# Verify VirusTotal API key
```

## Support

- Documentation: `/docs/README.md`
- Logs: `docker-compose logs`
- Issue Tracking: GitHub Issues

## Next Steps

1. Configure alert sources
2. Create case templates
3. Set up response policies
4. Configure notifications
5. Plan backup strategy
6. Set up monitoring
