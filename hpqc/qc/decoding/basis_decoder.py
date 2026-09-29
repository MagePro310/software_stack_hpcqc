from qiskit import QuantumCircuit
from .base import BaseDecoder

class BasisDecoder(BaseDecoder):
    """Simple decoder that appends computational basis measurements to the circuit."""
    
    def __init__(self, num_qubits: int = 2):
        self.num_qubits = num_qubits

    def decode(self) -> QuantumCircuit:
        """
        Temporarily returns an empty circuit as requested.
        Normally this would return a measurement circuit.
        
        Returns:
            An empty QuantumCircuit.
        """
        circuit = QuantumCircuit(self.num_qubits)
        # Tạm thời để trống (không thêm cổng đo)
        return circuit
