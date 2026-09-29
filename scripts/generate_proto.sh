#!/usr/bin/env sh
set -eu

# Development-only: generated files are committed, so grpcio-tools is not
# required on HPC/QC runtime hosts.
python -m grpc_tools.protoc \
  -I proto \
  --python_out=. \
  --grpc_python_out=. \
  proto/hpqc/communication/v1/quantum.proto
