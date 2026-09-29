from qiskit import QuantumCircuit

qc = QuantumCircuit(3, 3)

qc.cx(0, 1)
qc.cx(0, 2)

print(qc.depth())