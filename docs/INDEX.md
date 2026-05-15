# SOC Platform - Project Index

## Project Overview
Automated SOC Incident Response Platform using TheHive, Cortex, Splunk, Wazuh, and VirusTotal

## Quick Navigation

### 📚 Documentation
- **[README](README.md)** - Main project documentation
- **[Quick Start](QUICKSTART.md)** - Get running in 5 minutes
- **[Deployment Guide](DEPLOYMENT.md)** - Complete setup instructions
- **[API Integration](API_INTEGRATION.md)** - API reference and examples

### 🔧 Directory Structure

```
TheHive/
├── config/                 # Configuration files
│   ├── thehive.conf       # TheHive config
│   ├── cortex.conf        # Cortex config
│   └── README.md          # Config guide
├── dashboards/            # Web dashboard
│   ├── app.py             # Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Dashboard container
│   ├── templates/         # HTML templates
│   ├── static/
│   │   ├── css/style.css  # Dashboard styles
│   │   └── js/dashboard.js # Dashboard JS
├── docker/                # Docker setup
│   ├── docker-compose.yml # Services definition
│   ├── .env              # Environment variables
│   └── Dockerfile.collector # Alert collector
├── docs/                  # Documentation
│   ├── README.md          # Full documentation
│   ├── QUICKSTART.md      # Quick start
│   ├── DEPLOYMENT.md      # Deployment guide
│   └── API_INTEGRATION.md # API docs
├── playbooks/             # Incident response playbooks
│   ├── malware_response.md
│   └── brute_force_response.md
└── scripts/               # Python scripts
    ├── alert_collector.py # Alert collection service
    ├── threat_enrichment.py # Threat enrichment
    ├── response_engine.py # Response automation
    └── requirements.txt   # Python dependencies
```

### 🚀 Getting Started

1. **Prerequisites**
   ```bash
   docker --version    # 20.10+
   docker-compose --version  # 2.0+
   ```

2. **Quick Start** (5 minutes)
   ```bash
   cd docker
   nano .env          # Configure
   docker-compose up -d
   ```

3. **Access Services**
   - TheHive: http://localhost:9000
   - Cortex: http://localhost:9001
   - Dashboard: http://localhost:5000

### 🔑 Key Components

| Component | Purpose | Port | Documentation |
|-----------|---------|------|-----------------|
| TheHive | Case Management | 9000 | thehive.conf |
| Cortex | Threat Intelligence | 9001 | cortex.conf |
| Dashboard | Web UI | 5000 | dashboards/app.py |
| Splunk | Alert Source | 8089 | scripts/alert_collector.py |
| Wazuh | Alert Source | 55000 | scripts/alert_collector.py |
| Cassandra | Database | 9042 | docker-compose.yml |
| Elasticsearch | Search | 9200 | docker-compose.yml |
| PostgreSQL | Cortex DB | 5432 | docker-compose.yml |
| MinIO | Storage | 9000 | docker-compose.yml |

### 📋 Features

#### Alert Collection
- Splunk integration
- Wazuh integration
- Custom alert sources
- Automatic deduplication
- Real-time processing

#### Threat Enrichment
- VirusTotal API
- Shodan integration
- MaxMind GeoIP
- URLhaus
- PhishTank
- Automatic observable enrichment

#### Automated Response
- Host isolation
- IP blocking
- File quarantine
- Account management
- Process control
- Forensic snapshot
- Log collection
- Policy-based actions

#### Web Dashboard
- Real-time statistics
- Case management
- Alert visualization
- Threat intelligence display
- Response action logging
- Analytics and reporting

### 🔗 Workflow

```
Alert Generation
       ↓
Alert Collection (Splunk/Wazuh)
       ↓
Alert to TheHive
       ↓
Observable Extraction
       ↓
Threat Enrichment (Cortex)
       ↓
Severity Assessment
       ↓
Policy Matching
       ↓
Automated Response Actions
       ↓
Logging & Notification
       ↓
Dashboard Display
       ↓
SOC Team Review
```

### 📖 Documentation Map

| Document | Purpose |
|----------|---------|
| README.md | Complete system documentation |
| QUICKSTART.md | 5-minute setup guide |
| DEPLOYMENT.md | Full deployment & production setup |
| API_INTEGRATION.md | API endpoints & integration examples |
| config/README.md | Configuration file documentation |
| playbooks/ | Incident response procedures |

### 🔐 Security

- TLS/SSL support
- API key authentication
- Database encryption (configurable)
- Audit logging
- Network segmentation
- Credential management

### 📊 Performance

- Designed for 1000+ alerts/day
- Sub-second response times
- Horizontal scalability
- Configurable resource limits
- Automatic failover (with clustering)

### 🔧 Configuration

### Minimal Setup (Development)
1. Edit `docker/.env` with API keys
2. Run `docker-compose up -d`
3. Access http://localhost:5000

### Production Setup
1. Follow [DEPLOYMENT.md](DEPLOYMENT.md)
2. Configure TLS/SSL
3. Set up monitoring
4. Configure backups
5. Enable audit logging

### 📝 API Examples

#### Create Case
```bash
curl -X POST http://localhost:9000/api/v1/case \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title": "Incident", "severity": 3}'
```

#### Get Dashboard Stats
```bash
curl http://localhost:5000/api/dashboard/stats
```

#### Run Threat Enrichment
```bash
curl -X POST http://localhost:9001/api/analyzer/VirusTotal/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"data": "hash", "dataType": "file"}'
```

### 🐛 Troubleshooting

1. **Services won't start**
   ```bash
   docker-compose logs
   docker-compose ps
   ```

2. **API key errors**
   - Regenerate in TheHive UI
   - Update .env file
   - Restart services

3. **Performance issues**
   - Check resource limits
   - Review logs
   - Tune database settings

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting.

### 📚 Learning Resources

#### TheHive
- Documentation: https://docs.thehive-project.org/
- GitHub: https://github.com/TheHive-Project/TheHive

#### Cortex
- Documentation: https://cortex-docs.readthedocs.io/
- GitHub: https://github.com/TheHive-Project/Cortex

#### Splunk
- Documentation: https://docs.splunk.com/

#### Wazuh
- Documentation: https://documentation.wazuh.com/

### 🤝 Support

- Check logs: `docker-compose logs`
- Review documentation
- Check GitHub issues
- Create issue with error details

### 📝 Changelog

See [DEPLOYMENT.md](DEPLOYMENT.md) for version-specific information.

### 📄 License

This project integrates multiple open-source and commercial tools. Refer to individual tool licenses:
- TheHive: AGPL v3
- Cortex: AGPL v3
- Splunk: Splunk License Agreement
- Wazuh: AGPL v2
- Elasticsearch: Elastic License
- PostgreSQL: PostgreSQL License

### 🎯 Next Steps

1. **Try it out**: Follow [QUICKSTART.md](QUICKSTART.md)
2. **Learn the system**: Read [README.md](README.md)
3. **Deploy to production**: Follow [DEPLOYMENT.md](DEPLOYMENT.md)
4. **Integrate APIs**: Check [API_INTEGRATION.md](API_INTEGRATION.md)
5. **Customize playbooks**: Review playbooks/ directory

### 📞 Contact

For questions or issues:
1. Check documentation
2. Review logs
3. Search GitHub issues
4. Create new issue with details

---

**Last Updated**: January 2024
**Version**: 1.0.0
**Status**: Production Ready
