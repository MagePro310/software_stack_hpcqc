#!/usr/bin/env bash
set -eu

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Navigate to the project root (3 levels up from hpqc/communication/v1)
PROJECT_ROOT="$(dirname $(dirname $(dirname "$DIR")))"

cd "$PROJECT_ROOT"

# Development-only: generated files are committed, so grpcio-tools is not
# required on HPC/QC runtime hosts.
python -m grpc_tools.protoc \
  -I . \
  --python_out=. \
  --grpc_python_out=. \
  hpqc/communication/v1/quantum.proto
