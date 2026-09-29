"""Service endpoint for the Bell-state quantum function."""

from typing import Any

from hpqc.qc.circuits.bell_circuit import create_bell_circuit
from hpqc.qc.runners.qiskit_runner import run_on_aer_simulator

# Keep the fixed seed for now if required for tests, but we'll allow the runner to take it.
# We will just pass None to simulate real noise, or 42 for testing if we wanted.
# I will pass None by default as suggested in the plan.

def execute(inputs: Any, shots: int) -> tuple[dict[str, Any], str]:
    """Run a Bell-state circuit and return a JSON-ready result and backend."""
    
    # 1. Tạo mạch
    circuit = create_bell_circuit()
    
    # 2. Chạy trên runner
    counts, backend_name = run_on_aer_simulator(circuit, shots)
    
    # 3. Trả về format chuẩn
    result_payload = {
        "counts": counts,
        "input": inputs,
    }
    
    return result_payload, backend_name

