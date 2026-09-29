from qiskit import QuantumCircuit
from .base import BaseEncoder

class BasisEncoder(BaseEncoder):
    """Simple Basis Encoder that maps binary data to basis states."""
    
    def __init__(self, num_qubits: int = 2):
        self.num_qubits = num_qubits

    def encode(self, data: list[int]) -> QuantumCircuit:
        """
        Create a quantum circuit encoding binary data (0s and 1s) by applying X gates.
        
        Args:
            data: A list of binary integers (0 or 1).
            
        Returns:
            A new QuantumCircuit with the encoded data.
        """
        circuit = QuantumCircuit(self.num_qubits)
        for i, bit in enumerate(data):
            if i < self.num_qubits and bit == 1:
                circuit.x(i)
                
        return circuit
