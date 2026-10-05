from qiskit import QuantumCircuit
from .base import BaseDecoder

class BasisDecoder(BaseDecoder):
    """Simple decoder that appends computational basis measurements to the circuit."""
    
    def __init__(self, num_qubits: int = 2):
        self.num_qubits = num_qubits

    def decode(self) -> QuantumCircuit:
        """
        Create a measurement circuit in the computational (Z) basis.
        
        Returns:
            A QuantumCircuit with measurements mapped to classical bits.
        """
        circuit = QuantumCircuit(self.num_qubits, self.num_qubits)
        circuit.measure(range(self.num_qubits), range(self.num_qubits))
        return circuit
