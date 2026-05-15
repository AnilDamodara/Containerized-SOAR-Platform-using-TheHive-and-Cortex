"""
Threat Enrichment Service
Uses Cortex to enrich alerts with threat intelligence
"""

import os
import logging
import json
import requests
from typing import Dict, List, Any
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CortexConnector:
    """Connector to Cortex threat intelligence platform"""
    
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_analyzers(self) -> List[Dict]:
        """Get list of available analyzers"""
        try:
            response = requests.get(
                f'{self.url}/api/analyzer',
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching analyzers: {e}")
            return []
    
    def run_analyzer(self, analyzer_name: str, data_type: str, data: str) -> Dict:
        """Run an analyzer on observable data"""
        try:
            payload = {
                'data': data,
                'dataType': data_type,
                'tlp': 2,
                'pap': 2
            }
            
            response = requests.post(
                f'{self.url}/api/analyzer/{analyzer_name}/run',
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            job_id = response.json().get('id')
            logger.info(f"Analyzer job started: {job_id}")
            
            # Wait for job to complete
            return self.wait_for_job(job_id)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error running analyzer: {e}")
            return {}
    
    def wait_for_job(self, job_id: str, timeout: int = 300) -> Dict:
        """Wait for analyzer job to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(
                    f'{self.url}/api/job/{job_id}',
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get('status') in ['Success', 'Failure']:
                    return result
                
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error checking job status: {e}")
                return {}
        
        logger.warning(f"Job {job_id} timed out")
        return {}
    
    def get_job_result(self, job_id: str) -> Dict:
        """Get result of a completed job"""
        try:
            response = requests.get(
                f'{self.url}/api/job/{job_id}/result',
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching job result: {e}")
            return {}


class ThreatEnricher:
    """Enriches observables with threat intelligence"""
    
    def __init__(self, cortex: CortexConnector):
        self.cortex = cortex
        self.enrichment_cache = {}
    
    def enrich_observable(self, data_type: str, data: str) -> Dict:
        """Enrich an observable with threat intelligence"""
        cache_key = f"{data_type}:{data}"
        
        # Check cache first
        if cache_key in self.enrichment_cache:
            logger.info(f"Using cached enrichment for {data}")
            return self.enrichment_cache[cache_key]
        
        logger.info(f"Enriching {data_type}: {data}")
        
        # Select appropriate analyzers based on data type
        analyzers = self._get_analyzers_for_type(data_type)
        enrichment_results = {}
        
        for analyzer in analyzers:
            logger.info(f"Running {analyzer} analyzer...")
            result = self.cortex.run_analyzer(analyzer, data_type, data)
            
            if result.get('status') == 'Success':
                enrichment_results[analyzer] = result.get('report', {})
        
        # Cache the results
        self.enrichment_cache[cache_key] = enrichment_results
        
        return enrichment_results
    
    def enrich_ip(self, ip: str) -> Dict:
        """Enrich IP address"""
        return self.enrich_observable('ip', ip)
    
    def enrich_file(self, file_hash: str) -> Dict:
        """Enrich file hash"""
        return self.enrich_observable('file', file_hash)
    
    def enrich_url(self, url: str) -> Dict:
        """Enrich URL"""
        return self.enrich_observable('url', url)
    
    def enrich_domain(self, domain: str) -> Dict:
        """Enrich domain"""
        return self.enrich_observable('domain', domain)
    
    def enrich_email(self, email: str) -> Dict:
        """Enrich email address"""
        return self.enrich_observable('email', email)
    
    @staticmethod
    def _get_analyzers_for_type(data_type: str) -> List[str]:
        """Get list of analyzers for a specific data type"""
        analyzers = {
            'ip': ['MaxMind_GeoIP', 'Shodan', 'Virustotal'],
            'file': ['File_Info_Details', 'File_Type_Magic', 'Virustotal'],
            'url': ['URLhaus', 'Virustotal', 'PhishTank'],
            'domain': ['Virustotal', 'Shodan'],
            'email': ['PhishTank']
        }
        return analyzers.get(data_type, [])
    
    def generate_enrichment_report(self, enrichment: Dict) -> str:
        """Generate a human-readable enrichment report"""
        report = "=== Threat Enrichment Report ===\n"
        
        for analyzer, data in enrichment.items():
            report += f"\n{analyzer}:\n"
            
            if isinstance(data, dict):
                for key, value in data.items():
                    if not isinstance(value, (dict, list)):
                        report += f"  {key}: {value}\n"
            else:
                report += f"  {str(data)[:500]}\n"
        
        return report


class ResponderAutomation:
    """Automated response based on enrichment"""
    
    def __init__(self, cortex: CortexConnector):
        self.cortex = cortex
    
    def get_responders(self) -> List[Dict]:
        """Get available responders"""
        try:
            response = requests.get(
                f'{self.cortex.url}/api/responder',
                headers=self.cortex.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching responders: {e}")
            return []
    
    def execute_responder(self, responder_name: str, observable_id: str) -> Dict:
        """Execute a responder action"""
        try:
            payload = {
                'observableId': observable_id
            }
            
            response = requests.post(
                f'{self.cortex.url}/api/responder/{responder_name}/run',
                headers=self.cortex.headers,
                json=payload
            )
            response.raise_for_status()
            logger.info(f"Responder {responder_name} executed")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error executing responder: {e}")
            return {}
    
    def determine_response(self, enrichment: Dict, severity: int) -> List[str]:
        """Determine appropriate automated responses based on enrichment and severity"""
        actions = []
        
        # Check for malicious indicators
        for analyzer, data in enrichment.items():
            if isinstance(data, dict):
                # Check detection ratios
                if 'positives' in data:
                    positives = data.get('positives', 0)
                    total = data.get('total', 1)
                    
                    if positives > 0:
                        detection_ratio = positives / total
                        
                        if detection_ratio > 0.5:  # More than 50% detected as malicious
                            if severity >= 3:
                                actions.append('block_ip')
                                actions.append('isolate_host')
                            else:
                                actions.append('alert_security_team')
                        elif detection_ratio > 0.1:
                            actions.append('monitor_closely')
        
        return list(set(actions))  # Remove duplicates


class ThreatEnrichmentService:
    """Main threat enrichment service"""
    
    def __init__(self):
        self.cortex = CortexConnector(
            os.getenv('CORTEX_URL', 'http://localhost:9001'),
            os.getenv('CORTEX_API_KEY', '')
        )
        self.enricher = ThreatEnricher(self.cortex)
        self.responder = ResponderAutomation(self.cortex)
    
    def process_case(self, case_id: str, observables: List[Dict]) -> Dict:
        """Process a case and enrich all observables"""
        enrichment_results = {}
        
        logger.info(f"Processing case {case_id} with {len(observables)} observables")
        
        for observable in observables:
            data_type = observable.get('dataType')
            data = observable.get('data')
            
            enrichment = self.enricher.enrich_observable(data_type, data)
            enrichment_results[data] = enrichment
            
            # Generate report
            report = self.enricher.generate_enrichment_report(enrichment)
            logger.info(f"Enrichment report for {data}:\n{report}")
        
        return enrichment_results


if __name__ == '__main__':
    service = ThreatEnrichmentService()
    logger.info("Threat Enrichment Service initialized")
