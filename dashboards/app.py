"""
SOC Dashboard - Web-based incident management and monitoring
"""

from flask import Flask, render_template, jsonify, request, session
from flask_cors import CORS
import os
import logging
from datetime import datetime, timedelta
import requests
from functools import wraps
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
CORS(app)

# Configuration
THEHIVE_URL = os.getenv('THEHIVE_URL', 'http://thehive:9000')
THEHIVE_API_KEY = os.getenv('THEHIVE_API_KEY', '')
CORTEX_URL = os.getenv('CORTEX_URL', 'http://cortex:9001')
CORTEX_API_KEY = os.getenv('CORTEX_API_KEY', '')
WAZUH_URL = os.getenv('WAZUH_URL', 'http://wazuh:55000')


class TheHiveAPI:
    """Wrapper for TheHive API"""
    
    def __init__(self, url, api_key):
        self.url = url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_cases(self, limit=100):
        """Get recent cases"""
        try:
            response = requests.get(
                f'{self.url}/api/v1/case',
                headers=self.headers,
                params={'limit': limit, 'sort': '-createdAt'}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching cases: {e}")
            return []
    
    def get_alerts(self, limit=100):
        """Get recent alerts"""
        try:
            response = requests.get(
                f'{self.url}/api/v1/alert',
                headers=self.headers,
                params={'limit': limit, 'sort': '-createdAt'}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return []
    
    def get_case_details(self, case_id):
        """Get detailed information about a case"""
        try:
            response = requests.get(
                f'{self.url}/api/v1/case/{case_id}',
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching case details: {e}")
            return None
    
    def get_observables(self, case_id):
        """Get observables for a case"""
        try:
            response = requests.get(
                f'{self.url}/api/v1/case/{case_id}/observable',
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching observables: {e}")
            return []
    
    def update_case_status(self, case_id, status):
        """Update case status"""
        try:
            response = requests.patch(
                f'{self.url}/api/v1/case/{case_id}',
                headers=self.headers,
                json={'status': status}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error updating case status: {e}")
            return None


class CortexAPI:
    """Wrapper for Cortex API"""
    
    def __init__(self, url, api_key):
        self.url = url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_jobs(self, limit=100):
        """Get recent analyzer jobs"""
        try:
            response = requests.get(
                f'{self.url}/api/job',
                headers=self.headers,
                params={'limit': limit}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching jobs: {e}")
            return []


# Initialize API clients
thehive = TheHiveAPI(THEHIVE_URL, THEHIVE_API_KEY)
cortex = CortexAPI(CORTEX_URL, CORTEX_API_KEY)


# Dashboard routes
@app.route('/')
def index():
    """Dashboard home page"""
    return render_template('index.html')


@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        cases = thehive.get_cases(limit=1000)
        alerts = thehive.get_alerts(limit=1000)
        
        # Calculate statistics
        case_list = cases if isinstance(cases, list) else []
        alert_list = alerts if isinstance(alerts, list) else []
        
        new_cases = len([c for c in case_list if c.get('status') == 'New'])
        open_cases = len([c for c in case_list if c.get('status') in ['New', 'InProgress']])
        closed_cases = len([c for c in case_list if c.get('status') == 'Resolved'])
        
        new_alerts = len([a for a in alert_list if a.get('status') == 'New'])
        
        # Severity distribution
        severity_dist = {
            '1': len([c for c in case_list if c.get('severity') == 1]),
            '2': len([c for c in case_list if c.get('severity') == 2]),
            '3': len([c for c in case_list if c.get('severity') == 3]),
            '4': len([c for c in case_list if c.get('severity') == 4])
        }
        
        stats = {
            'total_cases': len(case_list),
            'new_cases': new_cases,
            'open_cases': open_cases,
            'closed_cases': closed_cases,
            'total_alerts': len(alert_list),
            'new_alerts': new_alerts,
            'severity_distribution': severity_dist,
            'mttr': calculate_mttr(case_list)
        }
        
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Error calculating dashboard stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cases')
def get_cases():
    """Get all cases"""
    try:
        limit = request.args.get('limit', 100, type=int)
        cases = thehive.get_cases(limit=limit)
        return jsonify(cases if isinstance(cases, list) else [])
    except Exception as e:
        logger.error(f"Error fetching cases: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cases/<case_id>')
def get_case(case_id):
    """Get case details"""
    try:
        case = thehive.get_case_details(case_id)
        observables = thehive.get_observables(case_id)
        
        return jsonify({
            'case': case,
            'observables': observables if isinstance(observables, list) else []
        })
    except Exception as e:
        logger.error(f"Error fetching case details: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cases/<case_id>/status', methods=['PATCH'])
def update_case_status(case_id):
    """Update case status"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        result = thehive.update_case_status(case_id, status)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error updating case status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts')
def get_alerts():
    """Get all alerts"""
    try:
        limit = request.args.get('limit', 100, type=int)
        alerts = thehive.get_alerts(limit=limit)
        return jsonify(alerts if isinstance(alerts, list) else [])
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/enrichment')
def get_enrichment_jobs():
    """Get threat enrichment jobs"""
    try:
        jobs = cortex.get_jobs(limit=50)
        return jsonify(jobs if isinstance(jobs, list) else [])
    except Exception as e:
        logger.error(f"Error fetching enrichment jobs: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/timeline')
def get_timeline():
    """Get incident timeline"""
    try:
        cases = thehive.get_cases(limit=1000)
        case_list = cases if isinstance(cases, list) else []
        
        timeline = []
        for case in case_list:
            timeline.append({
                'id': case.get('id'),
                'title': case.get('title'),
                'date': case.get('createdAt'),
                'severity': case.get('severity'),
                'status': case.get('status')
            })
        
        return jsonify(sorted(timeline, key=lambda x: x['date'], reverse=True))
    except Exception as e:
        logger.error(f"Error fetching timeline: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


def calculate_mttr(cases):
    """Calculate Mean Time To Resolve"""
    try:
        resolved_cases = [c for c in cases if c.get('status') == 'Resolved']
        
        if not resolved_cases:
            return 0
        
        total_time = 0
        for case in resolved_cases:
            created = datetime.fromisoformat(case.get('createdAt', '').replace('Z', '+00:00'))
            resolved = datetime.fromisoformat(case.get('updatedAt', '').replace('Z', '+00:00'))
            total_time += (resolved - created).total_seconds()
        
        # Return MTTR in hours
        return round(total_time / (len(resolved_cases) * 3600), 2)
    except:
        return 0

@app.route('/health')
def health():
    return {'status': 'ok'}, 200


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
