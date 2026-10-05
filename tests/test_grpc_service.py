"""Unit tests for QuantumService gRPC handler."""

import json
import pytest
import grpc
from hpqc.qc.service import QuantumService
from hpqc.communication.v1 import quantum_pb2


class MockContext:
    def __init__(self):
        self.aborted = False
        self.code = None
        self.details = None

    def abort(self, code, details):
        self.aborted = True
        self.code = code
        self.details = details
        raise RuntimeError(f"RPC Aborted: {code} - {details}")


def test_service_invoke_bell():
    service = QuantumService()
    ctx = MockContext()
    req = quantum_pb2.QuantumRequest(
        function_name="bell",
        input_json=json.dumps({"data": [0, 0]}),
        shots=100
    )
    resp = service.Invoke(req, ctx)
    assert resp.backend == "aer_simulator"
    result = json.loads(resp.result_json)
    assert "counts" in result
    assert "00" in result["counts"] or "11" in result["counts"]


def test_service_invalid_json():
    service = QuantumService()
    ctx = MockContext()
    req = quantum_pb2.QuantumRequest(
        function_name="bell",
        input_json="not a json string",
        shots=100
    )
    with pytest.raises(RuntimeError):
        service.Invoke(req, ctx)
    assert ctx.aborted is True
    assert ctx.code == grpc.StatusCode.INVALID_ARGUMENT


def test_service_unknown_function():
    service = QuantumService()
    ctx = MockContext()
    req = quantum_pb2.QuantumRequest(
        function_name="nonexistent_function",
        input_json="{}",
        shots=100
    )
    with pytest.raises(RuntimeError):
        service.Invoke(req, ctx)
    assert ctx.aborted is True
    assert ctx.code == grpc.StatusCode.NOT_FOUND
