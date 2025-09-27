#!/usr/bin/env python3
"""
Satellite Network Delay Analyzer

This tool performs comprehensive delay analysis for satellite networks,
including RTT measurements, jitter analysis, and delay decomposition.
"""

import subprocess
import time
import json
import argparse
import statistics
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

@dataclass
class DelayMeasurement:
    """Single delay measurement"""
    timestamp: float
    rtt_ms: float
    packet_loss: bool
    sequence: int

@dataclass
class DelayAnalysis:
    """Comprehensive delay analysis results"""
    target: str
    measurements: List[DelayMeasurement]
    min_rtt: float
    max_rtt: float
    avg_rtt: float
    median_rtt: float
    std_dev: float
    jitter: float
    packet_loss_rate: float
    theoretical_satellite_delay: float
    excess_delay: float

class SatelliteDelayAnalyzer:
    """Comprehensive satellite network delay analyzer"""
    
    def __init__(self):
        # Theoretical delays for different satellite types
        self.theoretical_delays = {
            'GEO': 240,      # Geostationary minimum RTT (ms)
            'MEO': 80,       # Medium Earth Orbit typical RTT (ms)
            'LEO': 20,       # Low Earth Orbit typical RTT (ms)
        }
        
        # Speed of light constant
        self.SPEED_OF_LIGHT = 299792458  # m/s
        
    def ping_analysis(self, target: str, count: int = 100, interval: float = 1.0,
                     packet_size: int = 64) -> DelayAnalysis:
        """Perform comprehensive ping-based delay analysis"""
        
        print(f"Starting delay analysis for {target}")
        print(f"Packets: {count}, Interval: {interval}s, Size: {packet_size} bytes")
        print("-" * 60)
        
        measurements = []
        
        for i in range(count):
            measurement = self._single_ping(target, i, packet_size)
            if measurement:
                measurements.append(measurement)
                
                # Real-time display
                if measurement.packet_loss:
                    print(f"Ping {i+1:3d}: TIMEOUT")
                else:
                    print(f"Ping {i+1:3d}: {measurement.rtt_ms:6.2f}ms")
            
            if i < count - 1:  # Don't sleep after last ping
                time.sleep(interval)
        
        return self._analyze_measurements(target, measurements)
    
    def _single_ping(self, target: str, sequence: int, 
                    packet_size: int) -> DelayMeasurement:
        """Perform a single ping measurement"""
        
        try:
            cmd = ['ping', '-c', '1', '-s', str(packet_size), target]
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Parse ping output for RTT
                output = result.stdout
                for line in output.split('\n'):
                    if 'time=' in line:
                        rtt_str = line.split('time=')[1].split()[0]
                        rtt_ms = float(rtt_str)
                        
                        return DelayMeasurement(
                            timestamp=start_time,
                            rtt_ms=rtt_ms,
                            packet_loss=False,
                            sequence=sequence
                        )
            
            # If we get here, ping failed
            return DelayMeasurement(
                timestamp=start_time,
                rtt_ms=0.0,
                packet_loss=True,
                sequence=sequence
            )
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
            return DelayMeasurement(
                timestamp=time.time(),
                rtt_ms=0.0,
                packet_loss=True,
                sequence=sequence
            )
    
    def _analyze_measurements(self, target: str, 
                            measurements: List[DelayMeasurement]) -> DelayAnalysis:
        """Analyze delay measurements and generate comprehensive report"""
        
        # Filter out lost packets for statistical analysis
        successful_measurements = [m for m in measurements if not m.packet_loss]
        rtts = [m.rtt_ms for m in successful_measurements]
        
        if not rtts:
            raise ValueError("No successful measurements obtained")
        
        # Basic statistics
        min_rtt = min(rtts)
        max_rtt = max(rtts)
        avg_rtt = statistics.mean(rtts)
        median_rtt = statistics.median(rtts)
        std_dev = statistics.stdev(rtts) if len(rtts) > 1 else 0.0
        
        # Calculate jitter (average deviation from mean)
        jitter = statistics.mean([abs(rtt - avg_rtt) for rtt in rtts])
        
        # Packet loss rate
        packet_loss_rate = len([m for m in measurements if m.packet_loss]) / len(measurements) * 100
        
        # Determine satellite type and theoretical delay
        satellite_type, theoretical_delay = self._classify_satellite_type(min_rtt)
        excess_delay = avg_rtt - theoretical_delay
        
        analysis = DelayAnalysis(
            target=target,
            measurements=measurements,
            min_rtt=min_rtt,
            max_rtt=max_rtt,
            avg_rtt=avg_rtt,
            median_rtt=median_rtt,
            std_dev=std_dev,
            jitter=jitter,
            packet_loss_rate=packet_loss_rate,
            theoretical_satellite_delay=theoretical_delay,
            excess_delay=excess_delay
        )
        
        self._print_analysis_report(analysis, satellite_type)
        return analysis
    
    def _classify_satellite_type(self, min_rtt: float) -> Tuple[str, float]:
        """Classify satellite type based on minimum RTT"""
        
        if min_rtt >= 200:
            return 'GEO', self.theoretical_delays['GEO']
        elif min_rtt >= 60:
            return 'MEO', self.theoretical_delays['MEO']
        elif min_rtt >= 10:
            return 'LEO', self.theoretical_delays['LEO']
        else:
            return 'Terrestrial', 0.0
    
    def _print_analysis_report(self, analysis: DelayAnalysis, satellite_type: str):
        """Print comprehensive analysis report"""
        
        print("\n" + "=" * 80)
        print("SATELLITE DELAY ANALYSIS REPORT")
        print("=" * 80)
        print(f"Target: {analysis.target}")
        print(f"Total Measurements: {len(analysis.measurements)}")
        print(f"Successful Measurements: {len([m for m in analysis.measurements if not m.packet_loss])}")
        print(f"Packet Loss Rate: {analysis.packet_loss_rate:.2f}%")
        print()
        
        print("DELAY STATISTICS:")
        print(f"  Minimum RTT:     {analysis.min_rtt:8.2f} ms")
        print(f"  Maximum RTT:     {analysis.max_rtt:8.2f} ms")
        print(f"  Average RTT:     {analysis.avg_rtt:8.2f} ms")
        print(f"  Median RTT:      {analysis.median_rtt:8.2f} ms")
        print(f"  Standard Dev:    {analysis.std_dev:8.2f} ms")
        print(f"  Jitter:          {analysis.jitter:8.2f} ms")
        print()
        
        print("SATELLITE ANALYSIS:")
        print(f"  Detected Type:   {satellite_type}")
        print(f"  Theoretical Min: {analysis.theoretical_satellite_delay:8.2f} ms")
        print(f"  Excess Delay:    {analysis.excess_delay:8.2f} ms")
        print()
        
        # Delay breakdown analysis
        self._analyze_delay_components(analysis, satellite_type)
        
        print("=" * 80)
    
    def _analyze_delay_components(self, analysis: DelayAnalysis, satellite_type: str):
        """Analyze and break down delay components"""
        
        print("DELAY COMPONENT ANALYSIS:")
        
        if satellite_type == 'GEO':
            # GEO satellite delay breakdown
            propagation_delay = analysis.theoretical_satellite_delay
            processing_delay = analysis.excess_delay
            
            print(f"  Propagation Delay:  {propagation_delay:8.2f} ms (satellite distance)")
            print(f"  Processing Delay:   {processing_delay:8.2f} ms (equipment + routing)")
            
            # Estimate satellite distance
            distance_km = (propagation_delay / 1000) * self.SPEED_OF_LIGHT / 2000
            print(f"  Estimated Distance: {distance_km:8.0f} km (round trip)")
            
        elif satellite_type in ['LEO', 'MEO']:
            print(f"  Base Satellite RTT: {analysis.theoretical_satellite_delay:8.2f} ms")
            print(f"  Additional Delay:   {analysis.excess_delay:8.2f} ms")
            
        # Jitter analysis
        if analysis.jitter > 10:
            print(f"  High Jitter Detected: {analysis.jitter:.2f}ms (possible congestion)")
        elif analysis.jitter > 5:
            print(f"  Moderate Jitter: {analysis.jitter:.2f}ms (normal variation)")
        else:
            print(f"  Low Jitter: {analysis.jitter:.2f}ms (stable connection)")
        
        print()
    
    def continuous_delay_monitoring(self, target: str, duration: int = 3600,
                                  interval: float = 1.0):
        """Continuously monitor delay characteristics"""
        
        print(f"Starting continuous delay monitoring for {target}")
        print(f"Duration: {duration}s, Interval: {interval}s")
        print("-" * 50)
        
        measurements = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            measurement = self._single_ping(target, len(measurements), 64)
            if measurement:
                measurements.append(measurement)
                
                # Real-time statistics every 60 measurements
                if len(measurements) % 60 == 0:
                    recent_rtts = [m.rtt_ms for m in measurements[-60:] if not m.packet_loss]
                    if recent_rtts:
                        avg_recent = statistics.mean(recent_rtts)
                        print(f"Recent 60s average: {avg_recent:.2f}ms")
            
            time.sleep(interval)
        
        # Final analysis
        return self._analyze_measurements(target, measurements)
    
    def multi_target_analysis(self, targets: List[str], count: int = 50):
        """Analyze delay characteristics for multiple targets"""
        
        print(f"Multi-target delay analysis for {len(targets)} targets")
        print("-" * 60)
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.ping_analysis, target, count, 0.1): target 
                      for target in targets}
            
            for future in futures:
                target = futures[future]
                try:
                    results[target] = future.result()
                except Exception as e:
                    print(f"Error analyzing {target}: {e}")
        
        # Comparative analysis
        self._print_comparative_analysis(results)
        return results
    
    def _print_comparative_analysis(self, results: Dict[str, DelayAnalysis]):
        """Print comparative analysis of multiple targets"""
        
        print("\n" + "=" * 80)
        print("COMPARATIVE DELAY ANALYSIS")
        print("=" * 80)
        
        print(f"{'Target':<25} {'Min RTT':<10} {'Avg RTT':<10} {'Jitter':<10} {'Loss %':<8}")
        print("-" * 80)
        
        for target, analysis in results.items():
            print(f"{target:<25} {analysis.min_rtt:<10.2f} {analysis.avg_rtt:<10.2f} "
                  f"{analysis.jitter:<10.2f} {analysis.packet_loss_rate:<8.2f}")
        
        print("=" * 80)
    
    def generate_delay_plot(self, analysis: DelayAnalysis, filename: str = None):
        """Generate delay visualization plots"""
        
        successful_measurements = [m for m in analysis.measurements if not m.packet_loss]
        timestamps = [m.timestamp for m in successful_measurements]
        rtts = [m.rtt_ms for m in successful_measurements]
        
        if not rtts:
            print("No data to plot")
            return
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Satellite Delay Analysis: {analysis.target}', fontsize=16)
        
        # RTT over time
        ax1.plot(timestamps, rtts, 'b-', alpha=0.7)
        ax1.set_title('RTT Over Time')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('RTT (ms)')
        ax1.grid(True)
        
        # RTT histogram
        ax2.hist(rtts, bins=30, alpha=0.7, color='green')
        ax2.axvline(analysis.avg_rtt, color='red', linestyle='--', label=f'Mean: {analysis.avg_rtt:.2f}ms')
        ax2.axvline(analysis.median_rtt, color='orange', linestyle='--', label=f'Median: {analysis.median_rtt:.2f}ms')
        ax2.set_title('RTT Distribution')
        ax2.set_xlabel('RTT (ms)')
        ax2.set_ylabel('Frequency')
        ax2.legend()
        ax2.grid(True)
        
        # Jitter analysis
        if len(rtts) > 1:
            jitter_values = [abs(rtts[i] - rtts[i-1]) for i in range(1, len(rtts))]
            ax3.plot(jitter_values, 'r-', alpha=0.7)
            ax3.set_title('Jitter (RTT Variation)')
            ax3.set_xlabel('Measurement')
            ax3.set_ylabel('Jitter (ms)')
            ax3.grid(True)
        
        # Packet loss over time
        loss_indicators = [1 if m.packet_loss else 0 for m in analysis.measurements]
        ax4.plot(loss_indicators, 'ro', markersize=2)
        ax4.set_title('Packet Loss Over Time')
        ax4.set_xlabel('Measurement')
        ax4.set_ylabel('Packet Lost (1=Yes, 0=No)')
        ax4.grid(True)
        
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Plot saved as {filename}")
        else:
            plt.show()

def main():
    parser = argparse.ArgumentParser(description='Satellite Network Delay Analyzer')
    parser.add_argument('target', help='Target IP or hostname')
    parser.add_argument('--count', type=int, default=100,
                       help='Number of ping packets (default: 100)')
    parser.add_argument('--interval', type=float, default=1.0,
                       help='Interval between pings in seconds (default: 1.0)')
    parser.add_argument('--size', type=int, default=64,
                       help='Packet size in bytes (default: 64)')
    parser.add_argument('--monitor', action='store_true',
                       help='Enable continuous monitoring')
    parser.add_argument('--duration', type=int, default=3600,
                       help='Monitoring duration in seconds (default: 3600)')
    parser.add_argument('--plot', action='store_true',
                       help='Generate delay plots')
    parser.add_argument('--output', type=str,
                       help='Output filename for plots')
    
    args = parser.parse_args()
    
    analyzer = SatelliteDelayAnalyzer()
    
    if args.monitor:
        analysis = analyzer.continuous_delay_monitoring(args.target, args.duration, args.interval)
    else:
        analysis = analyzer.ping_analysis(args.target, args.count, args.interval, args.size)
    
    if args.plot:
        analyzer.generate_delay_plot(analysis, args.output)
    
    # Save results to JSON
    results_file = f"delay_analysis_{args.target.replace('.', '_')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'target': analysis.target,
            'min_rtt': analysis.min_rtt,
            'max_rtt': analysis.max_rtt,
            'avg_rtt': analysis.avg_rtt,
            'median_rtt': analysis.median_rtt,
            'std_dev': analysis.std_dev,
            'jitter': analysis.jitter,
            'packet_loss_rate': analysis.packet_loss_rate,
            'theoretical_satellite_delay': analysis.theoretical_satellite_delay,
            'excess_delay': analysis.excess_delay,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\nResults saved to {results_file}")

if __name__ == '__main__':
    main()
