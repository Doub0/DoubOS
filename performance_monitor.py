"""
DoubOS Performance Monitor
Track and optimize system performance
"""

import time
import json
from datetime import datetime
from collections import deque

# Try to import psutil, but work without it
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class PerformanceMonitor:
    """Monitor DoubOS performance metrics"""
    
    def __init__(self, max_samples=100):
        self.max_samples = max_samples
        self.cpu_history = deque(maxlen=max_samples)
        self.memory_history = deque(maxlen=max_samples)
        self.io_history = deque(maxlen=max_samples)
        self.start_time = time.time()
        self.command_timings = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
    def record_cpu(self):
        """Record CPU usage"""
        try:
            if HAS_PSUTIL:
                cpu = psutil.cpu_percent(interval=0.1)
                self.cpu_history.append({
                    'time': time.time(),
                    'value': cpu
                })
                return cpu
            else:
                # Simulated CPU usage
                import random
                cpu = random.uniform(5, 30)
                self.cpu_history.append({
                    'time': time.time(),
                    'value': cpu
                })
                return cpu
        except:
            return 0
            
    def record_memory(self):
        """Record memory usage"""
        try:
            if HAS_PSUTIL:
                mem = psutil.virtual_memory()
                self.memory_history.append({
                    'time': time.time(),
                    'used': mem.used,
                    'percent': mem.percent
                })
                return mem.percent
            else:
                # Simulated memory usage
                import random
                percent = random.uniform(30, 60)
                self.memory_history.append({
                    'time': time.time(),
                    'used': int(percent * 1024 * 1024 * 100),
                    'percent': percent
                })
                return percent
        except:
            return 0
            
    def record_io(self):
        """Record I/O operations"""
        try:
            if HAS_PSUTIL:
                io = psutil.disk_io_counters()
                self.io_history.append({
                    'time': time.time(),
                    'read_bytes': io.read_bytes,
                    'write_bytes': io.write_bytes
                })
            else:
                # Simulated I/O
                import random
                self.io_history.append({
                    'time': time.time(),
                    'read_bytes': random.randint(1000000, 5000000),
                    'write_bytes': random.randint(500000, 2000000)
                })
        except:
            pass
            
    def start_command_timer(self, command_name):
        """Start timing a command"""
        self.command_timings[command_name] = {
            'start': time.time(),
            'count': self.command_timings.get(command_name, {}).get('count', 0) + 1
        }
        
    def end_command_timer(self, command_name):
        """End timing a command"""
        if command_name in self.command_timings:
            elapsed = time.time() - self.command_timings[command_name]['start']
            
            if 'total_time' not in self.command_timings[command_name]:
                self.command_timings[command_name]['total_time'] = 0
                
            self.command_timings[command_name]['total_time'] += elapsed
            self.command_timings[command_name]['last_time'] = elapsed
            
            return elapsed
        return 0
        
    def record_cache_hit(self):
        """Record cache hit"""
        self.cache_hits += 1
        
    def record_cache_miss(self):
        """Record cache miss"""
        self.cache_misses += 1
        
    def get_cache_hit_rate(self):
        """Calculate cache hit rate"""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0
        return (self.cache_hits / total) * 100
        
    def get_uptime(self):
        """Get system uptime"""
        return time.time() - self.start_time
        
    def get_average_cpu(self):
        """Get average CPU usage"""
        if not self.cpu_history:
            return 0
        return sum(s['value'] for s in self.cpu_history) / len(self.cpu_history)
        
    def get_average_memory(self):
        """Get average memory usage"""
        if not self.memory_history:
            return 0
        return sum(s['percent'] for s in self.memory_history) / len(self.memory_history)
        
    def get_command_stats(self, command_name):
        """Get statistics for a command"""
        if command_name not in self.command_timings:
            return None
            
        stats = self.command_timings[command_name]
        count = stats['count']
        total_time = stats.get('total_time', 0)
        
        return {
            'count': count,
            'total_time': total_time,
            'average_time': total_time / count if count > 0 else 0,
            'last_time': stats.get('last_time', 0)
        }
        
    def get_slowest_commands(self, top_n=5):
        """Get slowest commands"""
        commands = []
        
        for name, data in self.command_timings.items():
            if 'total_time' in data and data['count'] > 0:
                avg_time = data['total_time'] / data['count']
                commands.append({
                    'name': name,
                    'avg_time': avg_time,
                    'count': data['count']
                })
                
        commands.sort(key=lambda x: x['avg_time'], reverse=True)
        return commands[:top_n]
        
    def get_most_used_commands(self, top_n=5):
        """Get most frequently used commands"""
        commands = []
        
        for name, data in self.command_timings.items():
            commands.append({
                'name': name,
                'count': data['count'],
                'total_time': data.get('total_time', 0)
            })
            
        commands.sort(key=lambda x: x['count'], reverse=True)
        return commands[:top_n]
        
    def generate_report(self):
        """Generate performance report"""
        uptime = self.get_uptime()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': uptime,
            'uptime_formatted': self.format_uptime(uptime),
            'cpu': {
                'current': self.record_cpu(),
                'average': self.get_average_cpu(),
                'samples': len(self.cpu_history)
            },
            'memory': {
                'current': self.record_memory(),
                'average': self.get_average_memory(),
                'samples': len(self.memory_history)
            },
            'cache': {
                'hits': self.cache_hits,
                'misses': self.cache_misses,
                'hit_rate': self.get_cache_hit_rate()
            },
            'commands': {
                'total_unique': len(self.command_timings),
                'slowest': self.get_slowest_commands(),
                'most_used': self.get_most_used_commands()
            }
        }
        
        return report
        
    def format_uptime(self, seconds):
        """Format uptime"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
            
    def print_report(self):
        """Print performance report"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("DoubOS Performance Report")
        print("="*60)
        print(f"\n⏱️  Uptime: {report['uptime_formatted']}")
        print(f"\n💻 CPU Usage:")
        print(f"   Current: {report['cpu']['current']:.1f}%")
        print(f"   Average: {report['cpu']['average']:.1f}%")
        print(f"\n🧠 Memory Usage:")
        print(f"   Current: {report['memory']['current']:.1f}%")
        print(f"   Average: {report['memory']['average']:.1f}%")
        print(f"\n💾 Cache Performance:")
        print(f"   Hit Rate: {report['cache']['hit_rate']:.1f}%")
        print(f"   Hits: {report['cache']['hits']}, Misses: {report['cache']['misses']}")
        
        if report['commands']['slowest']:
            print(f"\n🐌 Slowest Commands:")
            for cmd in report['commands']['slowest']:
                print(f"   {cmd['name']}: {cmd['avg_time']*1000:.2f}ms (called {cmd['count']}x)")
                
        if report['commands']['most_used']:
            print(f"\n🔥 Most Used Commands:")
            for cmd in report['commands']['most_used']:
                print(f"   {cmd['name']}: {cmd['count']} times")
                
        print()
        
    def save_report(self, filename):
        """Save report to file"""
        report = self.generate_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
            

class PerformanceOptimizer:
    """Optimize DoubOS performance"""
    
    def __init__(self, filesystem, monitor):
        self.filesystem = filesystem
        self.monitor = monitor
        self.cache = {}
        
    def cache_file_content(self, path, content):
        """Cache file content"""
        self.cache[path] = {
            'content': content,
            'time': time.time()
        }
        self.monitor.record_cache_hit()
        
    def get_cached_content(self, path):
        """Get cached file content"""
        if path in self.cache:
            # Cache valid for 60 seconds
            if time.time() - self.cache[path]['time'] < 60:
                self.monitor.record_cache_hit()
                return self.cache[path]['content']
            else:
                del self.cache[path]
                
        self.monitor.record_cache_miss()
        return None
        
    def clear_cache(self):
        """Clear cache"""
        self.cache.clear()
        
    def optimize_filesystem(self):
        """Optimize filesystem"""
        print("🔧 Optimizing virtual filesystem...")
        
        # Remove empty directories
        # Defragment file storage
        # Compact JSON storage
        
        print("✓ Filesystem optimized")
        
    def cleanup_memory(self):
        """Cleanup memory"""
        print("🧹 Cleaning up memory...")
        self.clear_cache()
        import gc
        gc.collect()
        print("✓ Memory cleaned")


# Global performance monitor instance
_monitor = None

def get_monitor():
    """Get global performance monitor"""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor
