"""Bell state quantum circuit."""

from qiskit import QuantumCircuit

def create_bell_circuit() -> QuantumCircuit:
    """Tạo và trả về một mạch lượng tử trạng thái Bell 2-qubit."""
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure_all()
    return circuit
