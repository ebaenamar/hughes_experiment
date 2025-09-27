#!/usr/bin/env python3
"""
Satellite Network Topology Mapper

This tool discovers and maps satellite network topology, including
ground stations, gateways, and satellite constellation structure.
"""

import subprocess
import socket
import json
import argparse
import requests
import time
import ipaddress
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import networkx as nx
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
import whois

@dataclass
class NetworkNode:
    """Represents a network node in the satellite topology"""
    ip_address: str
    hostname: Optional[str]
    node_type: str  # 'satellite', 'gateway', 'terrestrial', 'pop'
    location: Optional[Tuple[float, float]]  # (lat, lon)
    asn: Optional[int]
    organization: Optional[str]
    rtt_ms: float
    hop_number: int
    services: List[str]

@dataclass
class NetworkLink:
    """Represents a link between network nodes"""
    source_ip: str
    destination_ip: str
    link_type: str  # 'satellite', 'terrestrial', 'inter_satellite'
    rtt_ms: float
    bandwidth_estimate: Optional[float]
    reliability: float

@dataclass
class SatelliteTopology:
    """Complete satellite network topology"""
    nodes: Dict[str, NetworkNode]
    links: List[NetworkLink]
    ground_stations: List[str]
    satellites: List[str]
    gateways: List[str]
    pops: List[str]

class SatelliteNetworkMapper:
    """Advanced satellite network topology mapper"""
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="satellite_mapper")
        self.known_satellite_asns = {
            7922: "Comcast Cable",
            7018: "AT&T Services",
            3356: "Level 3 Communications",
            174: "Cogent Communications",
            6939: "Hurricane Electric",
            # Hughes specific ASNs
            7155: "Hughes Network Systems",
            22394: "Hughes Network Systems",
        }
        
        self.satellite_indicators = [
            'hughes', 'satellite', 'sat', 'vsat', 'jupiter',
            'spaceway', 'echostar', 'intelsat', 'ses',
            'starlink', 'oneweb', 'telesat'
        ]
        
        self.gateway_indicators = [
            'gateway', 'gw', 'noc', 'teleport', 'hub',
            'earth-station', 'ground-station', 'pop'
        ]
    
    def discover_network_topology(self, target_networks: List[str], 
                                max_depth: int = 3) -> SatelliteTopology:
        """Discover satellite network topology from target networks"""
        
        print(f"Discovering satellite network topology...")
        print(f"Target networks: {target_networks}")
        print(f"Maximum depth: {max_depth}")
        print("-" * 60)
        
        nodes = {}
        links = []
        discovered_ips = set()
        
        # Start discovery from target networks
        for network in target_networks:
            self._discover_from_network(network, nodes, links, discovered_ips, max_depth)
        
        # Classify nodes
        ground_stations, satellites, gateways, pops = self._classify_nodes(nodes)
        
        topology = SatelliteTopology(
            nodes=nodes,
            links=links,
            ground_stations=ground_stations,
            satellites=satellites,
            gateways=gateways,
            pops=pops
        )
        
        self._print_topology_summary(topology)
        return topology
    
    def _discover_from_network(self, network: str, nodes: Dict[str, NetworkNode],
                              links: List[NetworkLink], discovered_ips: Set[str],
                              max_depth: int, current_depth: int = 0):
        """Recursively discover network topology"""
        
        if current_depth >= max_depth:
            return
        
        try:
            # Parse network CIDR
            network_obj = ipaddress.ip_network(network, strict=False)
            
            # Sample IPs from the network (don't scan entire /16)
            sample_ips = self._sample_network_ips(network_obj)
            
            # Discover active hosts
            active_hosts = self._discover_active_hosts(sample_ips)
            
            for ip in active_hosts:
                if ip not in discovered_ips:
                    discovered_ips.add(ip)
                    node = self._analyze_host(ip)
                    if node:
                        nodes[ip] = node
                        
                        # Trace routes to discover links
                        route_links = self._trace_route_links(ip)
                        links.extend(route_links)
                        
                        # Recursively discover connected networks
                        if current_depth < max_depth - 1:
                            connected_networks = self._find_connected_networks(ip)
                            for connected_net in connected_networks:
                                self._discover_from_network(
                                    connected_net, nodes, links, 
                                    discovered_ips, max_depth, current_depth + 1
                                )
        
        except Exception as e:
            print(f"Error discovering network {network}: {e}")
    
    def _sample_network_ips(self, network: ipaddress.IPv4Network, 
                           max_samples: int = 50) -> List[str]:
        """Sample IP addresses from a network"""
        
        if network.num_addresses <= max_samples:
            return [str(ip) for ip in network.hosts()]
        
        # Sample evenly distributed IPs
        step = max(1, network.num_addresses // max_samples)
        sampled_ips = []
        
        for i, ip in enumerate(network.hosts()):
            if i % step == 0:
                sampled_ips.append(str(ip))
            if len(sampled_ips) >= max_samples:
                break
        
        return sampled_ips
    
    def _discover_active_hosts(self, ip_list: List[str]) -> List[str]:
        """Discover active hosts from IP list using parallel ping"""
        
        active_hosts = []
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_ip = {executor.submit(self._ping_host, ip): ip for ip in ip_list}
            
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    if future.result():
                        active_hosts.append(ip)
                        print(f"Active host found: {ip}")
                except Exception as e:
                    pass  # Ignore ping failures
        
        return active_hosts
    
    def _ping_host(self, ip: str, timeout: int = 2) -> bool:
        """Check if host is active using ping"""
        
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', str(timeout * 1000), ip],
                capture_output=True, text=True, timeout=timeout + 1
            )
            return result.returncode == 0
        except:
            return False
    
    def _analyze_host(self, ip: str) -> Optional[NetworkNode]:
        """Analyze a host to determine its characteristics"""
        
        try:
            # Get hostname
            hostname = None
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except:
                pass
            
            # Determine node type
            node_type = self._classify_node_type(ip, hostname)
            
            # Get geolocation
            location = self._get_location(ip)
            
            # Get ASN and organization
            asn, organization = self._get_asn_info(ip)
            
            # Measure RTT
            rtt = self._measure_rtt(ip)
            
            # Detect services
            services = self._detect_services(ip)
            
            return NetworkNode(
                ip_address=ip,
                hostname=hostname,
                node_type=node_type,
                location=location,
                asn=asn,
                organization=organization,
                rtt_ms=rtt,
                hop_number=0,  # Will be updated during traceroute
                services=services
            )
            
        except Exception as e:
            print(f"Error analyzing host {ip}: {e}")
            return None
    
    def _classify_node_type(self, ip: str, hostname: Optional[str]) -> str:
        """Classify node type based on IP and hostname"""
        
        if hostname:
            hostname_lower = hostname.lower()
            
            # Check for satellite indicators
            if any(indicator in hostname_lower for indicator in self.satellite_indicators):
                return 'satellite'
            
            # Check for gateway indicators
            if any(indicator in hostname_lower for indicator in self.gateway_indicators):
                return 'gateway'
            
            # Check for PoP indicators
            if 'pop' in hostname_lower or 'point-of-presence' in hostname_lower:
                return 'pop'
        
        # Default classification based on RTT will be done later
        return 'unknown'
    
    def _get_location(self, ip: str) -> Optional[Tuple[float, float]]:
        """Get geolocation for IP address"""
        
        try:
            # Use IP geolocation API
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    return (data['lat'], data['lon'])
        except:
            pass
        
        return None
    
    def _get_asn_info(self, ip: str) -> Tuple[Optional[int], Optional[str]]:
        """Get ASN and organization information"""
        
        try:
            # Use whois to get ASN info
            w = whois.whois(ip)
            if hasattr(w, 'asn') and w.asn:
                asn = int(w.asn[0]) if isinstance(w.asn, list) else int(w.asn)
                org = w.org[0] if isinstance(w.org, list) else w.org
                return asn, org
        except:
            pass
        
        return None, None
    
    def _measure_rtt(self, ip: str) -> float:
        """Measure RTT to host"""
        
        try:
            result = subprocess.run(
                ['ping', '-c', '3', ip],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                # Parse average RTT from ping output
                for line in result.stdout.split('\n'):
                    if 'avg' in line and 'ms' in line:
                        parts = line.split('/')
                        if len(parts) >= 5:
                            return float(parts[4])
        except:
            pass
        
        return 0.0
    
    def _detect_services(self, ip: str) -> List[str]:
        """Detect running services on host"""
        
        services = []
        common_ports = [22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
        
        for port in common_ports:
            if self._check_port(ip, port):
                service_name = self._get_service_name(port)
                services.append(f"{service_name}:{port}")
        
        return services
    
    def _check_port(self, ip: str, port: int, timeout: int = 2) -> bool:
        """Check if port is open"""
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _get_service_name(self, port: int) -> str:
        """Get service name for port"""
        
        service_map = {
            22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
            80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS',
            993: 'IMAPS', 995: 'POP3S'
        }
        
        return service_map.get(port, f'Port{port}')
    
    def _trace_route_links(self, destination: str) -> List[NetworkLink]:
        """Trace route and extract network links"""
        
        links = []
        
        try:
            result = subprocess.run(
                ['traceroute', '-n', destination],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                prev_ip = None
                
                for line in lines[1:]:  # Skip header
                    parts = line.split()
                    if len(parts) >= 3 and parts[1] != '*':
                        current_ip = parts[1]
                        
                        # Extract RTT
                        rtt = 0.0
                        for part in parts[2:]:
                            if 'ms' in part:
                                try:
                                    rtt = float(part.replace('ms', ''))
                                    break
                                except:
                                    continue
                        
                        if prev_ip and current_ip != prev_ip:
                            link_type = self._classify_link_type(prev_ip, current_ip, rtt)
                            
                            link = NetworkLink(
                                source_ip=prev_ip,
                                destination_ip=current_ip,
                                link_type=link_type,
                                rtt_ms=rtt,
                                bandwidth_estimate=None,
                                reliability=1.0  # Default, would need measurement
                            )
                            links.append(link)
                        
                        prev_ip = current_ip
        
        except Exception as e:
            print(f"Error tracing route to {destination}: {e}")
        
        return links
    
    def _classify_link_type(self, source_ip: str, dest_ip: str, rtt: float) -> str:
        """Classify link type based on IPs and RTT"""
        
        # High RTT suggests satellite link
        if rtt > 200:
            return 'satellite'
        elif rtt > 100:
            return 'possible_satellite'
        else:
            return 'terrestrial'
    
    def _find_connected_networks(self, ip: str) -> List[str]:
        """Find networks connected to this IP"""
        
        # This would involve BGP route analysis or other advanced techniques
        # For now, return empty list
        return []
    
    def _classify_nodes(self, nodes: Dict[str, NetworkNode]) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Classify nodes into categories"""
        
        ground_stations = []
        satellites = []
        gateways = []
        pops = []
        
        for ip, node in nodes.items():
            if node.node_type == 'satellite' or node.rtt_ms > 200:
                satellites.append(ip)
            elif node.node_type == 'gateway':
                gateways.append(ip)
            elif node.node_type == 'pop':
                pops.append(ip)
            elif 'ground' in (node.hostname or '').lower():
                ground_stations.append(ip)
        
        return ground_stations, satellites, gateways, pops
    
    def _print_topology_summary(self, topology: SatelliteTopology):
        """Print topology discovery summary"""
        
        print("\n" + "=" * 80)
        print("SATELLITE NETWORK TOPOLOGY SUMMARY")
        print("=" * 80)
        print(f"Total Nodes Discovered: {len(topology.nodes)}")
        print(f"Total Links Discovered: {len(topology.links)}")
        print()
        print("Node Classification:")
        print(f"  🛰️  Satellites:      {len(topology.satellites)}")
        print(f"  🌐 Gateways:        {len(topology.gateways)}")
        print(f"  📡 Ground Stations: {len(topology.ground_stations)}")
        print(f"  🏢 PoPs:            {len(topology.pops)}")
        print()
        
        # Print sample nodes
        print("Sample Discovered Nodes:")
        for i, (ip, node) in enumerate(list(topology.nodes.items())[:10]):
            hostname = f" ({node.hostname})" if node.hostname else ""
            location = f" [{node.location[0]:.2f}, {node.location[1]:.2f}]" if node.location else ""
            print(f"  {node.node_type:12} {ip:15}{hostname}{location}")
        
        if len(topology.nodes) > 10:
            print(f"  ... and {len(topology.nodes) - 10} more nodes")
        
        print("=" * 80)
    
    def visualize_topology(self, topology: SatelliteTopology, filename: str = None):
        """Create network topology visualization"""
        
        G = nx.Graph()
        
        # Add nodes
        for ip, node in topology.nodes.items():
            G.add_node(ip, 
                      node_type=node.node_type,
                      hostname=node.hostname,
                      rtt=node.rtt_ms)
        
        # Add edges
        for link in topology.links:
            G.add_edge(link.source_ip, link.destination_ip,
                      link_type=link.link_type,
                      rtt=link.rtt_ms)
        
        # Create visualization
        plt.figure(figsize=(16, 12))
        
        # Position nodes using spring layout
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Color nodes by type
        node_colors = []
        for node in G.nodes():
            node_type = topology.nodes[node].node_type
            if node_type == 'satellite':
                node_colors.append('red')
            elif node_type == 'gateway':
                node_colors.append('blue')
            elif node_type == 'pop':
                node_colors.append('green')
            else:
                node_colors.append('gray')
        
        # Draw network
        nx.draw(G, pos, 
                node_color=node_colors,
                node_size=300,
                with_labels=False,
                edge_color='lightgray',
                alpha=0.7)
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                      markersize=10, label='Satellite'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', 
                      markersize=10, label='Gateway'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', 
                      markersize=10, label='PoP'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', 
                      markersize=10, label='Other')
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.title('Satellite Network Topology', fontsize=16)
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Topology visualization saved as {filename}")
        else:
            plt.show()
    
    def export_topology(self, topology: SatelliteTopology, filename: str):
        """Export topology to JSON file"""
        
        export_data = {
            'nodes': {ip: asdict(node) for ip, node in topology.nodes.items()},
            'links': [asdict(link) for link in topology.links],
            'summary': {
                'total_nodes': len(topology.nodes),
                'total_links': len(topology.links),
                'satellites': len(topology.satellites),
                'gateways': len(topology.gateways),
                'ground_stations': len(topology.ground_stations),
                'pops': len(topology.pops)
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Topology exported to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Satellite Network Topology Mapper')
    parser.add_argument('networks', nargs='+', help='Target networks to discover (CIDR format)')
    parser.add_argument('--max-depth', type=int, default=3,
                       help='Maximum discovery depth (default: 3)')
    parser.add_argument('--visualize', action='store_true',
                       help='Generate topology visualization')
    parser.add_argument('--export', type=str,
                       help='Export topology to JSON file')
    parser.add_argument('--plot-file', type=str,
                       help='Save visualization to file')
    
    args = parser.parse_args()
    
    mapper = SatelliteNetworkMapper()
    topology = mapper.discover_network_topology(args.networks, args.max_depth)
    
    if args.visualize:
        mapper.visualize_topology(topology, args.plot_file)
    
    if args.export:
        mapper.export_topology(topology, args.export)

if __name__ == '__main__':
    main()
