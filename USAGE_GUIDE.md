# Hughes Satellite Research - Practical Usage Guide

## Quick Start

This guide provides practical examples for analyzing Hughes satellite network packet routing and delays.

### Prerequisites

1. **Install Dependencies**
```bash
cd /Users/e.baena/CascadeProjects/hughes-satellite-research
pip install -r requirements.txt
```

2. **Make Scripts Executable**
```bash
chmod +x tools/*.py examples/*.py
```

3. **Verify System Tools**
```bash
# Check if traceroute is available
which traceroute

# Check if ping is available  
which ping
```

## Basic Analysis Workflow

### Step 1: Quick Satellite Detection
```bash
# Quick check if your connection uses satellite
python examples/basic_analysis.py google.com quick
```

**Expected Output:**
```
Quick satellite check for google.com...
RTT: 245.2ms
✓ Satellite connection detected (GEO)
```

### Step 2: Comprehensive Route Analysis
```bash
# Full packet routing analysis
python tools/satellite_tracer.py google.com
```

**Expected Output:**
```
 1  🌍 192.168.1.1 (home-router.local)
     RTT: 1.2ms 1.1ms 1.3ms (avg: 1.2ms)

 2  🌍 10.0.0.1 (isp-local.net)
     RTT: 15.2ms 14.8ms 15.5ms (avg: 15.2ms)

 3  🌐 74.192.45.123 (hughes-gateway.net)
     RTT: 25.1ms 24.8ms 25.2ms (avg: 25.0ms)

 4  🛰️  162.248.12.45 (jupiter-sat.hughes.net)
     RTT: 245.1ms 244.8ms 246.2ms (avg: 245.4ms)

 5  🛰️  162.248.15.67 (sat-routing.hughes.net)
     RTT: 248.3ms 247.9ms 249.1ms (avg: 248.4ms)

 6  🌐 8.8.8.8
     RTT: 252.1ms 251.8ms 252.5ms (avg: 252.1ms)
```

### Step 3: Delay Analysis
```bash
# Detailed delay characteristics
python tools/delay_analyzer.py google.com --count 100
```

**Expected Output:**
```
SATELLITE DELAY ANALYSIS REPORT
================================================================================
Target: google.com
Total Measurements: 100
Successful Measurements: 98
Packet Loss Rate: 2.00%

DELAY STATISTICS:
  Minimum RTT:      242.15 ms
  Maximum RTT:      287.43 ms
  Average RTT:      251.32 ms
  Median RTT:       249.87 ms
  Standard Dev:      12.45 ms
  Jitter:            8.23 ms

SATELLITE ANALYSIS:
  Detected Type:   GEO
  Theoretical Min:   240.00 ms
  Excess Delay:      11.32 ms
```

## Advanced Analysis Examples

### Network Infrastructure Discovery
```bash
# Discover Hughes network infrastructure
python examples/network_discovery.py
```

This will:
1. Scan known Hughes IP ranges
2. Trace routes to common destinations
3. Classify discovered infrastructure
4. Generate comprehensive report

### Performance Monitoring
```bash
# Monitor performance for 1 hour with custom thresholds
python tools/performance_monitor.py \
  --max-rtt 500 \
  --max-loss 3 \
  --max-jitter 30 \
  --interval 30 \
  --duration 3600 \
  google.com
```

### Network Topology Mapping
```bash
# Map Hughes network topology
python tools/network_mapper.py \
  74.192.0.0/16 \
  162.248.0.0/16 \
  --visualize \
  --export hughes_topology.json
```

## Understanding the Results

### Hop Classification

| Symbol | Type | Description |
|--------|------|-------------|
| 🌍 | Terrestrial | Ground-based routing |
| 🌐 | Gateway | Satellite gateway/teleport |
| 🛰️ | Satellite | Satellite hop (GEO/MEO/LEO) |
| 🛰️? | Possible Satellite | High RTT, unclear type |
| ❓ | Unknown | Unclassified hop |

### RTT Interpretation

| RTT Range | Likely Type | Description |
|-----------|-------------|-------------|
| < 20ms | Terrestrial | Local/regional routing |
| 20-60ms | LEO Satellite | Low Earth Orbit |
| 60-150ms | MEO Satellite | Medium Earth Orbit |
| 200-300ms | GEO Satellite | Geostationary Orbit |
| > 300ms | Congested/Multi-hop | Multiple satellites or congestion |

### Hughes Network Identification

Look for these indicators:
- **Hostnames**: hughes, jupiter, spaceway, hughesnet
- **IP Ranges**: 74.192.x.x, 162.248.x.x, 67.15.x.x, 69.46.x.x
- **RTT Patterns**: Sudden jump to 240+ ms indicates satellite hop
- **ASN**: 7155, 22394 (Hughes Network Systems)

## Common Use Cases

### 1. Troubleshooting Slow Internet
```bash
# Check if delays are satellite-related
python examples/basic_analysis.py your-slow-site.com

# Monitor performance over time
python tools/performance_monitor.py \
  --duration 1800 \
  your-slow-site.com
```

### 2. Network Planning
```bash
# Analyze multiple destinations
python tools/delay_analyzer.py site1.com --count 50
python tools/delay_analyzer.py site2.com --count 50
python tools/delay_analyzer.py site3.com --count 50
```

### 3. Service Quality Assessment
```bash
# Monitor with strict thresholds
python tools/performance_monitor.py \
  --max-rtt 400 \
  --max-loss 1 \
  --max-jitter 20 \
  critical-service.com
```

### 4. Research and Analysis
```bash
# Comprehensive network discovery
python examples/network_discovery.py

# Generate detailed reports
python examples/basic_analysis.py research-target.com full
```

## Interpreting Hughes Satellite Delays

### Normal Performance Expectations

**Geostationary Satellite (Hughes Jupiter System):**
- **Minimum RTT**: 240-250ms (physics limit)
- **Typical RTT**: 250-300ms (including processing)
- **Good Performance**: < 350ms average
- **Acceptable Jitter**: < 30ms
- **Acceptable Loss**: < 3%

### Delay Components Breakdown

1. **Propagation Delay** (~240ms)
   - Fixed by satellite altitude
   - Cannot be reduced

2. **Processing Delays** (10-50ms)
   - VSAT modem processing
   - Satellite on-board processing
   - Gateway processing

3. **Queuing Delays** (0-100ms+)
   - Network congestion
   - Traffic prioritization
   - Fair Access Policy (FAP)

4. **Terrestrial Routing** (5-50ms)
   - Gateway to internet backbone
   - Internet routing to destination

### Performance Optimization Tips

1. **Choose Optimal Test Times**
   - Avoid peak hours (7-11 PM local)
   - Test during off-peak for baseline

2. **Multiple Measurement Points**
   - Test to different destinations
   - Use geographically diverse targets

3. **Weather Considerations**
   - Rain fade affects performance
   - Snow/ice on dish impacts signal

## Troubleshooting Common Issues

### High RTT (> 400ms)
```bash
# Check for multiple satellite hops
python tools/satellite_tracer.py slow-target.com --max-hops 30

# Monitor for congestion patterns
python tools/performance_monitor.py --duration 3600 slow-target.com
```

**Possible Causes:**
- Network congestion
- Suboptimal routing
- Multiple satellite hops
- Weather interference

### High Packet Loss (> 5%)
```bash
# Detailed loss analysis
python tools/delay_analyzer.py problematic-site.com --count 200
```

**Possible Causes:**
- Weather (rain fade)
- Dish alignment issues
- Network congestion
- Equipment problems

### High Jitter (> 50ms)
```bash
# Monitor jitter patterns
python tools/performance_monitor.py --max-jitter 25 target.com
```

**Possible Causes:**
- Variable network load
- Competing traffic
- Satellite handovers (LEO)
- Processing variations

## Data Export and Analysis

### JSON Export Format
All tools export data in JSON format for further analysis:

```json
{
  "target": "google.com",
  "timestamp": "20231227_143022",
  "min_rtt": 242.15,
  "avg_rtt": 251.32,
  "max_rtt": 287.43,
  "jitter": 8.23,
  "packet_loss_rate": 2.0,
  "satellite_type": "GEO"
}
```

### Integration with Other Tools
```bash
# Export for Grafana/InfluxDB
python tools/performance_monitor.py target.com --duration 3600
# Creates: satellite_performance_report_<timestamp>.json

# Export topology for network diagrams
python tools/network_mapper.py networks --export topology.json

# Export route analysis
python tools/satellite_tracer.py target.com
# Creates: route_analysis_<target>_<timestamp>.json
```

## Best Practices

### Measurement Accuracy
1. **Multiple Samples**: Use 50+ measurements for statistical validity
2. **Time Diversity**: Test at different times of day
3. **Target Diversity**: Test multiple destinations
4. **Baseline Establishment**: Regular measurements for comparison

### Network Analysis
1. **Start Simple**: Use quick checks before detailed analysis
2. **Document Conditions**: Note weather, time, network load
3. **Compare Baselines**: Track performance over time
4. **Validate Results**: Cross-check with multiple tools

### Performance Monitoring
1. **Set Realistic Thresholds**: Account for satellite physics
2. **Monitor Trends**: Look for degradation patterns
3. **Correlate Events**: Weather, time, network changes
4. **Regular Reviews**: Weekly/monthly performance analysis

## Getting Help

### Common Error Messages

**"Permission denied"**
```bash
# Some tools need elevated privileges
sudo python tools/satellite_tracer.py target.com
```

**"Command not found: traceroute"**
```bash
# Install traceroute (macOS)
brew install traceroute

# Install traceroute (Linux)
sudo apt-get install traceroute
```

**"Module not found"**
```bash
# Install missing dependencies
pip install -r requirements.txt
```

### Support Resources
- Check tool documentation in `tools/README.md`
- Review example scripts in `examples/`
- Examine analysis reports in `analysis/`
- Consult research findings in main `README.md`

### Contributing
If you discover issues or have improvements:
1. Document the problem/enhancement
2. Test with multiple scenarios
3. Follow existing code patterns
4. Update documentation as needed
