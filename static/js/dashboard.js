// Dashboard JavaScript - Real-time monitoring
let autoRefresh = true;
let refreshInterval = 5000; // 5 seconds
let refreshTimer = null;
let monitoringActive = true;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('ASL Monitoring Dashboard initialized');
    
    // Set up event listeners
    document.getElementById('refresh-btn').addEventListener('click', fetchMetrics);
    document.getElementById('toggle-monitoring-btn').addEventListener('click', toggleMonitoring);
    document.getElementById('auto-refresh-toggle').addEventListener('change', function(e) {
        autoRefresh = e.target.checked;
        if (autoRefresh) {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });
    
    // Initial data fetch
    fetchMetrics();
    fetchAlerts();
    
    // Start auto-refresh
    startAutoRefresh();
});

function startAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }
    refreshTimer = setInterval(() => {
        if (autoRefresh) {
            fetchMetrics();
            fetchAlerts();
        }
    }, refreshInterval);
}

function stopAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
    }
}

async function fetchMetrics() {
    try {
        const response = await fetch('/api/metrics/current');
        const result = await response.json();
        
        if (result.success) {
            updateDashboard(result.data);
            updateLastUpdateTime();
            updateStatus('online');
        } else {
            console.error('Failed to fetch metrics:', result.error);
            updateStatus('error');
        }
    } catch (error) {
        console.error('Error fetching metrics:', error);
        updateStatus('error');
    }
}

async function fetchAlerts() {
    try {
        const response = await fetch('/api/alerts/history?limit=10');
        const result = await response.json();
        
        if (result.success) {
            updateAlerts(result.data);
        }
    } catch (error) {
        console.error('Error fetching alerts:', error);
    }
}

function updateDashboard(metrics) {
    // Update CPU metrics
    if (metrics.cpu) {
        const cpuUsage = metrics.cpu.usage_percent;
        document.getElementById('cpu-usage').textContent = cpuUsage.toFixed(1);
        document.getElementById('cpu-count').textContent = `${metrics.cpu.count} cores`;
        
        if (metrics.cpu.frequency_current_mhz) {
            document.getElementById('cpu-freq').textContent = 
                `${(metrics.cpu.frequency_current_mhz / 1000).toFixed(2)} GHz`;
        } else {
            document.getElementById('cpu-freq').textContent = 'N/A';
        }
        
        // Update progress bar
        const cpuProgress = document.getElementById('cpu-progress');
        cpuProgress.style.width = `${cpuUsage}%`;
        updateProgressColor(cpuProgress, cpuUsage);
        
        // Update status badge
        updateStatusBadge('cpu-status', cpuUsage);
    }
    
    // Update memory metrics
    if (metrics.memory) {
        const memUsage = metrics.memory.usage_percent;
        document.getElementById('memory-usage').textContent = memUsage.toFixed(1);
        document.getElementById('memory-used').textContent = `${metrics.memory.used_gb} GB`;
        document.getElementById('memory-available').textContent = `${metrics.memory.available_gb} GB`;
        document.getElementById('memory-total').textContent = `${metrics.memory.total_gb} GB`;
        
        // Update progress bar
        const memProgress = document.getElementById('memory-progress');
        memProgress.style.width = `${memUsage}%`;
        updateProgressColor(memProgress, memUsage);
        
        // Update status badge
        updateStatusBadge('memory-status', memUsage);
    }
    
    // Update disk metrics
    if (metrics.disk && metrics.disk.partitions) {
        const diskContainer = document.getElementById('disk-partitions');
        diskContainer.innerHTML = '';
        
        metrics.disk.partitions.forEach(partition => {
            const partitionDiv = document.createElement('div');
            partitionDiv.className = 'disk-partition';
            
            const header = document.createElement('div');
            header.className = 'partition-header';
            header.innerHTML = `
                <span>${partition.mountpoint}</span>
                <span>${partition.usage_percent.toFixed(1)}%</span>
            `;
            
            const details = document.createElement('div');
            details.className = 'metric-details';
            details.innerHTML = `
                <div class="detail-row">
                    <span>Used:</span>
                    <span>${partition.used_gb} GB</span>
                </div>
                <div class="detail-row">
                    <span>Free:</span>
                    <span>${partition.free_gb} GB</span>
                </div>
                <div class="detail-row">
                    <span>Total:</span>
                    <span>${partition.total_gb} GB</span>
                </div>
            `;
            
            const progressBar = document.createElement('div');
            progressBar.className = 'progress-bar';
            const progressFill = document.createElement('div');
            progressFill.className = 'progress-fill';
            progressFill.style.width = `${partition.usage_percent}%`;
            updateProgressColor(progressFill, partition.usage_percent);
            progressBar.appendChild(progressFill);
            
            partitionDiv.appendChild(header);
            partitionDiv.appendChild(details);
            partitionDiv.appendChild(progressBar);
            diskContainer.appendChild(partitionDiv);
        });
        
        // Update disk status based on highest usage
        const maxDiskUsage = Math.max(...metrics.disk.partitions.map(p => p.usage_percent));
        updateStatusBadge('disk-status', maxDiskUsage);
    }
    
    // Update network metrics
    if (metrics.network) {
        document.getElementById('network-sent').textContent = `${metrics.network.mb_sent} MB`;
        document.getElementById('network-recv').textContent = `${metrics.network.mb_recv} MB`;
        document.getElementById('packets-sent').textContent = metrics.network.packets_sent.toLocaleString();
        document.getElementById('packets-recv').textContent = metrics.network.packets_recv.toLocaleString();
    }
    
    // Update system info
    if (metrics.system) {
        document.getElementById('system-uptime').textContent = metrics.system.uptime_formatted;
        const bootTime = new Date(metrics.system.boot_time);
        document.getElementById('boot-time').textContent = bootTime.toLocaleString();
    }
}

function updateAlerts(alerts) {
    const container = document.getElementById('alerts-container');
    const countBadge = document.getElementById('alert-count');
    
    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<p class="no-alerts">No recent alerts</p>';
        countBadge.textContent = '0';
        return;
    }
    
    countBadge.textContent = alerts.length;
    container.innerHTML = '';
    
    // Show most recent alerts first
    alerts.reverse().forEach(alert => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert-item ${alert.severity}`;
        
        const alertTime = new Date(alert.timestamp);
        alertDiv.innerHTML = `
            <div><strong>${alert.metric}</strong></div>
            <div>${alert.message}</div>
            <div class="alert-time">${alertTime.toLocaleString()}</div>
        `;
        
        container.appendChild(alertDiv);
    });
}

function updateProgressColor(element, value) {
    element.classList.remove('warning', 'danger');
    if (value >= 90) {
        element.classList.add('danger');
    } else if (value >= 75) {
        element.classList.add('warning');
    }
}

function updateStatusBadge(elementId, value) {
    const badge = document.getElementById(elementId);
    badge.classList.remove('badge-success', 'badge-warning', 'badge-danger');
    
    if (value >= 90) {
        badge.classList.add('badge-danger');
        badge.textContent = 'Critical';
    } else if (value >= 75) {
        badge.classList.add('badge-warning');
        badge.textContent = 'Warning';
    } else {
        badge.classList.add('badge-success');
        badge.textContent = 'Normal';
    }
}

function updateLastUpdateTime() {
    const now = new Date();
    document.getElementById('last-update').textContent = 
        `Last update: ${now.toLocaleTimeString()}`;
}

function updateStatus(status) {
    const indicator = document.getElementById('status-indicator');
    indicator.classList.remove('online', 'offline', 'error');
    
    if (status === 'online') {
        indicator.classList.add('online');
        indicator.textContent = '● Online';
    } else if (status === 'error') {
        indicator.classList.add('error');
        indicator.textContent = '● Error';
    } else {
        indicator.classList.add('offline');
        indicator.textContent = '● Offline';
    }
}

async function toggleMonitoring() {
    const btn = document.getElementById('toggle-monitoring-btn');
    
    try {
        const endpoint = monitoringActive ? '/api/monitoring/stop' : '/api/monitoring/start';
        const response = await fetch(endpoint, { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            monitoringActive = !monitoringActive;
            btn.textContent = monitoringActive ? '⏸️ Pause Monitoring' : '▶️ Resume Monitoring';
            console.log(result.message);
        }
    } catch (error) {
        console.error('Error toggling monitoring:', error);
    }
}
