"""Unit tests for Quantum Pipeline components (Encoding, Circuits, Decoding, Runners)."""

import pytest
from hpqc.qc.encoding.basis_encoder import BasisEncoder
from hpqc.qc.circuits.bell_circuit import BellCircuit
from hpqc.qc.decoding.basis_decoder import BasisDecoder
from hpqc.qc.runners.qiskit_runner import AerSimulatorRunner
from hpqc.qc.services.bell import execute


def test_basis_encoder():
    encoder = BasisEncoder(num_qubits=2)
    circ = encoder.encode([1, 0])
    assert circ.num_qubits == 2
    # Verify Pauli-X gate applied to qubit 0
    ops = [instr.operation.name for instr in circ.data]
    assert "x" in ops


def test_bell_circuit():
    circuit = BellCircuit().build()
    assert circuit.num_qubits == 2
    ops = [instr.operation.name for instr in circuit.data]
    assert "h" in ops
    assert "cx" in ops


def test_basis_decoder():
    decoder = BasisDecoder(num_qubits=2)
    circ = decoder.decode()
    assert circ.num_qubits == 2
    assert circ.num_clbits == 2
    ops = [instr.operation.name for instr in circ.data]
    assert "measure" in ops


def test_aer_runner():
    circuit = BellCircuit().build()
    decoder = BasisDecoder(num_qubits=2)
    full_circuit = circuit.compose(decoder.decode())
    
    runner = AerSimulatorRunner(seed=42)
    counts, backend = runner.run(full_circuit, shots=200)
    assert backend == "aer_simulator"
    assert sum(counts.values()) == 200
    assert "00" in counts or "11" in counts


def test_bell_service_execution_standard():
    # Input [0, 0] or empty produces Bell state |Phi+> (|00> and |11>)
    res_phi, backend = execute({"data": [0, 0]}, shots=500)
    assert backend == "aer_simulator"
    assert "00" in res_phi["counts"]
    assert "11" in res_phi["counts"]
    assert res_phi["decoded_output"] in ["00", "11"]


def test_bell_service_execution_encoded():
    # Input [0, 1] applies X to qubit 1, producing Bell state |Psi+> (|01> and |10>)
    res_psi, backend = execute({"data": [0, 1]}, shots=500)
    assert backend == "aer_simulator"
    assert "01" in res_psi["counts"]
    assert "10" in res_psi["counts"]
    assert res_psi["decoded_output"] in ["01", "10"]
