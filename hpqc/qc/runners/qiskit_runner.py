"""Qiskit implementation of quantum circuit runner."""

import logging
from qiskit import QuantumCircuit, transpile
from qiskit.exceptions import QiskitError
from qiskit_aer import AerError, AerSimulator
from .base import BaseRunner

LOGGER = logging.getLogger(__name__)


class AerSimulatorRunner(BaseRunner):
    """Runner using Qiskit's AerSimulator."""

    BACKEND_NAME = "aer_simulator"

    def __init__(self, seed: int | None = 42):
        """
        Args:
            seed: Seed for the simulator (default 42 for reproducible results).
        """
        self.seed = seed
        self._simulator = AerSimulator()

    def run(self, circuit: QuantumCircuit, shots: int, **kwargs) -> tuple[dict[str, int], str]:
        """Runs a QuantumCircuit on AerSimulator and returns counts."""
        if shots < 1:
            raise ValueError("shots must be >= 1")

        try:
            LOGGER.debug(
                "Transpiling circuit (qubits=%d, depth=%d, ops=%s)",
                circuit.num_qubits,
                circuit.depth(),
                dict(circuit.count_ops()),
            )
            compiled_circuit = transpile(circuit, self._simulator)

            simulation_result = self._simulator.run(
                compiled_circuit,
                shots=shots,
                seed_simulator=self.seed,
            ).result()
            counts = simulation_result.get_counts(compiled_circuit)
        except (AerError, QiskitError) as exc:
            raise RuntimeError("Quantum simulation failed") from exc

        return {outcome: int(count) for outcome, count in counts.items()}, self.BACKEND_NAME
