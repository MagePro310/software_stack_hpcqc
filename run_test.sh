#!/bin/bash
PYTHON="/home/trieu/anaconda3/envs/HPQCthayNam/bin/python"

# Start server in background
$PYTHON -m hpqc.qc.server --host 0.0.0.0 --port 50051 > server.log 2>&1 &
SERVER_PID=$!

sleep 2

# Run client
echo "Running client..."
$PYTHON -m hpqc.hpc.client --server localhost:50051 --function bell --shots 1024 > client.log 2>&1

echo "Client exit code: $?"

kill $SERVER_PID
