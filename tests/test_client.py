"""Unit tests for HPC QuantumClient."""

import json
from unittest.mock import MagicMock, patch
from hpqc.hpc.client import QuantumClient
from hpqc.communication.v1 import quantum_pb2


def test_client_context_manager():
    with patch("grpc.insecure_channel") as mock_channel:
        with QuantumClient("localhost:50051") as client:
            assert client._server == "localhost:50051"
        mock_channel.return_value.close.assert_called_once()


def test_client_invoke():
    with patch("grpc.insecure_channel") as mock_channel:
        client = QuantumClient("localhost:50051")
        mock_stub = MagicMock()
        client._stub = mock_stub
        
        mock_stub.Invoke.return_value = quantum_pb2.QuantumResponse(
            backend="aer_simulator",
            result_json=json.dumps({"counts": {"00": 50, "11": 50}, "decoded_output": "00"})
        )
        
        res = client.invoke("bell", {"data": [0, 0]}, shots=100)
        assert res["backend"] == "aer_simulator"
        assert res["result"]["counts"] == {"00": 50, "11": 50}
        
        # Verify request parameters
        called_req = mock_stub.Invoke.call_args[0][0]
        assert called_req.function_name == "bell"
        assert called_req.shots == 100
        assert json.loads(called_req.input_json) == {"data": [0, 0]}
        
        client.close()
