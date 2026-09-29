from abc import ABC, abstractmethod
from qiskit import QuantumCircuit

class BaseRunner(ABC):
    """Base class for quantum circuit runners."""
    
    @abstractmethod
    def run(self, circuit: QuantumCircuit, shots: int, **kwargs) -> tuple[dict[str, int], str]:
        """
        Execute a quantum circuit and return results.
        
        Args:
            circuit: The quantum circuit to run.
            shots: Number of measurement shots.
            
        Returns:
            A tuple of (counts dictionary, backend name).
        """
        pass
