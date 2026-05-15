"""
Alert Collector Service
Collects alerts from various sources (Splunk, Wazuh) and sends them to TheHive
"""

import os
import time
import logging
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
from requests.auth import HTTPBasicAuth
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/alert-collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TheHiveConnector:
    """Connector to TheHive API"""
    
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_case(self, case_data: Dict) -> Dict:
        """Create a case in TheHive"""
        try:
            response = requests.post(
                f'{self.url}/api/v1/case',
                headers=self.headers,
                json=case_data
            )
            response.raise_for_status()
            logger.info(f"Case created successfully: {response.json().get('id')}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating case: {e}")
            raise
    
    def create_alert(self, alert_data: Dict) -> Dict:
        """Create an alert in TheHive"""
        try:
            response = requests.post(
                f'{self.url}/api/v1/alert',
                headers=self.headers,
                json=alert_data
            )
            response.raise_for_status()
            logger.info(f"Alert created successfully: {response.json().get('id')}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating alert: {e}")
            raise
    
    def create_observable(self, case_id: str, observable_data: Dict) -> Dict:
        """Create an observable in a case"""
        try:
            response = requests.post(
                f'{self.url}/api/v1/case/{case_id}/observable',
                headers=self.headers,
                json=observable_data
            )
            response.raise_for_status()
            logger.info(f"Observable created successfully: {response.json().get('id')}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating observable: {e}")
            raise


class SplunkConnector:
    """Connector to Splunk Enterprise"""
    
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.auth = HTTPBasicAuth(username, password)
    
    def get_alerts(self, search_query: str, count: int = 100) -> List[Dict]:
        """Fetch alerts from Splunk using search query"""
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            
            # Create search job
            search_data = {
                'search': search_query,
                'output_mode': 'json',
                'earliest_time': '-1h'  # Last hour
            }
            
            response = requests.post(
                f'{self.url}/services/search/jobs',
                auth=self.auth,
                headers=headers,
                data=search_data,
                verify=False
            )
            response.raise_for_status()
            
            job_id = response.json()['sid']
            
            # Wait for search to complete
            time.sleep(5)
            
            # Get search results
            results_response = requests.get(
                f'{self.url}/services/search/jobs/{job_id}/results',
                auth=self.auth,
                headers=headers,
                params={'output_mode': 'json', 'count': count},
                verify=False
            )
            results_response.raise_for_status()
            
            alerts = results_response.json().get('results', [])
            logger.info(f"Retrieved {len(alerts)} alerts from Splunk")
            return alerts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching alerts from Splunk: {e}")
            return []
    
    def get_security_alerts(self) -> List[Dict]:
        """Fetch security-related alerts from Splunk"""
        query = 'index=security alert_level>=high | fields alert_id, alert_name, severity, source, dest'
        return self.get_alerts(query)


class WazuhConnector:
    """Connector to Wazuh"""
    
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password
        self.token = self._get_token()
    
    def _get_token(self) -> str:
        """Get authentication token from Wazuh"""
        try:
            response = requests.get(
                f'{self.url}/security/user/authenticate',
                auth=HTTPBasicAuth(self.username, self.password),
                verify=False
            )
            response.raise_for_status()
            return response.json().get('data', {}).get('token', '')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error authenticating with Wazuh: {e}")
            return ""
    
    def get_alerts(self, severity: int = 3) -> List[Dict]:
        """Fetch alerts from Wazuh"""
        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'{self.url}/alerts',
                headers=headers,
                params={'rule.level': severity},
                verify=False
            )
            response.raise_for_status()
            
            alerts = response.json().get('data', {}).get('affected_items', [])
            logger.info(f"Retrieved {len(alerts)} alerts from Wazuh")
            return alerts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching alerts from Wazuh: {e}")
            return []


class VirusTotalConnector:
    """Connector to VirusTotal API for threat enrichment"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.virustotal.com/api/v3"
        self.headers = {'x-apikey': api_key}
    
    def check_file(self, file_hash: str) -> Dict:
        """Check file hash on VirusTotal"""
        try:
            response = requests.get(
                f'{self.base_url}/files/{file_hash}',
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking VirusTotal: {e}")
            return {}
    
    def check_url(self, url: str) -> Dict:
        """Check URL on VirusTotal"""
        try:
            import hashlib
            url_id = hashlib.sha256(url.encode()).hexdigest()
            
            response = requests.get(
                f'{self.base_url}/urls/{url_id}',
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking VirusTotal URL: {e}")
            return {}


class AlertProcessor:
    """Process and enrich alerts before sending to TheHive"""
    
    def __init__(self, thehive: TheHiveConnector, virustotal: VirusTotalConnector):
        self.thehive = thehive
        self.virustotal = virustotal
    
    def process_splunk_alert(self, splunk_alert: Dict) -> Dict:
        """Convert Splunk alert to TheHive format"""
        try:
            case_data = {
                'title': splunk_alert.get('alert_name', 'Security Alert'),
                'description': f"Alert from Splunk: {splunk_alert.get('alert_id', 'N/A')}",
                'severity': self._map_severity(splunk_alert.get('severity')),
                'tlp': 2,
                'pap': 2,
                'status': 'New',
                'tags': ['splunk', 'automated'],
                'template': 'Security Incident'
            }
            
            # Create case
            case = self.thehive.create_case(case_data)
            
            # Create observables
            observables = [
                {
                    'dataType': 'ip',
                    'data': splunk_alert.get('source'),
                    'message': 'Source IP',
                    'tlp': 2
                },
                {
                    'dataType': 'ip',
                    'data': splunk_alert.get('dest'),
                    'message': 'Destination IP',
                    'tlp': 2
                }
            ]
            
            for observable in observables:
                if observable['data']:
                    self.thehive.create_observable(case['id'], observable)
            
            return case
            
        except Exception as e:
            logger.error(f"Error processing Splunk alert: {e}")
            raise
    
    def process_wazuh_alert(self, wazuh_alert: Dict) -> Dict:
        """Convert Wazuh alert to TheHive format"""
        try:
            alert_data = {
                'title': f"Wazuh Alert: {wazuh_alert.get('rule', {}).get('description', 'N/A')}",
                'description': json.dumps(wazuh_alert, indent=2),
                'severity': self._map_wazuh_severity(wazuh_alert.get('rule', {}).get('level', 0)),
                'tlp': 2,
                'pap': 2,
                'tags': ['wazuh', 'automated'],
                'type': 'external'
            }
            
            # Create alert
            alert = self.thehive.create_alert(alert_data)
            
            # Extract and create observables
            agent = wazuh_alert.get('agent', {})
            if agent.get('ip'):
                observable = {
                    'dataType': 'ip',
                    'data': agent['ip'],
                    'message': f"Wazuh Agent IP: {agent.get('name')}",
                    'tlp': 2
                }
                # Note: We would create observables in the case if converted to case
            
            return alert
            
        except Exception as e:
            logger.error(f"Error processing Wazuh alert: {e}")
            raise
    
    @staticmethod
    def _map_severity(severity_str: str) -> int:
        """Map Splunk severity to TheHive severity (1-4)"""
        severity_map = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1,
            'info': 1
        }
        return severity_map.get(severity_str.lower(), 1)
    
    @staticmethod
    def _map_wazuh_severity(wazuh_level: int) -> int:
        """Map Wazuh level to TheHive severity"""
        if wazuh_level >= 15:
            return 4  # Critical
        elif wazuh_level >= 9:
            return 3  # High
        elif wazuh_level >= 5:
            return 2  # Medium
        else:
            return 1  # Low


class AlertCollectorService:
    """Main alert collection service"""
    
    def __init__(self):
        # Initialize connectors
        self.thehive = TheHiveConnector(
            os.getenv('THEHIVE_URL', 'http://localhost:9000'),
            os.getenv('THEHIVE_API_KEY', '')
        )
        
        self.splunk = SplunkConnector(
            os.getenv('SPLUNK_URL', 'https://localhost:8089'),
            os.getenv('SPLUNK_USERNAME', 'admin'),
            os.getenv('SPLUNK_PASSWORD', '')
        )
        
        self.wazuh = WazuhConnector(
            os.getenv('WAZUH_URL', 'http://localhost:55000'),
            os.getenv('WAZUH_USERNAME', 'wazuh'),
            os.getenv('WAZUH_PASSWORD', '')
        )
        
        self.virustotal = VirusTotalConnector(
            os.getenv('VIRUSTOTAL_API_KEY', '')
        )
        
        self.processor = AlertProcessor(self.thehive, self.virustotal)
    
    def collect_alerts(self):
        """Collect alerts from all sources"""
        logger.info("Starting alert collection...")
        
        try:
            # Collect from Splunk
            logger.info("Collecting alerts from Splunk...")
            splunk_alerts = self.splunk.get_security_alerts()
            for alert in splunk_alerts:
                self.processor.process_splunk_alert(alert)
            
            # Collect from Wazuh
            logger.info("Collecting alerts from Wazuh...")
            wazuh_alerts = self.wazuh.get_alerts(severity=3)
            for alert in wazuh_alerts:
                self.processor.process_wazuh_alert(alert)
            
            logger.info("Alert collection completed")
            
        except Exception as e:
            logger.error(f"Error during alert collection: {e}")
    
    def start_scheduler(self):
        """Start the alert collection scheduler"""
        # Schedule alert collection every 5 minutes
        schedule.every(5).minutes.do(self.collect_alerts)
        
        logger.info("Alert collector scheduler started")
        
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    service = AlertCollectorService()
    service.start_scheduler()
