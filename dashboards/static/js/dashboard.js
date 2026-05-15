// SOC Dashboard JavaScript

let severityChart = null;
let statusChart = null;
const API_BASE = '/api';

// Initialize dashboard on load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    loadCases();
    loadAlerts();
    loadEnrichmentJobs();
    
    // Refresh data every 30 seconds
    setInterval(loadDashboardData, 30000);
    setInterval(loadAlerts, 30000);
    
    updateTimestamp();
    setInterval(updateTimestamp, 1000);
});

// Show/Hide sections
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active class from menu items
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(sectionId).classList.add('active');
    
    // Add active class to menu item
    event.target.closest('.menu-item').classList.add('active');
}

// Load dashboard statistics
function loadDashboardData() {
    fetch(`${API_BASE}/dashboard/stats`)
        .then(response => response.json())
        .then(data => {
            // Update KPI cards
            document.getElementById('open-cases').textContent = data.open_cases || 0;
            document.getElementById('new-cases').textContent = data.new_cases || 0;
            document.getElementById('active-alerts').textContent = data.total_alerts || 0;
            document.getElementById('new-alerts').textContent = data.new_alerts || 0;
            document.getElementById('resolved-cases').textContent = data.closed_cases || 0;
            document.getElementById('mttr').textContent = data.mttr || '0';
            
            // Calculate threat score (0-100)
            const threatScore = calculateThreatScore(data);
            document.getElementById('threat-score').textContent = threatScore;
            
            // Update charts
            updateSeverityChart(data.severity_distribution);
            updateStatusChart(data);
        })
        .catch(error => console.error('Error loading dashboard data:', error));
}

// Calculate threat score based on metrics
function calculateThreatScore(data) {
    let score = 50; // Base score
    
    // Increase score based on open cases
    if (data.open_cases > 10) score += 20;
    else if (data.open_cases > 5) score += 10;
    
    // Increase score based on new alerts
    if (data.new_alerts > 5) score += 15;
    else if (data.new_alerts > 2) score += 5;
    
    // Check severity distribution
    if (data.severity_distribution['4'] > 0) score += 15;
    if (data.severity_distribution['3'] > 2) score += 10;
    
    return Math.min(score, 100);
}

// Update severity distribution chart
function updateSeverityChart(distribution) {
    const ctx = document.getElementById('severity-chart');
    if (!ctx) return;
    
    if (severityChart) {
        severityChart.destroy();
    }
    
    const labels = ['Low', 'Medium', 'High', 'Critical'];
    const data = [
        distribution['1'] || 0,
        distribution['2'] || 0,
        distribution['3'] || 0,
        distribution['4'] || 0
    ];
    
    const colors = ['#10b981', '#f59e0b', '#ef4444', '#dc2626'];
    
    severityChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Update case status chart
function updateStatusChart(data) {
    const ctx = document.getElementById('status-chart');
    if (!ctx) return;
    
    if (statusChart) {
        statusChart.destroy();
    }
    
    statusChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['New', 'In Progress', 'Resolved'],
            datasets: [{
                label: 'Cases',
                data: [
                    data.new_cases || 0,
                    (data.open_cases - data.new_cases) || 0,
                    data.closed_cases || 0
                ],
                backgroundColor: ['#3b82f6', '#f59e0b', '#10b981'],
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Load cases
function loadCases() {
    fetch(`${API_BASE}/cases?limit=50`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('cases-tbody');
            const cases = Array.isArray(data) ? data : data.data || [];
            
            if (cases.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">No cases found</td></tr>';
                return;
            }
            
            tbody.innerHTML = cases.map(caseItem => `
                <tr>
                    <td>${caseItem.id || caseItem.caseId || 'N/A'}</td>
                    <td>${caseItem.title || 'Untitled'}</td>
                    <td>
                        <span class="status-badge status-${caseItem.status?.toLowerCase() || 'new'}">
                            ${caseItem.status || 'New'}
                        </span>
                    </td>
                    <td>
                        <span class="severity-${caseItem.severity || 1}">
                            ${getSeverityLabel(caseItem.severity)}
                        </span>
                    </td>
                    <td>${formatDate(caseItem.createdAt)}</td>
                    <td>
                        <button class="btn btn-primary" onclick="viewCase('${caseItem.id || caseItem.caseId}')">
                            View
                        </button>
                    </td>
                </tr>
            `).join('');
        })
        .catch(error => {
            console.error('Error loading cases:', error);
            document.getElementById('cases-tbody').innerHTML = 
                '<tr><td colspan="6" class="text-center">Error loading cases</td></tr>';
        });
}

// Load alerts
function loadAlerts() {
    fetch(`${API_BASE}/alerts?limit=10`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('alerts-container');
            const alerts = Array.isArray(data) ? data : data.data || [];
            
            if (alerts.length === 0) {
                container.innerHTML = '<div class="text-center">No active alerts</div>';
                return;
            }
            
            container.innerHTML = alerts.map(alert => `
                <div class="alert-card ${getSeverityClass(alert.severity)}">
                    <div class="alert-title">${alert.title || 'Alert'}</div>
                    <div class="alert-meta">
                        Severity: <strong>${getSeverityLabel(alert.severity)}</strong> | 
                        ${formatDate(alert.createdAt)}
                    </div>
                    <div class="alert-description">
                        ${alert.description || alert.message || 'No description'}
                    </div>
                    <button class="btn btn-primary" style="width: 100%;">
                        Create Case
                    </button>
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Error loading alerts:', error);
            document.getElementById('alerts-container').innerHTML = 
                '<div class="text-center">Error loading alerts</div>';
        });
}

// Load enrichment jobs
function loadEnrichmentJobs() {
    fetch(`${API_BASE}/enrichment`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('jobs-tbody');
            const jobs = Array.isArray(data) ? data : data.data || [];
            
            if (jobs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No enrichment jobs</td></tr>';
                return;
            }
            
            tbody.innerHTML = jobs.slice(0, 10).map(job => `
                <tr>
                    <td>${job.id || 'N/A'}</td>
                    <td>${job.name || 'Unknown'}</td>
                    <td>${job.data || 'N/A'}</td>
                    <td>
                        <span class="status-badge ${getJobStatusClass(job.status)}">
                            ${job.status || 'Unknown'}
                        </span>
                    </td>
                    <td>${job.report ? 'Available' : 'Pending'}</td>
                </tr>
            `).join('');
        })
        .catch(error => {
            console.error('Error loading enrichment jobs:', error);
            document.getElementById('jobs-tbody').innerHTML = 
                '<tr><td colspan="5" class="text-center">Error loading jobs</td></tr>';
        });
}

// View case details
function viewCase(caseId) {
    fetch(`${API_BASE}/cases/${caseId}`)
        .then(response => response.json())
        .then(data => {
            console.log('Case details:', data);
            alert(`Case: ${data.case?.title}\n\nObservables: ${data.observables?.length || 0}`);
        })
        .catch(error => console.error('Error fetching case:', error));
}

// Filter cases
function filterCases() {
    const status = document.getElementById('status-filter').value;
    const severity = document.getElementById('severity-filter').value;
    
    const rows = document.querySelectorAll('#cases-tbody tr');
    
    rows.forEach(row => {
        let show = true;
        
        if (status && !row.textContent.includes(status)) {
            show = false;
        }
        
        if (severity && !row.innerHTML.includes(`severity-${severity}`)) {
            show = false;
        }
        
        row.style.display = show ? '' : 'none';
    });
}

// Utility functions
function getSeverityLabel(severity) {
    const labels = {
        1: 'Low',
        2: 'Medium',
        3: 'High',
        4: 'Critical'
    };
    return labels[severity] || 'Unknown';
}

function getSeverityClass(severity) {
    const classes = {
        1: 'low',
        2: 'medium',
        3: 'high',
        4: 'critical'
    };
    return classes[severity] || 'low';
}

function getJobStatusClass(status) {
    if (status === 'Success') return 'status-resolved';
    if (status === 'Failure') return 'status-new';
    if (status === 'Running') return 'status-in-progress';
    return 'status-new';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return date.toLocaleDateString();
    } catch (e) {
        return 'N/A';
    }
}

function updateTimestamp() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    const timeElement = document.getElementById('update-time');
    if (timeElement) {
        timeElement.textContent = timeString;
    }
}

// Export functions
function exportToPDF() {
    alert('PDF export functionality would be implemented here');
}

function exportToCSV() {
    alert('CSV export functionality would be implemented here');
}

function exportToJSON() {
    alert('JSON export functionality would be implemented here');
}
