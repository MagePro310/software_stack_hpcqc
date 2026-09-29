# HPC-QC Communication Stack (Quantum-HPC Integration)

This repository provides a scalable integration framework between High-Performance Computing (HPC) nodes and Quantum Computing (QC) servers. 
It uses **gRPC** for efficient, low-latency communication, allowing HPC applications to submit quantum execution tasks to a centralized Quantum Node seamlessly.

## 🌟 Key Features

*   **gRPC-Based Communication**: Fast, typed, and reliable client-server architecture.
*   **Centralized Task Queue**: The QC Server implements a First-Come-First-Served (FCFS) queue, allowing multiple HPC clients to submit tasks without overwhelming the quantum backend.
*   **Encoding & Decoding Framework**: Supports sending classical data from HPC to QC, automatically encoding it into quantum states (e.g., Basis Encoding) before executing the quantum circuit.
*   **Flexible Client Options**: Interact with the QC server via a command-line interface (CLI) hoặc directly within your Python HPC applications.

---

## 🏗 Architecture Overview

1.  **HPC Node (Client)**: Runs classical simulations or workflows. When quantum acceleration is needed, it uses the `QuantumClient` to package data and send a request.
2.  **QC Node (Server)**: Listens for incoming gRPC requests, places them in a task queue, and executes the quantum circuits (e.g., Qiskit Aer Simulator, or real QPUs) using registered function handlers.

---

## 🚀 Getting Started

### 1. Installation

First, clone the repository and set up your Python environment:

```bash
git clone <repository_url>
cd software_stack_hpcqc

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

*(Note: Protocol buffer compilation is already done, so you only need `requirements.txt` to run the code. If you plan to develop the framework further (e.g., modify `.proto` files and recompile them), you should run `pip install -r requirements-dev.txt` instead, which includes `grpcio-tools`.)*

### 2. Start the Quantum Server (QC Node)

Run the following command on the machine designated as the Quantum Computing node:

```bash
python -m hpqc.qc.server --host 0.0.0.0 --port 50051
```

**Expected output:**
```text
INFO:__main__:QC server listening on 0.0.0.0:50051
INFO:hpqc.qc.queue:QuantumTaskQueue initialized with max_concurrent=1
```

### 3. Run the HPC Client (HPC Node)

You can interact with the QC server using the provided Python client. We provide a ready-to-run example in `run_hpc_example.py`.

#### Option A: Running the Example Script

```bash
python run_hpc_example.py
```
*Note: If your server is on a different machine, edit `run_hpc_example.py` to change `"localhost:50051"` to the QC Server's IP address.*

#### Option B: Using Python directly in your application

You can easily integrate quantum calls into your existing HPC pipelines:

```python
import time
from hpqc.hpc.client import QuantumClient

# 1. Connect to the QC server
# Replace 'localhost:50051' with the QC machine's IP (e.g., '10.0.0.20:50051')
qc = QuantumClient("localhost:50051")

try:
    # 2. Prepare classical data to be encoded into the quantum circuit
    # This data will be handled by the server's BasisEncoder
    input_data = {
        "data": [1, 0] 
    }
    
    print("Sending quantum task...")
    
    # 3. Request a quantum execution (e.g., 'bell' function) with 10000 shots
    result = qc.bell(inputs=input_data, shots=10000)
    
    # 4. Process the results
    print("Backend used:", result["backend"])
    print("Result (Counts):", result["result"]["counts"])

finally:
    # 5. Close the connection
    qc.close()
```

#### Option C: Using the Command Line Interface (CLI)

For quick tests, you can use the built-in CLI module:

```bash
python -m hpqc.hpc.client \
  --server localhost:50051 \
  --function bell \
  --shots 1024
```

---

## 🐳 Docker Deployment (Optional)

If you prefer using Docker to isolate the QC server environment:

```bash
# Build the image
docker build -t hpqc-qc-server:0.1 .

# Run the container, exposing the gRPC port
docker run --rm -p 50051:50051 hpqc-qc-server:0.1
```
*(The HPC client does not require Docker and can be run purely in Python).*
