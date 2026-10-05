"""Qiskit implementation of quantum circuit runner."""

from qiskit import QuantumCircuit, transpile
from qiskit.exceptions import QiskitError
from qiskit_aer import AerError, AerSimulator
from .base import BaseRunner

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
        """Chạy một QuantumCircuit trên AerSimulator và trả về counts."""
        if shots < 1:
            raise ValueError("shots must be >= 1")

        try:
            compiled_circuit = transpile(circuit, self._simulator)
            
            # Chạy simulator
            simulation_result = self._simulator.run(
                compiled_circuit,
                shots=shots,
                seed_simulator=self.seed,
            ).result()
            counts = simulation_result.get_counts(compiled_circuit)
        except (AerError, QiskitError) as exc:
            raise RuntimeError("Quantum simulation failed") from exc

        return {outcome: int(count) for outcome, count in counts.items()}, self.BACKEND_NAME
