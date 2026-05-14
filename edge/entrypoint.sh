#!/bin/bash
# Apply simulated geographic latency using Linux Traffic Control
# $LATENCY is passed from docker-compose (e.g., 120ms)
tc qdisc add dev eth0 root netem delay $LATENCY 10ms distribution normal

# Start the Python application
uvicorn main:app --host 0.0.0.0 --port 8000