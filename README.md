# HPC-QC Communication Stack

This repository provides a gRPC communication layer between an High-Performance Computing (HPC) application and a Quantum Computing (QC) server. 

## 1. Installation

First, set up your Python environment and install the required dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
*(Note: The `grpcio-tools` compiler is not required at runtime as the generated protocol files are already included).*

## 2. Start the Quantum Server (QC Side)

To start the quantum backend server, run the following command on the QC machine:

```bash
python -m hpqc.qc.server --host 0.0.0.0 --port 50051
```

**Expected output:**
```text
QC server listening on 0.0.0.0:50051
```

## 3. Connect from the HPC Machine (Client Side)

You can interact with the QC server either via the Command Line Interface (CLI) or directly within your Python scripts.

### Option A: Using the CLI

Run the client script to send a quantum task (e.g., the `bell` function) to the server:

```bash
python -m hpqc.hpc.client \
  --server QC_SERVER_IP:50051 \
  --function bell \
  --shots 1024
```
*(Use `--server localhost:50051` for local testing).*

**Example Response:**
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

### Option B: Using Python in an HPC Application

You can integrate the client directly into your HPC application workflows:

```python
from hpqc.hpc.client import QuantumClient

# Connect to the QC server
qc = QuantumClient("10.0.0.20:50051")

# Request a quantum simulation (e.g., Bell state)
quantum_result = qc.bell(shots=1024)

print("Quantum Execution Result:")
print(quantum_result)

# Close the connection
qc.close()
```

## 4. Run QC Server via Docker (Optional)

If you prefer using Docker for the QC server, you can build and run the container using:

```bash
docker build -t hpqc-qc-server:0.1 .
docker run --rm -p 50051:50051 hpqc-qc-server:0.1
```
*(The HPC client does not require Docker to run).*
