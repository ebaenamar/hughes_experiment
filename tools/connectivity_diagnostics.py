#!/usr/bin/env python3
"""
Connectivity Diagnostics for Filtered Networks

This tool diagnoses connectivity issues when traditional network tools
are blocked or filtered, common in satellite and corporate networks.
"""

import subprocess
import socket
import time
import json
import argparse
import threading
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import urllib.request
import urllib.error
import ssl

@dataclass
class ConnectivityTest:
    """Result of a connectivity test"""
    test_name: str
    success: bool
    rtt_ms: Optional[float]
    error_message: Optional[str]
    details: Dict

class ConnectivityDiagnostics:
    """Comprehensive connectivity diagnostics for filtered networks"""
    
    def __init__(self):
        self.timeout = 10
        self.test_results = []
        
    def run_full_diagnostics(self, target: str) -> Dict:
        """Run comprehensive connectivity diagnostics"""
        
        print("=" * 80)
        print("CONNECTIVITY DIAGNOSTICS FOR FILTERED NETWORKS")
        print("=" * 80)
        print(f"Target: {target}")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {
            'target': target,
            'timestamp': time.time(),
            'tests': {}
        }
        
        # Test 1: Basic ICMP connectivity
        print("Test 1: ICMP Connectivity (Ping)")
        print("-" * 40)
        icmp_result = self._test_icmp_connectivity(target)
        results['tests']['icmp'] = icmp_result
        self._print_test_result(icmp_result)
        
        # Test 2: DNS Resolution
        print("\nTest 2: DNS Resolution")
        print("-" * 40)
        dns_result = self._test_dns_resolution(target)
        results['tests']['dns'] = dns_result
        self._print_test_result(dns_result)
        
        # Test 3: TCP Connectivity
        print("\nTest 3: TCP Port Connectivity")
        print("-" * 40)
        tcp_result = self._test_tcp_connectivity(target)
        results['tests']['tcp'] = tcp_result
        self._print_test_result(tcp_result)
        
        # Test 4: HTTP/HTTPS Connectivity
        print("\nTest 4: HTTP/HTTPS Connectivity")
        print("-" * 40)
        http_result = self._test_http_connectivity(target)
        results['tests']['http'] = http_result
        self._print_test_result(http_result)
        
        # Test 5: Traceroute Analysis
        print("\nTest 5: Traceroute Analysis")
        print("-" * 40)
        traceroute_result = self._test_traceroute(target)
        results['tests']['traceroute'] = traceroute_result
        self._print_test_result(traceroute_result)
        
        # Test 6: MTU Discovery
        print("\nTest 6: MTU Path Discovery")
        print("-" * 40)
        mtu_result = self._test_mtu_discovery(target)
        results['tests']['mtu'] = mtu_result
        self._print_test_result(mtu_result)
        
        # Test 7: Firewall Detection
        print("\nTest 7: Firewall/Filtering Detection")
        print("-" * 40)
        firewall_result = self._test_firewall_detection(target)
        results['tests']['firewall'] = firewall_result
        self._print_test_result(firewall_result)
        
        # Generate summary
        print("\n" + "=" * 80)
        print("DIAGNOSTIC SUMMARY")
        print("=" * 80)
        self._generate_diagnostic_summary(results)
        
        return results
    
    def _test_icmp_connectivity(self, target: str) -> ConnectivityTest:
        """Test basic ICMP connectivity"""
        
        try:
            # Try multiple ping attempts
            rtts = []
            
            for i in range(5):
                cmd = ['ping', '-c', '1', '-W', '5000', target]
                
                start_time = time.time()
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                end_time = time.time()
                
                if result.returncode == 0:
                    # Extract RTT from output
                    for line in result.stdout.split('\n'):
                        if 'time=' in line:
                            try:
                                rtt = float(line.split('time=')[1].split()[0])
                                rtts.append(rtt)
                                break
                            except:
                                pass
            
            if rtts:
                avg_rtt = sum(rtts) / len(rtts)
                success_rate = len(rtts) / 5 * 100
                
                return ConnectivityTest(
                    test_name="ICMP Ping",
                    success=True,
                    rtt_ms=avg_rtt,
                    error_message=None,
                    details={
                        'packets_sent': 5,
                        'packets_received': len(rtts),
                        'success_rate': success_rate,
                        'min_rtt': min(rtts),
                        'max_rtt': max(rtts),
                        'avg_rtt': avg_rtt
                    }
                )
            else:
                return ConnectivityTest(
                    test_name="ICMP Ping",
                    success=False,
                    rtt_ms=None,
                    error_message="All ping packets lost",
                    details={'packets_sent': 5, 'packets_received': 0}
                )
                
        except Exception as e:
            return ConnectivityTest(
                test_name="ICMP Ping",
                success=False,
                rtt_ms=None,
                error_message=str(e),
                details={}
            )
    
    def _test_dns_resolution(self, target: str) -> ConnectivityTest:
        """Test DNS resolution"""
        
        try:
            start_time = time.time()
            ip_address = socket.gethostbyname(target)
            end_time = time.time()
            
            rtt = (end_time - start_time) * 1000
            
            # Try reverse DNS
            try:
                reverse_start = time.time()
                hostname = socket.gethostbyaddr(ip_address)[0]
                reverse_end = time.time()
                reverse_rtt = (reverse_end - reverse_start) * 1000
            except:
                hostname = None
                reverse_rtt = None
            
            return ConnectivityTest(
                test_name="DNS Resolution",
                success=True,
                rtt_ms=rtt,
                error_message=None,
                details={
                    'ip_address': ip_address,
                    'reverse_hostname': hostname,
                    'forward_rtt': rtt,
                    'reverse_rtt': reverse_rtt
                }
            )
            
        except Exception as e:
            return ConnectivityTest(
                test_name="DNS Resolution",
                success=False,
                rtt_ms=None,
                error_message=str(e),
                details={}
            )
    
    def _test_tcp_connectivity(self, target: str) -> ConnectivityTest:
        """Test TCP connectivity to common ports"""
        
        common_ports = [80, 443, 22, 25, 53, 110, 143, 993, 995]
        open_ports = []
        closed_ports = []
        filtered_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                
                start_time = time.time()
                result = sock.connect_ex((target, port))
                end_time = time.time()
                
                rtt = (end_time - start_time) * 1000
                
                if result == 0:
                    open_ports.append({'port': port, 'rtt': rtt})
                else:
                    if rtt < 100:  # Quick response suggests active rejection
                        closed_ports.append(port)
                    else:  # Slow response suggests filtering
                        filtered_ports.append(port)
                
                sock.close()
                
            except socket.timeout:
                filtered_ports.append(port)
            except Exception:
                closed_ports.append(port)
        
        success = len(open_ports) > 0
        avg_rtt = sum(p['rtt'] for p in open_ports) / len(open_ports) if open_ports else None
        
        return ConnectivityTest(
            test_name="TCP Connectivity",
            success=success,
            rtt_ms=avg_rtt,
            error_message=None if success else "No TCP ports accessible",
            details={
                'open_ports': open_ports,
                'closed_ports': closed_ports,
                'filtered_ports': filtered_ports,
                'total_tested': len(common_ports)
            }
        )
    
    def _test_http_connectivity(self, target: str) -> ConnectivityTest:
        """Test HTTP/HTTPS connectivity"""
        
        protocols = ['http', 'https']
        results = {}
        
        for protocol in protocols:
            try:
                url = f"{protocol}://{target}"
                
                # Create SSL context that ignores certificate errors
                if protocol == 'https':
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    
                    start_time = time.time()
                    response = urllib.request.urlopen(url, timeout=self.timeout, context=ctx)
                    end_time = time.time()
                else:
                    start_time = time.time()
                    response = urllib.request.urlopen(url, timeout=self.timeout)
                    end_time = time.time()
                
                rtt = (end_time - start_time) * 1000
                
                results[protocol] = {
                    'success': True,
                    'status_code': response.getcode(),
                    'rtt': rtt,
                    'content_length': len(response.read()),
                    'headers': dict(response.headers)
                }
                
            except urllib.error.HTTPError as e:
                results[protocol] = {
                    'success': False,
                    'error': f"HTTP {e.code}: {e.reason}",
                    'status_code': e.code
                }
            except Exception as e:
                results[protocol] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Determine overall success
        success = any(r.get('success', False) for r in results.values())
        successful_results = [r for r in results.values() if r.get('success', False)]
        avg_rtt = sum(r['rtt'] for r in successful_results) / len(successful_results) if successful_results else None
        
        return ConnectivityTest(
            test_name="HTTP/HTTPS",
            success=success,
            rtt_ms=avg_rtt,
            error_message=None if success else "No HTTP/HTTPS connectivity",
            details=results
        )
    
    def _test_traceroute(self, target: str) -> ConnectivityTest:
        """Test if traceroute works"""
        
        try:
            cmd = ['traceroute', '-n', '-m', '10', target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                hops = []
                
                for line in lines[1:]:  # Skip header
                    if line.strip() and not line.startswith('traceroute'):
                        parts = line.split()
                        if len(parts) >= 2:
                            hop_num = parts[0]
                            if parts[1] != '*':
                                hops.append({
                                    'hop': hop_num,
                                    'ip': parts[1],
                                    'responsive': True
                                })
                            else:
                                hops.append({
                                    'hop': hop_num,
                                    'ip': None,
                                    'responsive': False
                                })
                
                success = len([h for h in hops if h['responsive']]) > 0
                
                return ConnectivityTest(
                    test_name="Traceroute",
                    success=success,
                    rtt_ms=None,
                    error_message=None if success else "No responsive hops found",
                    details={
                        'total_hops': len(hops),
                        'responsive_hops': len([h for h in hops if h['responsive']]),
                        'hops': hops
                    }
                )
            else:
                return ConnectivityTest(
                    test_name="Traceroute",
                    success=False,
                    rtt_ms=None,
                    error_message="Traceroute command failed",
                    details={'stderr': result.stderr}
                )
                
        except Exception as e:
            return ConnectivityTest(
                test_name="Traceroute",
                success=False,
                rtt_ms=None,
                error_message=str(e),
                details={}
            )
    
    def _test_mtu_discovery(self, target: str) -> ConnectivityTest:
        """Test MTU path discovery"""
        
        mtu_sizes = [1500, 1400, 1300, 1200, 1100, 1000, 576]
        working_mtu = None
        
        for mtu in mtu_sizes:
            try:
                # Use ping with Don't Fragment flag
                cmd = ['ping', '-c', '1', '-s', str(mtu - 28), '-M', 'do', target]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    working_mtu = mtu
                    break
                    
            except Exception:
                continue
        
        success = working_mtu is not None
        
        return ConnectivityTest(
            test_name="MTU Discovery",
            success=success,
            rtt_ms=None,
            error_message=None if success else "No working MTU size found",
            details={
                'working_mtu': working_mtu,
                'tested_sizes': mtu_sizes
            }
        )
    
    def _test_firewall_detection(self, target: str) -> ConnectivityTest:
        """Detect firewall/filtering behavior"""
        
        # Test different protocols and behaviors
        detection_results = {}
        
        # Test 1: TCP SYN scan behavior
        filtered_ports = 0
        closed_ports = 0
        open_ports = 0
        
        test_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 993, 995]
        
        for port in test_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                
                start_time = time.time()
                result = sock.connect_ex((target, port))
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                
                if result == 0:
                    open_ports += 1
                elif response_time > 2000:  # Slow response suggests filtering
                    filtered_ports += 1
                else:
                    closed_ports += 1
                
                sock.close()
                
            except socket.timeout:
                filtered_ports += 1
            except Exception:
                closed_ports += 1
        
        detection_results['port_scan'] = {
            'open_ports': open_ports,
            'closed_ports': closed_ports,
            'filtered_ports': filtered_ports,
            'total_tested': len(test_ports)
        }
        
        # Test 2: ICMP filtering
        try:
            cmd = ['ping', '-c', '3', target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            icmp_works = result.returncode == 0
        except:
            icmp_works = False
        
        detection_results['icmp_filtering'] = not icmp_works
        
        # Test 3: Traceroute filtering
        try:
            cmd = ['traceroute', '-n', '-m', '5', target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            traceroute_works = result.returncode == 0 and '*' not in result.stdout
        except:
            traceroute_works = False
        
        detection_results['traceroute_filtering'] = not traceroute_works
        
        # Analyze results
        firewall_indicators = []
        
        if filtered_ports > closed_ports:
            firewall_indicators.append("High port filtering detected")
        
        if not icmp_works:
            firewall_indicators.append("ICMP traffic blocked")
        
        if not traceroute_works:
            firewall_indicators.append("Traceroute traffic blocked")
        
        if filtered_ports > 5:
            firewall_indicators.append("Stateful firewall likely present")
        
        success = len(firewall_indicators) > 0
        
        return ConnectivityTest(
            test_name="Firewall Detection",
            success=success,
            rtt_ms=None,
            error_message=None,
            details={
                'indicators': firewall_indicators,
                'detection_results': detection_results,
                'firewall_likely': success
            }
        )
    
    def _print_test_result(self, test: ConnectivityTest):
        """Print formatted test result"""
        
        status = "✅ PASS" if test.success else "❌ FAIL"
        print(f"{status} {test.test_name}")
        
        if test.rtt_ms:
            print(f"    RTT: {test.rtt_ms:.1f}ms")
        
        if test.error_message:
            print(f"    Error: {test.error_message}")
        
        # Print key details
        if test.details:
            for key, value in test.details.items():
                if key in ['ip_address', 'working_mtu', 'success_rate', 'open_ports']:
                    print(f"    {key}: {value}")
    
    def _generate_diagnostic_summary(self, results: Dict):
        """Generate diagnostic summary and recommendations"""
        
        tests = results['tests']
        
        print("Connection Status:")
        
        # Basic connectivity
        if tests['icmp']['success']:
            print("  ✅ Basic ICMP connectivity: WORKING")
        else:
            print("  ❌ Basic ICMP connectivity: BLOCKED")
        
        if tests['dns']['success']:
            print("  ✅ DNS resolution: WORKING")
        else:
            print("  ❌ DNS resolution: FAILED")
        
        if tests['tcp']['success']:
            open_ports = len(tests['tcp']['details'].get('open_ports', []))
            print(f"  ✅ TCP connectivity: WORKING ({open_ports} ports accessible)")
        else:
            print("  ❌ TCP connectivity: BLOCKED")
        
        if tests['http']['success']:
            print("  ✅ HTTP/HTTPS connectivity: WORKING")
        else:
            print("  ❌ HTTP/HTTPS connectivity: BLOCKED")
        
        print("\nNetwork Characteristics:")
        
        # Analyze RTT for satellite detection
        rtts = []
        for test_name, test_data in tests.items():
            if test_data.get('rtt_ms'):
                rtts.append(test_data['rtt_ms'])
        
        if rtts:
            avg_rtt = sum(rtts) / len(rtts)
            min_rtt = min(rtts)
            
            if min_rtt > 200:
                print(f"  🛰️  Satellite connection detected (min RTT: {min_rtt:.1f}ms)")
                print("      - Likely geostationary satellite (GEO)")
                print("      - Expected high latency for all traffic")
            elif min_rtt > 60:
                print(f"  🛰️  Possible satellite connection (min RTT: {min_rtt:.1f}ms)")
                print("      - Could be MEO satellite or long terrestrial path")
            else:
                print(f"  🌍 Terrestrial connection (min RTT: {min_rtt:.1f}ms)")
        
        # Filtering analysis
        print("\nFiltering Analysis:")
        
        if not tests['traceroute']['success']:
            print("  🚫 Traceroute traffic is blocked")
            print("      - Network path discovery limited")
            print("      - Use alternative analysis methods")
        
        if tests['firewall']['success']:
            indicators = tests['firewall']['details'].get('indicators', [])
            for indicator in indicators:
                print(f"  🔥 {indicator}")
        
        # Recommendations
        print("\nRecommendations:")
        
        if not tests['traceroute']['success']:
            print("  • Use alternative tracing methods (TCP, HTTP)")
            print("  • Focus on timing analysis for satellite detection")
            print("  • Use service-specific connectivity tests")
        
        if tests['firewall']['success']:
            print("  • Network has active filtering/firewall")
            print("  • Some analysis tools may not work as expected")
            print("  • Use application-layer testing when possible")
        
        if any(rtt > 200 for rtt in rtts if rtts):
            print("  • Satellite connection detected:")
            print("    - Expect high latency (200-600ms)")
            print("    - Optimize applications for high RTT")
            print("    - Consider TCP acceleration")

def main():
    parser = argparse.ArgumentParser(description='Connectivity Diagnostics for Filtered Networks')
    parser.add_argument('target', help='Target hostname or IP address')
    parser.add_argument('--output', type=str, help='Save results to JSON file')
    
    args = parser.parse_args()
    
    diagnostics = ConnectivityDiagnostics()
    results = diagnostics.run_full_diagnostics(args.target)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved to {args.output}")

if __name__ == '__main__':
    main()
