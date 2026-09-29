"""Service endpoint for the Bell-state quantum function."""

from typing import Any

from hpqc.qc.circuits.bell_circuit import BellCircuit
from hpqc.qc.runners.qiskit_runner import AerSimulatorRunner
from hpqc.qc.encoding.basis_encoder import BasisEncoder
from hpqc.qc.decoding.basis_decoder import BasisDecoder

def execute(inputs: Any, shots: int) -> tuple[dict[str, Any], str]:
    """Run a Bell-state circuit and return a JSON-ready result and backend."""
    
    data_to_encode = inputs.get("data", []) if isinstance(inputs, dict) else []
    
    # 1. Khởi tạo components (Cố định 2 qubit cho Bell)
    num_qubits = 2
    circuit_builder = BellCircuit()
    encoder = BasisEncoder(num_qubits=num_qubits)
    decoder = BasisDecoder(num_qubits=num_qubits)
    runner = AerSimulatorRunner(seed=None)
    
    # 2. Xây dựng các mạch độc lập
    encode_circ = encoder.encode(data_to_encode)
    algo_circ = circuit_builder.build()
    decode_circ = decoder.decode()
    
    # 3. Ghép nối tiếp (Composition)
    # Mạch tổng = Encode + Algorithm + Decode
    full_circuit = encode_circ.compose(algo_circ).compose(decode_circ)
    
    # Do decode tạm thời để trống, ta phải add measure vào cuối để giả lập chạy
    full_circuit.measure_all()
    
    # 4. Thực thi
    counts, backend_name = runner.run(full_circuit, shots)
    
    # 5. Hậu xử lý cổ điển
    decoded_output = max(counts, key=counts.get) if counts else ""
    
    # 6. Trả về
    result_payload = {
        "counts": counts,
        "input": inputs,
        "decoded_output": decoded_output
    }
    
    return result_payload, backend_name
