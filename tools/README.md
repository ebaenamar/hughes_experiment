# Satellite Network Analysis Tools

This directory contains advanced tools for analyzing Hughes satellite network packet routing, delays, and performance characteristics.

## Tools Overview

### 1. satellite_tracer.py
Advanced packet tracing tool specifically designed for satellite networks.

**Features:**
- Enhanced traceroute with satellite-specific analysis
- Automatic classification of hops (satellite, gateway, terrestrial)
- Delay analysis and satellite segment identification
- Continuous monitoring capabilities
- Real-time hop classification with visual indicators

**Usage:**
```bash
# Basic satellite trace
python satellite_tracer.py google.com

# Extended analysis with more packets per hop
python satellite_tracer.py --max-hops 25 --packets 5 8.8.8.8

# Continuous monitoring
python satellite_tracer.py --monitor --interval 60 --duration 3600 satellite.example.com
```

**Example Output:**
```
 1  🌍 192.168.1.1 (router.local)
     RTT: 1.2ms 1.1ms 1.3ms (avg: 1.2ms)

 2  🌍 10.0.0.1 (isp-gateway.net)
     RTT: 15.2ms 14.8ms 15.5ms (avg: 15.2ms)

 3  🛰️  74.192.45.123 (hughes-sat-gw.net)
     RTT: 245.1ms 244.8ms 246.2ms (avg: 245.4ms)

 4  🛰️  162.248.12.45 (jupiter-sat.hughes.net)
     RTT: 248.3ms 247.9ms 249.1ms (avg: 248.4ms)
```

### 2. delay_analyzer.py
Comprehensive delay analysis tool for satellite networks.

**Features:**
- Statistical analysis of RTT, jitter, and packet loss
- Satellite type classification (GEO/MEO/LEO)
- Delay component breakdown
- Continuous monitoring with trend analysis
- Performance visualization and reporting

**Usage:**
```bash
# Basic delay analysis
python delay_analyzer.py google.com

# Extended analysis with more packets
python delay_analyzer.py --count 200 --interval 0.5 satellite.example.com

# Continuous monitoring
python delay_analyzer.py --monitor --duration 7200 target.com

# Generate performance plots
python delay_analyzer.py --plot --output delay_analysis.png target.com
```

**Key Metrics:**
- **Minimum RTT**: Baseline propagation delay
- **Average RTT**: Typical performance
- **Jitter**: Network stability indicator
- **Packet Loss**: Connection reliability
- **Excess Delay**: Processing and queuing delays

### 3. network_mapper.py
Network topology discovery and mapping tool.

**Features:**
- Automated discovery of satellite network topology
- Node classification (satellites, gateways, PoPs)
- Geolocation mapping of network infrastructure
- ASN and organization identification
- Network visualization and export

**Usage:**
```bash
# Discover topology from network ranges
python network_mapper.py 74.192.0.0/16 162.248.0.0/16

# Extended discovery with visualization
python network_mapper.py --max-depth 4 --visualize --export topology.json 69.46.0.0/16

# Generate network map
python network_mapper.py --visualize --plot-file network_map.png 67.15.0.0/16
```

**Output:**
- Network topology graph
- Node classification report
- Geographic distribution map
- JSON export for further analysis

### 4. performance_monitor.py
Real-time satellite network performance monitoring.

**Features:**
- Continuous performance monitoring
- Real-time alerting system
- Bandwidth utilization tracking
- Connection quality assessment
- Performance dashboard and reporting

**Usage:**
```bash
# Basic monitoring
python performance_monitor.py google.com 8.8.8.8

# Custom alert thresholds
python performance_monitor.py --max-rtt 500 --max-loss 2 --interval 15 target.com

# Real-time dashboard
python performance_monitor.py --dashboard target.com

# Extended monitoring with custom thresholds
python performance_monitor.py --max-rtt 800 --max-jitter 30 --duration 7200 satellite.example.com
```

**Alert Types:**
- High RTT (>threshold)
- High packet loss (>threshold)
- High jitter (>threshold)
- Low bandwidth (download/upload)
- Connection quality degradation

## Installation

1. Install Python dependencies:
```bash
pip install -r ../requirements.txt
```

2. Ensure system tools are available:
```bash
# macOS
brew install traceroute

# Linux (usually pre-installed)
sudo apt-get install traceroute iputils-ping
```

3. Make scripts executable:
```bash
chmod +x *.py
```

## Common Use Cases

### 1. Hughes Satellite Connection Analysis
```bash
# Trace route through Hughes network
python satellite_tracer.py --max-hops 30 your-target.com

# Analyze delay characteristics
python delay_analyzer.py --count 100 --plot your-target.com

# Monitor performance over time
python performance_monitor.py --interval 30 --duration 3600 your-target.com
```

### 2. Network Topology Discovery
```bash
# Discover Hughes network infrastructure
python network_mapper.py 74.192.0.0/16 162.248.0.0/16 69.46.0.0/16

# Visualize network topology
python network_mapper.py --visualize --export hughes_topology.json 67.15.0.0/16
```

### 3. Performance Baseline Establishment
```bash
# Establish performance baselines
python delay_analyzer.py --count 500 --interval 1.0 target1.com
python delay_analyzer.py --count 500 --interval 1.0 target2.com
python delay_analyzer.py --count 500 --interval 1.0 target3.com
```

### 4. Continuous Monitoring Setup
```bash
# Set up continuous monitoring with alerts
python performance_monitor.py \
  --max-rtt 600 \
  --max-loss 3 \
  --max-jitter 40 \
  --interval 30 \
  --duration 86400 \
  primary-target.com backup-target.com
```

## Understanding Satellite Network Characteristics

### Geostationary (GEO) Satellites
- **Altitude**: ~35,786 km
- **Typical RTT**: 240-280ms minimum
- **Coverage**: Large area, fixed position
- **Examples**: Hughes Jupiter, Intelsat, SES

### Medium Earth Orbit (MEO) Satellites
- **Altitude**: 2,000-35,786 km
- **Typical RTT**: 80-150ms
- **Coverage**: Regional, moving
- **Examples**: O3b, GPS constellation

### Low Earth Orbit (LEO) Satellites
- **Altitude**: 160-2,000 km
- **Typical RTT**: 20-80ms
- **Coverage**: Small area, fast moving
- **Examples**: Starlink, OneWeb, Telesat

### Key Performance Indicators

1. **RTT (Round Trip Time)**
   - GEO: >240ms indicates satellite hop
   - Processing delays add to base propagation time

2. **Jitter**
   - <10ms: Excellent stability
   - 10-30ms: Good stability
   - >30ms: Possible congestion or interference

3. **Packet Loss**
   - <1%: Excellent
   - 1-3%: Good
   - >5%: Poor (weather, interference, congestion)

4. **Hop Classification**
   - High RTT jumps (>200ms) indicate satellite segments
   - Hostname analysis reveals network infrastructure
   - Geographic distribution shows ground station locations

## Troubleshooting

### Common Issues

1. **Permission Errors**
   - Some tools require root/admin privileges for raw sockets
   - Use `sudo` on Linux/macOS if needed

2. **Network Timeouts**
   - Satellite networks have high latency
   - Increase timeout values for better results

3. **Rate Limiting**
   - Some networks implement rate limiting
   - Increase intervals between measurements

4. **Firewall Blocking**
   - ICMP may be blocked by firewalls
   - Try different target hosts or protocols

### Performance Optimization

1. **Measurement Accuracy**
   - Use multiple measurements for statistical validity
   - Account for network congestion variations
   - Consider time-of-day effects

2. **Resource Usage**
   - Limit concurrent measurements
   - Use appropriate sampling intervals
   - Monitor system resource usage

## Data Export and Analysis

All tools support data export in JSON format for further analysis:

```bash
# Export network topology
python network_mapper.py --export topology.json target-networks

# Export performance data
python performance_monitor.py --duration 3600 target.com
# Creates: satellite_performance_report_<timestamp>.json

# Export delay analysis
python delay_analyzer.py --count 200 target.com
# Creates: delay_analysis_<target>.json
```

## Integration with Other Tools

The tools can be integrated with:
- **Grafana**: For dashboard visualization
- **InfluxDB**: For time-series data storage
- **Nagios/Zabbix**: For network monitoring
- **Custom scripts**: Via JSON data export

## Contributing

When contributing to these tools:
1. Follow PEP 8 style guidelines
2. Add comprehensive error handling
3. Include docstrings and type hints
4. Test with various satellite network types
5. Document new features and usage examples
