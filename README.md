# Minimal HPC-QC Communication (gRPC + Protobuf)

This repository is intentionally limited to the smallest reusable communication layer between an HPC application and a QC server.

```text
HPC application
      |
      | gRPC + Protobuf
      v
QC server
      |
      | execute quantum function
      v
QC backend / simulator
      |
      v
result -> HPC application
```

## Repository layout

```text
hpqc-communication-minimal/
|
|-- proto/
|   `-- hpqc/communication/v1/
|       `-- quantum.proto          # source of truth for the wire contract
|
|-- hpqc/
|   |-- communication/v1/
|   |   |-- quantum_pb2.py         # generated protobuf messages
|   |   `-- quantum_pb2_grpc.py    # generated gRPC bindings
|   |
|   |-- hpc/
|   |   `-- client.py              # code that runs on the HPC side
|   |
|   `-- qc/
|       |-- server.py              # starts the gRPC server
|       |-- service.py             # gRPC request handling and dispatch
|       `-- services/
|           |-- __init__.py        # supported-function registry
|           `-- bell.py            # Qiskit Aer Bell implementation
|
|-- scripts/
|   `-- generate_proto.sh
|
|-- requirements.txt               # runtime dependencies only
|-- requirements-dev.txt           # adds grpcio-tools for proto generation
`-- Dockerfile                     # optional QC server container
```

## Protocol

The entire v1 API has one RPC:

```proto
service QuantumService {
  rpc Invoke(QuantumRequest) returns (QuantumResponse);
}
```

The protobuf envelope is versioned. For the MVP, function inputs and outputs are JSON strings inside the protobuf messages so new demo functions can be added without repeatedly changing the schema.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The generated `*_pb2.py` files are committed, so `grpcio-tools` is not required at runtime.

## Start the QC server

On the QC machine:

```bash
python -m hpqc.qc.server --host 0.0.0.0 --port 50051
```

Expected output:

```text
QC server listening on 0.0.0.0:50051
```

## Call it from the HPC machine

```bash
python -m hpqc.hpc.client \
  --server QC_SERVER_IP:50051 \
  --function bell \
  --shots 1024
```

For local testing:

```bash
python -m hpqc.hpc.client --server localhost:50051
```

Example response:

```json
{
  "backend": "aer_simulator",
  "result": {
    "counts": {
      "00": 521,
      "11": 503
    },
    "input": {}
  }
}
```

## Use it from an HPC application

```python
from hpqc.hpc.client import QuantumClient

qc = QuantumClient("10.0.0.20:50051")

x = "classical result"

quantum_result = qc.bell(shots=1024)

print(quantum_result)

qc.close()
```

The Bell result is produced by a Qiskit Aer simulation with a fixed seed of 42.
Later, the same application can call functions such as `vqe`, `qaoa`, or another
domain-specific function while the QC server decides how to build and execute
the corresponding circuit.

## Docker for the QC server

```bash
docker build -t hpqc-qc-server:0.1 .
docker run --rm -p 50051:50051 hpqc-qc-server:0.1
```

The HPC client does not need Docker.

## Regenerate protobuf code

Only needed when `quantum.proto` changes:

```bash
pip install -r requirements-dev.txt
./scripts/generate_proto.sh
```

## Add another quantum function

Quantum functions live in `hpqc/qc/services/`. Each handler accepts the decoded
JSON input and shot count, then returns a JSON-ready result and its backend name:

```python
def execute(inputs, shots):
    result = {"value": "function-specific result", "input": inputs}
    return result, "backend-name"
```

Register the handler in `hpqc/qc/services/__init__.py`:

```python
from hpqc.qc.services import bell, new_function

FUNCTION_HANDLERS = {
    "bell": bell.execute,
    "new-function": new_function.execute,
}
```

The gRPC dispatcher does not need to change when a function is added. Keep
`proto/hpqc/communication/v1/quantum.proto` stable until a real protocol change
is necessary. If a breaking protocol is needed later, add `v2` instead of
overwriting `v1`.
