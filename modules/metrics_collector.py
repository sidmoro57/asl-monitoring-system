"""
Metrics Collector Module
Collects system and application metrics
"""

import psutil
from datetime import datetime


class MetricsCollector:
    """Collects various system and application metrics"""
    
    def __init__(self, data_store):
        self.data_store = data_store
    
    def collect(self):
        """Collect all current metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': self._collect_system_metrics(),
            'cpu': self._collect_cpu_metrics(),
            'memory': self._collect_memory_metrics(),
            'disk': self._collect_disk_metrics(),
            'network': self._collect_network_metrics()
        }
        
        # Store metrics
        self.data_store.store(metrics)
        
        return metrics
    
    def _collect_system_metrics(self):
        """Collect general system metrics"""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        return {
            'boot_time': boot_time.isoformat(),
            'uptime_seconds': uptime.total_seconds(),
            'uptime_formatted': str(uptime).split('.')[0]  # Remove microseconds
        }
    
    def _collect_cpu_metrics(self):
        """Collect CPU metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        metrics = {
            'usage_percent': cpu_percent,
            'count': cpu_count,
            'count_logical': psutil.cpu_count(logical=True)
        }
        
        if cpu_freq:
            metrics.update({
                'frequency_current_mhz': cpu_freq.current,
                'frequency_min_mhz': cpu_freq.min,
                'frequency_max_mhz': cpu_freq.max
            })
        
        # Per-CPU usage
        per_cpu = psutil.cpu_percent(interval=1, percpu=True)
        metrics['per_cpu_usage'] = per_cpu
        
        return metrics
    
    def _collect_memory_metrics(self):
        """Collect memory metrics"""
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()
        
        return {
            'total_gb': round(virtual_mem.total / (1024 ** 3), 2),
            'available_gb': round(virtual_mem.available / (1024 ** 3), 2),
            'used_gb': round(virtual_mem.used / (1024 ** 3), 2),
            'usage_percent': virtual_mem.percent,
            'swap_total_gb': round(swap_mem.total / (1024 ** 3), 2),
            'swap_used_gb': round(swap_mem.used / (1024 ** 3), 2),
            'swap_percent': swap_mem.percent
        }
    
    def _collect_disk_metrics(self):
        """Collect disk metrics"""
        partitions = psutil.disk_partitions()
        disk_data = []
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_data.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total_gb': round(usage.total / (1024 ** 3), 2),
                    'used_gb': round(usage.used / (1024 ** 3), 2),
                    'free_gb': round(usage.free / (1024 ** 3), 2),
                    'usage_percent': usage.percent
                })
            except PermissionError:
                # Skip partitions we can't access
                continue
        
        # Disk I/O statistics
        disk_io = psutil.disk_io_counters()
        io_stats = {}
        if disk_io:
            io_stats = {
                'read_count': disk_io.read_count,
                'write_count': disk_io.write_count,
                'read_bytes': disk_io.read_bytes,
                'write_bytes': disk_io.write_bytes,
                'read_mb': round(disk_io.read_bytes / (1024 ** 2), 2),
                'write_mb': round(disk_io.write_bytes / (1024 ** 2), 2)
            }
        
        return {
            'partitions': disk_data,
            'io_stats': io_stats
        }
    
    def _collect_network_metrics(self):
        """Collect network metrics"""
        net_io = psutil.net_io_counters()
        
        metrics = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errors_in': net_io.errin,
            'errors_out': net_io.errout,
            'drops_in': net_io.dropin,
            'drops_out': net_io.dropout,
            'mb_sent': round(net_io.bytes_sent / (1024 ** 2), 2),
            'mb_recv': round(net_io.bytes_recv / (1024 ** 2), 2)
        }
        
        return metrics
    
    def collect_process_metrics(self, pid=None):
        """Collect metrics for a specific process"""
        if pid is None:
            # Get current process
            process = psutil.Process()
        else:
            process = psutil.Process(pid)
        
        return {
            'pid': process.pid,
            'name': process.name(),
            'status': process.status(),
            'cpu_percent': process.cpu_percent(interval=1),
            'memory_percent': process.memory_percent(),
            'memory_mb': round(process.memory_info().rss / (1024 ** 2), 2),
            'num_threads': process.num_threads(),
            'create_time': datetime.fromtimestamp(process.create_time()).isoformat()
        }
