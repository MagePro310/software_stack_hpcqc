"""Qiskit implementation of quantum circuit runner."""

from qiskit import QuantumCircuit, transpile
from qiskit.exceptions import QiskitError
from qiskit_aer import AerError, AerSimulator

BACKEND_NAME = "aer_simulator"

def run_on_aer_simulator(circuit: QuantumCircuit, shots: int, seed: int | None = 42) -> tuple[dict[str, int], str]:
    """Chạy một QuantumCircuit trên AerSimulator và trả về counts."""
    if shots < 1:
        raise ValueError("shots must be >= 1")

    try:
        simulator = AerSimulator()
        compiled_circuit = transpile(circuit, simulator)
        
        # Chạy simulator với seed mặc định là 42 để đảm bảo kết quả tái lập được (reproducible)
        simulation_result = simulator.run(
            compiled_circuit,
            shots=shots,
            seed_simulator=seed,
        ).result()
        counts = simulation_result.get_counts(compiled_circuit)
    except (AerError, QiskitError) as exc:
        raise RuntimeError("Quantum simulation failed") from exc

    return {outcome: int(count) for outcome, count in counts.items()}, BACKEND_NAME
