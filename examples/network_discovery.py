#!/usr/bin/env python3
"""
Hughes Satellite Network Discovery Example

This script demonstrates how to discover and map Hughes satellite network
infrastructure using automated discovery techniques.
"""

import sys
import os
import json
import ipaddress
from typing import List, Dict, Set
from concurrent.futures import ThreadPoolExecutor

# Add tools directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))

from network_mapper import SatelliteNetworkMapper
from satellite_tracer import SatelliteTracer

class HughesNetworkDiscovery:
    """Specialized Hughes network discovery and analysis"""
    
    def __init__(self):
        self.mapper = SatelliteNetworkMapper()
        self.tracer = SatelliteTracer()
        
        # Known Hughes network ranges
        self.hughes_networks = [
            '67.15.0.0/16',      # Hughes primary
            '69.46.0.0/16',      # Hughes secondary
            '74.192.0.0/10',     # Hughes broadband
            '162.248.0.0/16',    # Hughes satellite
            '199.167.0.0/16',    # Hughes infrastructure
        ]
        
        # Common Hughes test targets
        self.test_targets = [
            'google.com',
            'facebook.com',
            '8.8.8.8',
            'cloudflare.com',
            'amazon.com'
        ]
    
    def discover_hughes_infrastructure(self):
        """Discover Hughes satellite network infrastructure"""
        
        print("=" * 80)
        print("HUGHES SATELLITE NETWORK INFRASTRUCTURE DISCOVERY")
        print("=" * 80)
        
        print("Phase 1: Network Range Analysis")
        print("-" * 50)
        
        # Analyze known Hughes networks
        discovered_nodes = {}
        all_links = []
        
        for network in self.hughes_networks:
            print(f"\nAnalyzing network range: {network}")
            
            # Sample IPs from each network
            sample_ips = self._sample_network_range(network, 20)
            
            # Test connectivity to sampled IPs
            active_ips = self._test_ip_connectivity(sample_ips)
            
            print(f"Found {len(active_ips)} active hosts in {network}")
            
            # Analyze active hosts
            for ip in active_ips:
                node_info = self._analyze_hughes_node(ip)
                if node_info:
                    discovered_nodes[ip] = node_info
        
        print(f"\nPhase 1 Complete: Discovered {len(discovered_nodes)} Hughes nodes")
        
        print("\nPhase 2: Route Analysis to Common Destinations")
        print("-" * 50)
        
        # Trace routes to common destinations to find Hughes infrastructure
        route_nodes = {}
        
        for target in self.test_targets:
            print(f"\nTracing route to {target}...")
            
            try:
                route = self.tracer.enhanced_traceroute(target, max_hops=20, packets_per_hop=1)
                
                # Extract Hughes-related hops
                for hop in route.hops:
                    if self._is_hughes_infrastructure(hop):
                        route_nodes[hop.ip_address] = {
                            'ip': hop.ip_address,
                            'hostname': hop.hostname,
                            'hop_type': hop.hop_type,
                            'avg_rtt': hop.avg_rtt,
                            'discovered_via': f"route_to_{target}"
                        }
                        print(f"  Hughes infrastructure found: {hop.ip_address} ({hop.hostname})")
                
            except Exception as e:
                print(f"  Error tracing to {target}: {e}")
        
        print(f"\nPhase 2 Complete: Found {len(route_nodes)} Hughes infrastructure nodes")
        
        # Combine discoveries
        all_nodes = {**discovered_nodes, **route_nodes}
        
        print("\nPhase 3: Infrastructure Classification")
        print("-" * 50)
        
        classified_infrastructure = self._classify_hughes_infrastructure(all_nodes)
        
        print("\nPhase 4: Generating Infrastructure Map")
        print("-" * 50)
        
        self._generate_infrastructure_report(classified_infrastructure)
        
        return classified_infrastructure
    
    def _sample_network_range(self, network_cidr: str, max_samples: int) -> List[str]:
        """Sample IP addresses from network range"""
        
        try:
            network = ipaddress.ip_network(network_cidr, strict=False)
            
            # For large networks, sample strategically
            if network.num_addresses > max_samples * 10:
                # Sample from different subnets
                sampled_ips = []
                step = max(1, network.num_addresses // max_samples)
                
                for i, ip in enumerate(network.hosts()):
                    if i % step == 0:
                        sampled_ips.append(str(ip))
                    if len(sampled_ips) >= max_samples:
                        break
                
                return sampled_ips
            else:
                # Sample all or most IPs
                return [str(ip) for ip in list(network.hosts())[:max_samples]]
                
        except Exception as e:
            print(f"Error sampling network {network_cidr}: {e}")
            return []
    
    def _test_ip_connectivity(self, ip_list: List[str]) -> List[str]:
        """Test connectivity to list of IPs"""
        
        active_ips = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit ping tests
            future_to_ip = {
                executor.submit(self.mapper._ping_host, ip, 2): ip 
                for ip in ip_list
            }
            
            # Collect results
            for future in future_to_ip:
                ip = future_to_ip[future]
                try:
                    if future.result():
                        active_ips.append(ip)
                except:
                    pass  # Ignore failures
        
        return active_ips
    
    def _analyze_hughes_node(self, ip: str) -> Dict:
        """Analyze a potential Hughes network node"""
        
        try:
            # Get basic node information
            node = self.mapper._analyze_host(ip)
            
            if node:
                # Additional Hughes-specific analysis
                hughes_indicators = self._detect_hughes_indicators(node)
                
                return {
                    'ip': ip,
                    'hostname': node.hostname,
                    'node_type': node.node_type,
                    'location': node.location,
                    'asn': node.asn,
                    'organization': node.organization,
                    'rtt_ms': node.rtt_ms,
                    'services': node.services,
                    'hughes_indicators': hughes_indicators,
                    'confidence': self._calculate_hughes_confidence(node, hughes_indicators)
                }
        
        except Exception as e:
            print(f"Error analyzing node {ip}: {e}")
        
        return None
    
    def _detect_hughes_indicators(self, node) -> List[str]:
        """Detect indicators that suggest Hughes infrastructure"""
        
        indicators = []
        
        # Hostname analysis
        if node.hostname:
            hostname_lower = node.hostname.lower()
            
            hughes_keywords = [
                'hughes', 'jupiter', 'spaceway', 'echostar',
                'hughesnet', 'direcway', 'vsat'
            ]
            
            for keyword in hughes_keywords:
                if keyword in hostname_lower:
                    indicators.append(f"hostname_contains_{keyword}")
        
        # ASN analysis
        if node.asn in [7155, 22394]:  # Known Hughes ASNs
            indicators.append("hughes_asn")
        
        # Organization analysis
        if node.organization and 'hughes' in node.organization.lower():
            indicators.append("hughes_organization")
        
        # RTT analysis (satellite indicators)
        if node.rtt_ms > 200:
            indicators.append("satellite_rtt")
        
        # Service analysis
        for service in node.services:
            if any(port in service for port in ['80', '443', '22']):
                indicators.append(f"service_{service}")
        
        return indicators
    
    def _calculate_hughes_confidence(self, node, indicators: List[str]) -> float:
        """Calculate confidence that this is Hughes infrastructure"""
        
        confidence = 0.0
        
        # Strong indicators
        if any('hughes' in ind for ind in indicators):
            confidence += 0.8
        
        if 'hughes_asn' in indicators:
            confidence += 0.7
        
        if 'satellite_rtt' in indicators:
            confidence += 0.5
        
        # Moderate indicators
        if any('jupiter' in ind or 'spaceway' in ind for ind in indicators):
            confidence += 0.6
        
        # Weak indicators
        if any('service_' in ind for ind in indicators):
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def _is_hughes_infrastructure(self, hop) -> bool:
        """Check if a hop represents Hughes infrastructure"""
        
        if hop.hostname:
            hostname_lower = hop.hostname.lower()
            hughes_keywords = ['hughes', 'jupiter', 'spaceway', 'hughesnet', 'direcway']
            
            if any(keyword in hostname_lower for keyword in hughes_keywords):
                return True
        
        # Check if IP is in known Hughes ranges
        try:
            ip_addr = ipaddress.ip_address(hop.ip_address)
            for network_str in self.hughes_networks:
                network = ipaddress.ip_network(network_str, strict=False)
                if ip_addr in network:
                    return True
        except:
            pass
        
        # High RTT suggests satellite
        if hop.avg_rtt > 200:
            return True
        
        return False
    
    def _classify_hughes_infrastructure(self, nodes: Dict) -> Dict:
        """Classify discovered Hughes infrastructure"""
        
        classification = {
            'satellites': [],
            'gateways': [],
            'ground_stations': [],
            'pops': [],
            'customer_equipment': [],
            'unknown': []
        }
        
        for ip, node_info in nodes.items():
            node_type = self._determine_infrastructure_type(node_info)
            classification[node_type].append(node_info)
        
        return classification
    
    def _determine_infrastructure_type(self, node_info: Dict) -> str:
        """Determine the type of Hughes infrastructure"""
        
        hostname = node_info.get('hostname', '').lower() if node_info.get('hostname') else ''
        rtt = node_info.get('rtt_ms', 0)
        indicators = node_info.get('hughes_indicators', [])
        
        # Satellite classification
        if rtt > 200 or 'satellite_rtt' in indicators:
            if any(keyword in hostname for keyword in ['sat', 'satellite', 'jupiter', 'spaceway']):
                return 'satellites'
        
        # Gateway classification
        if any(keyword in hostname for keyword in ['gw', 'gateway', 'teleport']):
            return 'gateways'
        
        # Ground station classification
        if any(keyword in hostname for keyword in ['ground', 'earth', 'station']):
            return 'ground_stations'
        
        # PoP classification
        if any(keyword in hostname for keyword in ['pop', 'point-of-presence']):
            return 'pops'
        
        # Customer equipment
        if any(keyword in hostname for keyword in ['cpe', 'modem', 'customer']):
            return 'customer_equipment'
        
        return 'unknown'
    
    def _generate_infrastructure_report(self, infrastructure: Dict):
        """Generate comprehensive infrastructure report"""
        
        print("\n" + "=" * 80)
        print("HUGHES SATELLITE INFRASTRUCTURE REPORT")
        print("=" * 80)
        
        total_nodes = sum(len(nodes) for nodes in infrastructure.values())
        print(f"Total Infrastructure Nodes Discovered: {total_nodes}")
        print()
        
        for category, nodes in infrastructure.items():
            if nodes:
                print(f"{category.upper()}: {len(nodes)} nodes")
                
                # Show top nodes by confidence
                sorted_nodes = sorted(nodes, 
                                    key=lambda x: x.get('confidence', 0), 
                                    reverse=True)
                
                for i, node in enumerate(sorted_nodes[:5]):  # Top 5
                    hostname = node.get('hostname', 'N/A')
                    confidence = node.get('confidence', 0)
                    rtt = node.get('rtt_ms', 0)
                    
                    print(f"  {i+1}. {node['ip']} ({hostname})")
                    print(f"     RTT: {rtt:.1f}ms, Confidence: {confidence:.2f}")
                    
                    if node.get('location'):
                        lat, lon = node['location']
                        print(f"     Location: {lat:.2f}, {lon:.2f}")
                
                if len(nodes) > 5:
                    print(f"     ... and {len(nodes) - 5} more nodes")
                print()
        
        # Save detailed results
        timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"hughes_infrastructure_discovery_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(infrastructure, f, indent=2, default=str)
        
        print(f"Detailed results saved to: {filename}")
        print("=" * 80)
    
    def analyze_hughes_routing_patterns(self):
        """Analyze Hughes satellite routing patterns"""
        
        print("\n" + "=" * 80)
        print("HUGHES SATELLITE ROUTING PATTERN ANALYSIS")
        print("=" * 80)
        
        routing_patterns = {}
        
        for target in self.test_targets:
            print(f"\nAnalyzing routing to {target}...")
            
            try:
                route = self.tracer.enhanced_traceroute(target, max_hops=15, packets_per_hop=1)
                
                # Extract routing pattern
                pattern = self._extract_routing_pattern(route)
                routing_patterns[target] = pattern
                
                print(f"  Pattern: {' -> '.join(pattern['hop_types'])}")
                print(f"  Satellite hops: {pattern['satellite_hops']}")
                print(f"  Total RTT: {pattern['total_rtt']:.1f}ms")
                
            except Exception as e:
                print(f"  Error: {e}")
        
        # Analyze common patterns
        self._analyze_common_routing_patterns(routing_patterns)
        
        return routing_patterns
    
    def _extract_routing_pattern(self, route) -> Dict:
        """Extract routing pattern from route"""
        
        pattern = {
            'hop_types': [],
            'satellite_hops': 0,
            'gateway_hops': 0,
            'terrestrial_hops': 0,
            'total_rtt': route.total_rtt,
            'hughes_hops': []
        }
        
        for hop in route.hops:
            pattern['hop_types'].append(hop.hop_type)
            
            if hop.hop_type == 'satellite':
                pattern['satellite_hops'] += 1
            elif hop.hop_type == 'gateway':
                pattern['gateway_hops'] += 1
            else:
                pattern['terrestrial_hops'] += 1
            
            # Check if Hughes hop
            if self._is_hughes_infrastructure(hop):
                pattern['hughes_hops'].append({
                    'hop_number': hop.hop_number,
                    'ip': hop.ip_address,
                    'hostname': hop.hostname,
                    'rtt': hop.avg_rtt
                })
        
        return pattern
    
    def _analyze_common_routing_patterns(self, patterns: Dict):
        """Analyze common routing patterns"""
        
        print("\n" + "-" * 50)
        print("COMMON ROUTING PATTERNS ANALYSIS")
        print("-" * 50)
        
        # Count pattern types
        pattern_counts = {}
        
        for target, pattern in patterns.items():
            pattern_str = ' -> '.join(pattern['hop_types'])
            pattern_counts[pattern_str] = pattern_counts.get(pattern_str, 0) + 1
        
        print("Most common routing patterns:")
        for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {pattern} ({count} occurrences)")
        
        # Analyze Hughes infrastructure usage
        hughes_infrastructure = set()
        for pattern in patterns.values():
            for hop in pattern['hughes_hops']:
                hughes_infrastructure.add(hop['ip'])
        
        print(f"\nUnique Hughes infrastructure nodes in routes: {len(hughes_infrastructure)}")
        
        # Average performance metrics
        avg_satellite_hops = sum(p['satellite_hops'] for p in patterns.values()) / len(patterns)
        avg_total_rtt = sum(p['total_rtt'] for p in patterns.values()) / len(patterns)
        
        print(f"Average satellite hops per route: {avg_satellite_hops:.1f}")
        print(f"Average total RTT: {avg_total_rtt:.1f}ms")

def main():
    """Main function for network discovery"""
    
    discovery = HughesNetworkDiscovery()
    
    print("Hughes Satellite Network Discovery Tool")
    print("Choose analysis type:")
    print("1. Infrastructure Discovery")
    print("2. Routing Pattern Analysis")
    print("3. Full Analysis")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        discovery.discover_hughes_infrastructure()
    elif choice == "2":
        discovery.analyze_hughes_routing_patterns()
    elif choice == "3":
        discovery.discover_hughes_infrastructure()
        discovery.analyze_hughes_routing_patterns()
    else:
        print("Invalid choice. Running full analysis...")
        discovery.discover_hughes_infrastructure()
        discovery.analyze_hughes_routing_patterns()

if __name__ == "__main__":
    main()
