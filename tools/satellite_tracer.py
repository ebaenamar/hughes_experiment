#!/usr/bin/env python3
"""
Advanced Satellite Network Packet Tracer

This tool provides enhanced packet tracing capabilities specifically designed
for satellite networks, including Hughes satellite systems. It can identify
satellite hops, measure delays, and analyze routing paths.
"""

import subprocess
import socket
import time
import json
import argparse
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import statistics

@dataclass
class HopInfo:
    """Information about a network hop"""
    hop_number: int
    ip_address: str
    hostname: Optional[str]
    rtt_ms: List[float]
    avg_rtt: float
    packet_loss: float
    hop_type: str  # 'terrestrial', 'satellite', 'gateway', 'unknown'
    
@dataclass
class SatelliteRoute:
    """Complete satellite route information"""
    destination: str
    total_hops: int
    hops: List[HopInfo]
    total_rtt: float
    satellite_hops: int
    terrestrial_hops: int
    gateway_hops: int

class SatelliteTracer:
    """Advanced satellite network tracer"""
    
    def __init__(self):
        self.satellite_indicators = [
            'hughes', 'satellite', 'sat', 'geo', 'leo', 'meo',
            'vsat', 'jupiter', 'spaceway', 'echostar', 'intelsat',
            'ses', 'eutelsat', 'telesat', 'starlink', 'oneweb'
        ]
        
        self.gateway_indicators = [
            'gateway', 'gw', 'noc', 'teleport', 'earth-station',
            'ground-station', 'pop', 'hub'
        ]
        
        # Known satellite network IP ranges (examples)
        self.satellite_ranges = [
            '67.15.0.0/16',    # Hughes
            '69.46.0.0/16',    # Hughes
            '74.192.0.0/10',   # Hughes
            '162.248.0.0/16',  # Hughes
        ]
    
    def classify_hop(self, ip: str, hostname: Optional[str], rtt: float) -> str:
        """Classify a hop as terrestrial, satellite, gateway, or unknown"""
        
        # Check hostname for satellite indicators
        if hostname:
            hostname_lower = hostname.lower()
            if any(indicator in hostname_lower for indicator in self.satellite_indicators):
                return 'satellite'
            if any(indicator in hostname_lower for indicator in self.gateway_indicators):
                return 'gateway'
        
        # Check for high RTT indicating satellite hop
        if rtt > 200:  # Likely satellite if RTT > 200ms
            return 'satellite'
        elif rtt > 100:  # Possible satellite or long terrestrial
            return 'possible_satellite'
        
        return 'terrestrial'
    
    def enhanced_traceroute(self, destination: str, max_hops: int = 30, 
                          packets_per_hop: int = 3) -> SatelliteRoute:
        """Perform enhanced traceroute with satellite-specific analysis"""
        
        print(f"Tracing route to {destination} with satellite analysis...")
        print(f"Maximum hops: {max_hops}, Packets per hop: {packets_per_hop}")
        print("-" * 80)
        
        hops = []
        
        for hop_num in range(1, max_hops + 1):
            hop_info = self._trace_single_hop(destination, hop_num, packets_per_hop)
            if hop_info:
                hops.append(hop_info)
                self._print_hop_info(hop_info)
                
                # Check if we've reached the destination
                if hop_info.ip_address == destination:
                    break
            else:
                # Timeout or no response
                print(f"{hop_num:2d}  * * * Request timed out")
        
        return self._analyze_route(destination, hops)
    
    def _trace_single_hop(self, destination: str, hop_num: int, 
                         packets: int) -> Optional[HopInfo]:
        """Trace a single hop with multiple packets"""
        
        rtts = []
        ip_address = None
        hostname = None
        
        for packet_num in range(packets):
            try:
                # Use system traceroute for single hop
                cmd = ['traceroute', '-n', '-m', str(hop_num), '-q', '1', destination]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > hop_num:
                        line = lines[hop_num]
                        # Parse traceroute output
                        parts = line.split()
                        if len(parts) >= 3 and parts[1] != '*':
                            if not ip_address:
                                ip_address = parts[1]
                            
                            # Extract RTT
                            for part in parts[2:]:
                                if 'ms' in part:
                                    try:
                                        rtt = float(part.replace('ms', ''))
                                        rtts.append(rtt)
                                        break
                                    except ValueError:
                                        continue
                
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                continue
        
        if not ip_address or not rtts:
            return None
        
        # Try to resolve hostname
        try:
            hostname = socket.gethostbyaddr(ip_address)[0]
        except (socket.herror, socket.gaierror):
            hostname = None
        
        avg_rtt = statistics.mean(rtts)
        packet_loss = (packets - len(rtts)) / packets * 100
        hop_type = self.classify_hop(ip_address, hostname, avg_rtt)
        
        return HopInfo(
            hop_number=hop_num,
            ip_address=ip_address,
            hostname=hostname,
            rtt_ms=rtts,
            avg_rtt=avg_rtt,
            packet_loss=packet_loss,
            hop_type=hop_type
        )
    
    def _print_hop_info(self, hop: HopInfo):
        """Print formatted hop information"""
        
        hostname_str = f" ({hop.hostname})" if hop.hostname else ""
        rtt_str = " ".join([f"{rtt:.1f}ms" for rtt in hop.rtt_ms])
        
        # Color coding based on hop type
        type_indicator = {
            'satellite': '🛰️ ',
            'gateway': '🌐',
            'terrestrial': '🌍',
            'possible_satellite': '🛰️?',
            'unknown': '❓'
        }.get(hop.hop_type, '  ')
        
        print(f"{hop.hop_number:2d}  {type_indicator} {hop.ip_address}{hostname_str}")
        print(f"     RTT: {rtt_str} (avg: {hop.avg_rtt:.1f}ms)")
        if hop.packet_loss > 0:
            print(f"     Packet Loss: {hop.packet_loss:.1f}%")
        print()
    
    def _analyze_route(self, destination: str, hops: List[HopInfo]) -> SatelliteRoute:
        """Analyze the complete route and generate summary"""
        
        satellite_hops = len([h for h in hops if h.hop_type == 'satellite'])
        gateway_hops = len([h for h in hops if h.hop_type == 'gateway'])
        terrestrial_hops = len([h for h in hops if h.hop_type == 'terrestrial'])
        
        total_rtt = sum(hop.avg_rtt for hop in hops)
        
        route = SatelliteRoute(
            destination=destination,
            total_hops=len(hops),
            hops=hops,
            total_rtt=total_rtt,
            satellite_hops=satellite_hops,
            terrestrial_hops=terrestrial_hops,
            gateway_hops=gateway_hops
        )
        
        self._print_route_summary(route)
        return route
    
    def _print_route_summary(self, route: SatelliteRoute):
        """Print route analysis summary"""
        
        print("=" * 80)
        print("SATELLITE ROUTE ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Destination: {route.destination}")
        print(f"Total Hops: {route.total_hops}")
        print(f"Total RTT: {route.total_rtt:.1f}ms")
        print()
        print("Hop Classification:")
        print(f"  🛰️  Satellite Hops: {route.satellite_hops}")
        print(f"  🌐 Gateway Hops: {route.gateway_hops}")
        print(f"  🌍 Terrestrial Hops: {route.terrestrial_hops}")
        print()
        
        # Identify potential satellite segments
        satellite_segments = self._identify_satellite_segments(route.hops)
        if satellite_segments:
            print("Satellite Segments Detected:")
            for i, segment in enumerate(satellite_segments, 1):
                start_hop, end_hop, segment_rtt = segment
                print(f"  Segment {i}: Hops {start_hop}-{end_hop} "
                      f"(RTT: {segment_rtt:.1f}ms)")
        
        print("=" * 80)
    
    def _identify_satellite_segments(self, hops: List[HopInfo]) -> List[Tuple[int, int, float]]:
        """Identify continuous satellite segments in the route"""
        
        segments = []
        in_satellite_segment = False
        segment_start = None
        segment_rtt = 0
        
        for hop in hops:
            if hop.hop_type in ['satellite', 'possible_satellite']:
                if not in_satellite_segment:
                    in_satellite_segment = True
                    segment_start = hop.hop_number
                    segment_rtt = hop.avg_rtt
                else:
                    segment_rtt += hop.avg_rtt
            else:
                if in_satellite_segment:
                    segments.append((segment_start, hop.hop_number - 1, segment_rtt))
                    in_satellite_segment = False
                    segment_rtt = 0
        
        # Handle case where route ends in satellite segment
        if in_satellite_segment and segment_start:
            segments.append((segment_start, hops[-1].hop_number, segment_rtt))
        
        return segments
    
    def continuous_monitoring(self, destination: str, interval: int = 60, 
                            duration: int = 3600):
        """Continuously monitor satellite route for changes"""
        
        print(f"Starting continuous monitoring of {destination}")
        print(f"Interval: {interval}s, Duration: {duration}s")
        print("-" * 50)
        
        start_time = time.time()
        iteration = 0
        
        while time.time() - start_time < duration:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            route = self.enhanced_traceroute(destination, max_hops=20, packets_per_hop=1)
            
            # Log results
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_entry = {
                'timestamp': timestamp,
                'iteration': iteration,
                'total_hops': route.total_hops,
                'total_rtt': route.total_rtt,
                'satellite_hops': route.satellite_hops
            }
            
            with open(f'satellite_monitoring_{destination.replace(".", "_")}.json', 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description='Advanced Satellite Network Tracer')
    parser.add_argument('destination', help='Destination IP or hostname')
    parser.add_argument('--max-hops', type=int, default=30, 
                       help='Maximum number of hops (default: 30)')
    parser.add_argument('--packets', type=int, default=3,
                       help='Packets per hop (default: 3)')
    parser.add_argument('--monitor', action='store_true',
                       help='Enable continuous monitoring')
    parser.add_argument('--interval', type=int, default=60,
                       help='Monitoring interval in seconds (default: 60)')
    parser.add_argument('--duration', type=int, default=3600,
                       help='Monitoring duration in seconds (default: 3600)')
    
    args = parser.parse_args()
    
    tracer = SatelliteTracer()
    
    if args.monitor:
        tracer.continuous_monitoring(args.destination, args.interval, args.duration)
    else:
        tracer.enhanced_traceroute(args.destination, args.max_hops, args.packets)

if __name__ == '__main__':
    main()
