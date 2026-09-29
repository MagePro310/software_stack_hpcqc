from abc import ABC, abstractmethod
from qiskit import QuantumCircuit

class BaseCircuit(ABC):
    """Base class for quantum circuits."""
    
    @abstractmethod
    def build(self) -> QuantumCircuit:
        """
        Build and return the quantum circuit.
        
        Returns:
            A Qiskit QuantumCircuit instance.
        """
        pass
