from abc import ABC, abstractmethod
from qiskit import QuantumCircuit

class BaseEncoder(ABC):
    """Base class for quantum encoders."""
    
    @abstractmethod
    def encode(self, data: list) -> QuantumCircuit:
        """
        Create a quantum circuit that encodes the classical data.
        
        Args:
            data: The classical data to encode.
            
        Returns:
            A new QuantumCircuit containing the encoding gates.
        """
        pass
