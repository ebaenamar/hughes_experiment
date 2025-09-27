#!/usr/bin/env python3
"""
Basic Hughes Satellite Network Analysis Example

This script demonstrates how to perform basic analysis of Hughes satellite
network connections using the research tools.
"""

import sys
import os
import time
import json
from datetime import datetime

# Add tools directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))

from satellite_tracer import SatelliteTracer
from delay_analyzer import SatelliteDelayAnalyzer
from performance_monitor import SatellitePerformanceMonitor, AlertThreshold

def analyze_hughes_connection(target_host: str):
    """
    Perform comprehensive analysis of Hughes satellite connection
    """
    
    print("=" * 80)
    print("HUGHES SATELLITE NETWORK ANALYSIS")
    print("=" * 80)
    print(f"Target: {target_host}")
    print(f"Analysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Satellite Route Tracing
    print("Step 1: Analyzing packet routing path...")
    print("-" * 50)
    
    tracer = SatelliteTracer()
    route = tracer.enhanced_traceroute(target_host, max_hops=25, packets_per_hop=3)
    
    # Step 2: Delay Analysis
    print("\nStep 2: Performing delay analysis...")
    print("-" * 50)
    
    analyzer = SatelliteDelayAnalyzer()
    delay_analysis = analyzer.ping_analysis(target_host, count=50, interval=0.5)
    
    # Step 3: Generate Summary Report
    print("\nStep 3: Generating analysis summary...")
    print("-" * 50)
    
    generate_summary_report(target_host, route, delay_analysis)
    
    # Step 4: Save Results
    save_analysis_results(target_host, route, delay_analysis)
    
    print("\nAnalysis complete!")
    return route, delay_analysis

def generate_summary_report(target: str, route, delay_analysis):
    """Generate a comprehensive summary report"""
    
    print("\n" + "=" * 80)
    print("HUGHES SATELLITE CONNECTION SUMMARY")
    print("=" * 80)
    
    # Route Analysis Summary
    print("ROUTING ANALYSIS:")
    print(f"  Total Hops: {route.total_hops}")
    print(f"  Satellite Hops: {route.satellite_hops}")
    print(f"  Gateway Hops: {route.gateway_hops}")
    print(f"  Terrestrial Hops: {route.terrestrial_hops}")
    print(f"  Total Route RTT: {route.total_rtt:.1f}ms")
    print()
    
    # Identify Hughes Infrastructure
    hughes_hops = []
    for hop in route.hops:
        if hop.hostname and any(indicator in hop.hostname.lower() 
                               for indicator in ['hughes', 'jupiter', 'spaceway']):
            hughes_hops.append(hop)
    
    if hughes_hops:
        print("HUGHES INFRASTRUCTURE DETECTED:")
        for hop in hughes_hops:
            print(f"  Hop {hop.hop_number}: {hop.ip_address} ({hop.hostname})")
            print(f"    RTT: {hop.avg_rtt:.1f}ms, Type: {hop.hop_type}")
    print()
    
    # Delay Analysis Summary
    print("DELAY CHARACTERISTICS:")
    print(f"  Minimum RTT: {delay_analysis.min_rtt:.1f}ms")
    print(f"  Average RTT: {delay_analysis.avg_rtt:.1f}ms")
    print(f"  Maximum RTT: {delay_analysis.max_rtt:.1f}ms")
    print(f"  Jitter: {delay_analysis.jitter:.1f}ms")
    print(f"  Packet Loss: {delay_analysis.packet_loss_rate:.1f}%")
    print()
    
    # Satellite Classification
    if delay_analysis.min_rtt > 200:
        satellite_type = "Geostationary (GEO)"
        expected_min = 240
    elif delay_analysis.min_rtt > 60:
        satellite_type = "Medium Earth Orbit (MEO)"
        expected_min = 80
    else:
        satellite_type = "Low Earth Orbit (LEO) or Terrestrial"
        expected_min = 20
    
    print("SATELLITE CLASSIFICATION:")
    print(f"  Detected Type: {satellite_type}")
    print(f"  Expected Minimum RTT: {expected_min}ms")
    print(f"  Actual Minimum RTT: {delay_analysis.min_rtt:.1f}ms")
    print(f"  Excess Delay: {delay_analysis.excess_delay:.1f}ms")
    print()
    
    # Performance Assessment
    assess_connection_performance(delay_analysis)
    
    print("=" * 80)

def assess_connection_performance(delay_analysis):
    """Assess overall connection performance"""
    
    print("PERFORMANCE ASSESSMENT:")
    
    # RTT Assessment
    if delay_analysis.avg_rtt < 300:
        rtt_grade = "Excellent"
    elif delay_analysis.avg_rtt < 400:
        rtt_grade = "Good"
    elif delay_analysis.avg_rtt < 500:
        rtt_grade = "Fair"
    else:
        rtt_grade = "Poor"
    
    print(f"  RTT Performance: {rtt_grade} ({delay_analysis.avg_rtt:.1f}ms average)")
    
    # Jitter Assessment
    if delay_analysis.jitter < 10:
        jitter_grade = "Excellent"
    elif delay_analysis.jitter < 30:
        jitter_grade = "Good"
    elif delay_analysis.jitter < 50:
        jitter_grade = "Fair"
    else:
        jitter_grade = "Poor"
    
    print(f"  Jitter Performance: {jitter_grade} ({delay_analysis.jitter:.1f}ms)")
    
    # Packet Loss Assessment
    if delay_analysis.packet_loss_rate < 1:
        loss_grade = "Excellent"
    elif delay_analysis.packet_loss_rate < 3:
        loss_grade = "Good"
    elif delay_analysis.packet_loss_rate < 5:
        loss_grade = "Fair"
    else:
        loss_grade = "Poor"
    
    print(f"  Reliability: {loss_grade} ({delay_analysis.packet_loss_rate:.1f}% loss)")
    
    # Overall Grade
    grades = [rtt_grade, jitter_grade, loss_grade]
    if all(g == "Excellent" for g in grades):
        overall = "Excellent"
    elif all(g in ["Excellent", "Good"] for g in grades):
        overall = "Good"
    elif any(g == "Poor" for g in grades):
        overall = "Poor"
    else:
        overall = "Fair"
    
    print(f"  Overall Performance: {overall}")
    print()

def save_analysis_results(target: str, route, delay_analysis):
    """Save analysis results to files"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save route analysis
    route_data = {
        'target': target,
        'timestamp': timestamp,
        'total_hops': route.total_hops,
        'satellite_hops': route.satellite_hops,
        'gateway_hops': route.gateway_hops,
        'terrestrial_hops': route.terrestrial_hops,
        'total_rtt': route.total_rtt,
        'hops': [
            {
                'hop_number': hop.hop_number,
                'ip_address': hop.ip_address,
                'hostname': hop.hostname,
                'avg_rtt': hop.avg_rtt,
                'hop_type': hop.hop_type,
                'packet_loss': hop.packet_loss
            }
            for hop in route.hops
        ]
    }
    
    route_filename = f"route_analysis_{target.replace('.', '_')}_{timestamp}.json"
    with open(route_filename, 'w') as f:
        json.dump(route_data, f, indent=2)
    
    # Save delay analysis
    delay_data = {
        'target': target,
        'timestamp': timestamp,
        'min_rtt': delay_analysis.min_rtt,
        'max_rtt': delay_analysis.max_rtt,
        'avg_rtt': delay_analysis.avg_rtt,
        'median_rtt': delay_analysis.median_rtt,
        'std_dev': delay_analysis.std_dev,
        'jitter': delay_analysis.jitter,
        'packet_loss_rate': delay_analysis.packet_loss_rate,
        'theoretical_satellite_delay': delay_analysis.theoretical_satellite_delay,
        'excess_delay': delay_analysis.excess_delay,
        'total_measurements': len(delay_analysis.measurements)
    }
    
    delay_filename = f"delay_analysis_{target.replace('.', '_')}_{timestamp}.json"
    with open(delay_filename, 'w') as f:
        json.dump(delay_data, f, indent=2)
    
    print(f"Results saved:")
    print(f"  Route analysis: {route_filename}")
    print(f"  Delay analysis: {delay_filename}")

def quick_satellite_check(target_host: str):
    """
    Quick check to determine if connection uses satellite
    """
    
    print(f"Quick satellite check for {target_host}...")
    
    analyzer = SatelliteDelayAnalyzer()
    
    # Quick ping test
    measurement = analyzer._single_ping(target_host, 0, 64)
    
    if measurement and not measurement.packet_loss:
        rtt = measurement.rtt_ms
        
        print(f"RTT: {rtt:.1f}ms")
        
        if rtt > 200:
            print("✓ Satellite connection detected (GEO)")
            return "GEO"
        elif rtt > 60:
            print("? Possible satellite connection (MEO)")
            return "MEO"
        elif rtt > 20:
            print("? Possible satellite connection (LEO)")
            return "LEO"
        else:
            print("✗ Terrestrial connection")
            return "Terrestrial"
    else:
        print("✗ Connection failed")
        return "Failed"

def monitor_hughes_performance(target_host: str, duration_minutes: int = 60):
    """
    Monitor Hughes satellite performance for specified duration
    """
    
    print(f"Starting performance monitoring for {target_host}")
    print(f"Duration: {duration_minutes} minutes")
    
    # Set up Hughes-specific alert thresholds
    thresholds = AlertThreshold(
        max_rtt_ms=600.0,        # Higher threshold for satellite
        max_packet_loss_percent=3.0,
        max_jitter_ms=40.0,
        min_download_mbps=5.0,
        min_upload_mbps=1.0
    )
    
    monitor = SatellitePerformanceMonitor([target_host], thresholds)
    monitor.start_monitoring(interval=30, duration=duration_minutes * 60)

def main():
    """Main function for basic analysis"""
    
    if len(sys.argv) < 2:
        print("Usage: python basic_analysis.py <target_host> [command]")
        print("Commands:")
        print("  full     - Full analysis (default)")
        print("  quick    - Quick satellite check")
        print("  monitor  - Performance monitoring")
        sys.exit(1)
    
    target_host = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "full"
    
    if command == "quick":
        quick_satellite_check(target_host)
    elif command == "monitor":
        monitor_hughes_performance(target_host, 60)
    else:
        analyze_hughes_connection(target_host)

if __name__ == "__main__":
    main()
