from abc import ABC, abstractmethod
from qiskit import QuantumCircuit

class BaseDecoder(ABC):
    """Base class for quantum decoders."""
    
    @abstractmethod
    def decode(self) -> QuantumCircuit:
        """
        Create a quantum circuit for decoding/measurement.
        
        Returns:
            A new QuantumCircuit containing the measurement/decoding gates.
        """
        pass
