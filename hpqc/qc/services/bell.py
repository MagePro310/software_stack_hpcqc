"""Qiskit Aer implementation of the Bell-state quantum function."""

from typing import Any

from qiskit import QuantumCircuit, transpile
from qiskit.exceptions import QiskitError
from qiskit_aer import AerError, AerSimulator


BACKEND_NAME = "aer_simulator"
SIMULATOR_SEED = 42


def execute(inputs: Any, shots: int) -> tuple[dict[str, Any], str]:
    """Run a Bell-state circuit and return a JSON-ready result and backend."""
    if shots < 1:
        raise ValueError("shots must be >= 1")

    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])

    try:
        simulator = AerSimulator()
        compiled_circuit = transpile(circuit, simulator)
        simulation_result = simulator.run(
            compiled_circuit,
            shots=shots,
            seed_simulator=SIMULATOR_SEED,
        ).result()
        counts = simulation_result.get_counts(compiled_circuit)
    except (AerError, QiskitError) as exc:
        raise RuntimeError("Bell simulation failed") from exc

    return {
        "counts": {outcome: int(count) for outcome, count in counts.items()},
        "input": inputs,
    }, BACKEND_NAME

