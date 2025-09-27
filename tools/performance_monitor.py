#!/usr/bin/env python3
"""
Real-time Satellite Network Performance Monitor

This tool provides continuous monitoring of satellite network performance,
including bandwidth, latency, packet loss, and connection quality metrics.
"""

import subprocess
import time
import json
import argparse
import threading
import queue
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import psutil
import speedtest
import socket

@dataclass
class PerformanceMetrics:
    """Network performance metrics at a point in time"""
    timestamp: float
    target: str
    rtt_ms: float
    packet_loss_percent: float
    jitter_ms: float
    download_mbps: Optional[float]
    upload_mbps: Optional[float]
    bandwidth_utilization: float
    connection_quality: str
    satellite_type: str

@dataclass
class AlertThreshold:
    """Performance alert thresholds"""
    max_rtt_ms: float = 1000.0
    max_packet_loss_percent: float = 5.0
    max_jitter_ms: float = 50.0
    min_download_mbps: float = 1.0
    min_upload_mbps: float = 0.5

class SatellitePerformanceMonitor:
    """Real-time satellite network performance monitor"""
    
    def __init__(self, targets: List[str], alert_thresholds: AlertThreshold = None):
        self.targets = targets
        self.alert_thresholds = alert_thresholds or AlertThreshold()
        self.metrics_history = {target: deque(maxlen=1000) for target in targets}
        self.monitoring_active = False
        self.alert_queue = queue.Queue()
        
        # Performance tracking
        self.bandwidth_history = deque(maxlen=100)
        self.connection_stats = {}
        
        # Initialize speedtest client
        try:
            self.speedtest_client = speedtest.Speedtest()
        except:
            self.speedtest_client = None
            print("Warning: Speedtest client not available")
    
    def start_monitoring(self, interval: int = 30, duration: int = 3600):
        """Start continuous performance monitoring"""
        
        print(f"Starting satellite network performance monitoring")
        print(f"Targets: {self.targets}")
        print(f"Interval: {interval}s, Duration: {duration}s")
        print(f"Alert thresholds: RTT<{self.alert_thresholds.max_rtt_ms}ms, "
              f"Loss<{self.alert_thresholds.max_packet_loss_percent}%")
        print("-" * 80)
        
        self.monitoring_active = True
        
        # Start monitoring threads
        monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval, duration)
        )
        
        alert_thread = threading.Thread(
            target=self._alert_processor
        )
        
        bandwidth_thread = threading.Thread(
            target=self._bandwidth_monitor,
            args=(300,)  # Every 5 minutes
        )
        
        monitor_thread.start()
        alert_thread.start()
        bandwidth_thread.start()
        
        try:
            monitor_thread.join()
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            self.monitoring_active = False
        
        alert_thread.join()
        bandwidth_thread.join()
        
        self._generate_performance_report()
    
    def _monitoring_loop(self, interval: int, duration: int):
        """Main monitoring loop"""
        
        start_time = time.time()
        iteration = 0
        
        while self.monitoring_active and (time.time() - start_time) < duration:
            iteration += 1
            
            print(f"\n--- Monitoring Iteration {iteration} ---")
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Monitor each target
            for target in self.targets:
                metrics = self._collect_metrics(target)
                if metrics:
                    self.metrics_history[target].append(metrics)
                    self._check_alerts(metrics)
                    self._print_real_time_metrics(metrics)
            
            # Sleep until next interval
            time.sleep(interval)
        
        self.monitoring_active = False
    
    def _collect_metrics(self, target: str) -> Optional[PerformanceMetrics]:
        """Collect performance metrics for a target"""
        
        try:
            # Measure RTT and packet loss with ping
            rtt, packet_loss, jitter = self._measure_ping_metrics(target)
            
            # Classify satellite type based on RTT
            satellite_type = self._classify_satellite_type(rtt)
            
            # Determine connection quality
            connection_quality = self._assess_connection_quality(rtt, packet_loss, jitter)
            
            # Get bandwidth utilization
            bandwidth_util = self._get_bandwidth_utilization()
            
            # Get speed test results (less frequently)
            download_mbps, upload_mbps = self._get_speed_metrics(target)
            
            return PerformanceMetrics(
                timestamp=time.time(),
                target=target,
                rtt_ms=rtt,
                packet_loss_percent=packet_loss,
                jitter_ms=jitter,
                download_mbps=download_mbps,
                upload_mbps=upload_mbps,
                bandwidth_utilization=bandwidth_util,
                connection_quality=connection_quality,
                satellite_type=satellite_type
            )
            
        except Exception as e:
            print(f"Error collecting metrics for {target}: {e}")
            return None
    
    def _measure_ping_metrics(self, target: str, count: int = 10) -> Tuple[float, float, float]:
        """Measure ping-based metrics (RTT, packet loss, jitter)"""
        
        try:
            result = subprocess.run(
                ['ping', '-c', str(count), target],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Parse RTT statistics
                rtt_line = [line for line in output.split('\n') if 'min/avg/max' in line]
                if rtt_line:
                    stats = rtt_line[0].split('=')[1].strip()
                    min_rtt, avg_rtt, max_rtt, mdev = map(float, stats.split('/'))
                    jitter = mdev  # mdev is a measure of jitter
                else:
                    avg_rtt = 0.0
                    jitter = 0.0
                
                # Parse packet loss
                loss_line = [line for line in output.split('\n') if 'packet loss' in line]
                if loss_line:
                    loss_str = loss_line[0].split(',')[2].strip()
                    packet_loss = float(loss_str.split('%')[0])
                else:
                    packet_loss = 0.0
                
                return avg_rtt, packet_loss, jitter
            
            else:
                # Ping failed - assume 100% packet loss
                return 0.0, 100.0, 0.0
                
        except Exception as e:
            print(f"Error measuring ping metrics: {e}")
            return 0.0, 100.0, 0.0
    
    def _classify_satellite_type(self, rtt: float) -> str:
        """Classify satellite type based on RTT"""
        
        if rtt >= 500:
            return 'GEO'
        elif rtt >= 100:
            return 'MEO'
        elif rtt >= 20:
            return 'LEO'
        else:
            return 'Terrestrial'
    
    def _assess_connection_quality(self, rtt: float, packet_loss: float, jitter: float) -> str:
        """Assess overall connection quality"""
        
        # Quality scoring based on multiple factors
        quality_score = 100
        
        # RTT impact
        if rtt > 1000:
            quality_score -= 40
        elif rtt > 500:
            quality_score -= 20
        elif rtt > 200:
            quality_score -= 10
        
        # Packet loss impact
        quality_score -= packet_loss * 5
        
        # Jitter impact
        if jitter > 50:
            quality_score -= 20
        elif jitter > 20:
            quality_score -= 10
        
        # Classify quality
        if quality_score >= 80:
            return 'Excellent'
        elif quality_score >= 60:
            return 'Good'
        elif quality_score >= 40:
            return 'Fair'
        elif quality_score >= 20:
            return 'Poor'
        else:
            return 'Critical'
    
    def _get_bandwidth_utilization(self) -> float:
        """Get current bandwidth utilization"""
        
        try:
            # Get network interface statistics
            net_io = psutil.net_io_counters()
            
            # Calculate utilization (simplified)
            # This would need baseline measurements for accuracy
            current_time = time.time()
            
            if hasattr(self, '_last_net_check'):
                time_delta = current_time - self._last_net_check
                bytes_delta = net_io.bytes_sent + net_io.bytes_recv - self._last_net_bytes
                
                # Convert to Mbps
                mbps = (bytes_delta * 8) / (time_delta * 1000000)
                utilization = min(100, (mbps / 100) * 100)  # Assume 100Mbps max
                
                self._last_net_check = current_time
                self._last_net_bytes = net_io.bytes_sent + net_io.bytes_recv
                
                return utilization
            else:
                self._last_net_check = current_time
                self._last_net_bytes = net_io.bytes_sent + net_io.bytes_recv
                return 0.0
                
        except Exception as e:
            return 0.0
    
    def _get_speed_metrics(self, target: str) -> Tuple[Optional[float], Optional[float]]:
        """Get download/upload speed metrics (cached to avoid frequent tests)"""
        
        current_time = time.time()
        
        # Only run speed test every 10 minutes
        if (target not in self.connection_stats or 
            current_time - self.connection_stats.get(target, {}).get('last_speed_test', 0) > 600):
            
            try:
                if self.speedtest_client:
                    print(f"Running speed test for {target}...")
                    
                    # Configure speedtest
                    self.speedtest_client.get_best_server()
                    
                    # Measure download speed
                    download_bps = self.speedtest_client.download()
                    download_mbps = download_bps / 1000000
                    
                    # Measure upload speed
                    upload_bps = self.speedtest_client.upload()
                    upload_mbps = upload_bps / 1000000
                    
                    # Cache results
                    self.connection_stats[target] = {
                        'last_speed_test': current_time,
                        'download_mbps': download_mbps,
                        'upload_mbps': upload_mbps
                    }
                    
                    return download_mbps, upload_mbps
                
            except Exception as e:
                print(f"Speed test failed: {e}")
        
        # Return cached values if available
        if target in self.connection_stats:
            stats = self.connection_stats[target]
            return stats.get('download_mbps'), stats.get('upload_mbps')
        
        return None, None
    
    def _check_alerts(self, metrics: PerformanceMetrics):
        """Check metrics against alert thresholds"""
        
        alerts = []
        
        if metrics.rtt_ms > self.alert_thresholds.max_rtt_ms:
            alerts.append(f"High RTT: {metrics.rtt_ms:.1f}ms")
        
        if metrics.packet_loss_percent > self.alert_thresholds.max_packet_loss_percent:
            alerts.append(f"High packet loss: {metrics.packet_loss_percent:.1f}%")
        
        if metrics.jitter_ms > self.alert_thresholds.max_jitter_ms:
            alerts.append(f"High jitter: {metrics.jitter_ms:.1f}ms")
        
        if (metrics.download_mbps and 
            metrics.download_mbps < self.alert_thresholds.min_download_mbps):
            alerts.append(f"Low download speed: {metrics.download_mbps:.1f}Mbps")
        
        if (metrics.upload_mbps and 
            metrics.upload_mbps < self.alert_thresholds.min_upload_mbps):
            alerts.append(f"Low upload speed: {metrics.upload_mbps:.1f}Mbps")
        
        if alerts:
            alert_data = {
                'timestamp': datetime.fromtimestamp(metrics.timestamp),
                'target': metrics.target,
                'alerts': alerts,
                'metrics': metrics
            }
            self.alert_queue.put(alert_data)
    
    def _print_real_time_metrics(self, metrics: PerformanceMetrics):
        """Print real-time metrics"""
        
        print(f"Target: {metrics.target}")
        print(f"  RTT: {metrics.rtt_ms:6.1f}ms | Loss: {metrics.packet_loss_percent:4.1f}% | "
              f"Jitter: {metrics.jitter_ms:5.1f}ms")
        print(f"  Quality: {metrics.connection_quality:10} | Type: {metrics.satellite_type:12} | "
              f"Util: {metrics.bandwidth_utilization:4.1f}%")
        
        if metrics.download_mbps and metrics.upload_mbps:
            print(f"  Speed: ↓{metrics.download_mbps:6.1f}Mbps ↑{metrics.upload_mbps:6.1f}Mbps")
    
    def _alert_processor(self):
        """Process and log alerts"""
        
        alert_log = []
        
        while self.monitoring_active:
            try:
                alert = self.alert_queue.get(timeout=1)
                alert_log.append(alert)
                
                # Print alert
                timestamp = alert['timestamp'].strftime('%H:%M:%S')
                print(f"\n🚨 ALERT [{timestamp}] {alert['target']}: {', '.join(alert['alerts'])}")
                
                # Log to file
                with open('satellite_alerts.log', 'a') as f:
                    f.write(f"{alert['timestamp'].isoformat()} - {alert['target']}: "
                           f"{', '.join(alert['alerts'])}\n")
                
            except queue.Empty:
                continue
    
    def _bandwidth_monitor(self, interval: int):
        """Monitor bandwidth usage trends"""
        
        while self.monitoring_active:
            try:
                net_io = psutil.net_io_counters()
                
                bandwidth_data = {
                    'timestamp': time.time(),
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
                
                self.bandwidth_history.append(bandwidth_data)
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"Error monitoring bandwidth: {e}")
                time.sleep(interval)
    
    def _generate_performance_report(self):
        """Generate comprehensive performance report"""
        
        print("\n" + "=" * 80)
        print("SATELLITE NETWORK PERFORMANCE REPORT")
        print("=" * 80)
        
        for target in self.targets:
            if not self.metrics_history[target]:
                continue
            
            metrics_list = list(self.metrics_history[target])
            
            print(f"\nTarget: {target}")
            print("-" * 40)
            
            # Calculate statistics
            rtts = [m.rtt_ms for m in metrics_list if m.rtt_ms > 0]
            losses = [m.packet_loss_percent for m in metrics_list]
            jitters = [m.jitter_ms for m in metrics_list]
            
            if rtts:
                print(f"RTT Statistics:")
                print(f"  Min:     {min(rtts):8.1f} ms")
                print(f"  Max:     {max(rtts):8.1f} ms")
                print(f"  Average: {statistics.mean(rtts):8.1f} ms")
                print(f"  Median:  {statistics.median(rtts):8.1f} ms")
                
                if len(rtts) > 1:
                    print(f"  Std Dev: {statistics.stdev(rtts):8.1f} ms")
            
            if losses:
                avg_loss = statistics.mean(losses)
                print(f"Packet Loss: {avg_loss:6.2f}% average")
            
            if jitters:
                avg_jitter = statistics.mean(jitters)
                print(f"Jitter:      {avg_jitter:6.1f} ms average")
            
            # Connection quality distribution
            qualities = [m.connection_quality for m in metrics_list]
            quality_counts = {}
            for quality in qualities:
                quality_counts[quality] = quality_counts.get(quality, 0) + 1
            
            print("Connection Quality Distribution:")
            for quality, count in quality_counts.items():
                percentage = (count / len(qualities)) * 100
                print(f"  {quality:10}: {percentage:5.1f}%")
        
        print("=" * 80)
        
        # Save detailed report to file
        self._save_detailed_report()
    
    def _save_detailed_report(self):
        """Save detailed performance data to JSON"""
        
        report_data = {
            'monitoring_summary': {
                'targets': self.targets,
                'total_measurements': sum(len(history) for history in self.metrics_history.values()),
                'monitoring_duration': time.time() - (
                    min(m.timestamp for history in self.metrics_history.values() 
                        for m in history) if any(self.metrics_history.values()) else time.time()
                )
            },
            'metrics_history': {
                target: [asdict(m) for m in history] 
                for target, history in self.metrics_history.items()
            },
            'alert_thresholds': asdict(self.alert_thresholds),
            'bandwidth_history': list(self.bandwidth_history),
            'timestamp': datetime.now().isoformat()
        }
        
        filename = f"satellite_performance_report_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"Detailed report saved to {filename}")
    
    def create_performance_dashboard(self, target: str):
        """Create real-time performance dashboard"""
        
        if target not in self.metrics_history:
            print(f"No data available for {target}")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Real-time Performance Dashboard: {target}', fontsize=16)
        
        def update_dashboard(frame):
            if not self.metrics_history[target]:
                return
            
            # Get recent data
            recent_data = list(self.metrics_history[target])[-100:]  # Last 100 measurements
            
            if not recent_data:
                return
            
            timestamps = [datetime.fromtimestamp(m.timestamp) for m in recent_data]
            rtts = [m.rtt_ms for m in recent_data]
            losses = [m.packet_loss_percent for m in recent_data]
            jitters = [m.jitter_ms for m in recent_data]
            
            # Clear and update plots
            ax1.clear()
            ax1.plot(timestamps, rtts, 'b-', linewidth=2)
            ax1.set_title('RTT Over Time')
            ax1.set_ylabel('RTT (ms)')
            ax1.grid(True)
            
            ax2.clear()
            ax2.plot(timestamps, losses, 'r-', linewidth=2)
            ax2.set_title('Packet Loss Over Time')
            ax2.set_ylabel('Packet Loss (%)')
            ax2.grid(True)
            
            ax3.clear()
            ax3.plot(timestamps, jitters, 'g-', linewidth=2)
            ax3.set_title('Jitter Over Time')
            ax3.set_ylabel('Jitter (ms)')
            ax3.grid(True)
            
            # Connection quality pie chart
            ax4.clear()
            qualities = [m.connection_quality for m in recent_data]
            quality_counts = {}
            for quality in qualities:
                quality_counts[quality] = quality_counts.get(quality, 0) + 1
            
            if quality_counts:
                ax4.pie(quality_counts.values(), labels=quality_counts.keys(), autopct='%1.1f%%')
                ax4.set_title('Connection Quality Distribution')
            
            plt.tight_layout()
        
        # Create animation
        ani = animation.FuncAnimation(fig, update_dashboard, interval=5000, cache_frame_data=False)
        plt.show()

def main():
    parser = argparse.ArgumentParser(description='Satellite Network Performance Monitor')
    parser.add_argument('targets', nargs='+', help='Target hosts to monitor')
    parser.add_argument('--interval', type=int, default=30,
                       help='Monitoring interval in seconds (default: 30)')
    parser.add_argument('--duration', type=int, default=3600,
                       help='Monitoring duration in seconds (default: 3600)')
    parser.add_argument('--max-rtt', type=float, default=1000.0,
                       help='Alert threshold for RTT in ms (default: 1000)')
    parser.add_argument('--max-loss', type=float, default=5.0,
                       help='Alert threshold for packet loss % (default: 5)')
    parser.add_argument('--max-jitter', type=float, default=50.0,
                       help='Alert threshold for jitter in ms (default: 50)')
    parser.add_argument('--dashboard', action='store_true',
                       help='Show real-time dashboard')
    
    args = parser.parse_args()
    
    # Create alert thresholds
    thresholds = AlertThreshold(
        max_rtt_ms=args.max_rtt,
        max_packet_loss_percent=args.max_loss,
        max_jitter_ms=args.max_jitter
    )
    
    # Create monitor
    monitor = SatellitePerformanceMonitor(args.targets, thresholds)
    
    if args.dashboard and len(args.targets) == 1:
        # Start monitoring in background thread
        monitor_thread = threading.Thread(
            target=monitor.start_monitoring,
            args=(args.interval, args.duration)
        )
        monitor_thread.start()
        
        # Show dashboard
        time.sleep(5)  # Wait for some data
        monitor.create_performance_dashboard(args.targets[0])
        
        monitor_thread.join()
    else:
        # Standard monitoring
        monitor.start_monitoring(args.interval, args.duration)

if __name__ == '__main__':
    main()
