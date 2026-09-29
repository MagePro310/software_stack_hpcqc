"""Bell state quantum circuit."""

from qiskit import QuantumCircuit
from .base import BaseCircuit

class BellCircuit(BaseCircuit):
    """A Bell state 2-qubit quantum circuit."""
    
    def build(self) -> QuantumCircuit:
        """Tạo và trả về một mạch lượng tử trạng thái Bell 2-qubit (chưa có đo lường)."""
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        return circuit
