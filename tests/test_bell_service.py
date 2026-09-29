import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import grpc

from hpqc.communication.v1 import quantum_pb2
from hpqc.qc.service import QuantumService
from hpqc.qc.services import FUNCTION_HANDLERS
from hpqc.qc.services.bell import execute


class RpcAbort(Exception):
    def __init__(self, code, details):
        super().__init__(details)
        self.code = code
        self.details = details


class FakeContext:
    def abort(self, code, details):
        raise RpcAbort(code, details)


class BellHandlerTests(unittest.TestCase):
    def test_counts_are_bell_outcomes_and_match_shots(self):
        result, backend = execute({"request_id": "test"}, 128)

        self.assertEqual(backend, "aer_simulator")
        self.assertEqual(result["input"], {"request_id": "test"})
        self.assertTrue(set(result["counts"]).issubset({"00", "11"}))
        self.assertEqual(sum(result["counts"].values()), 128)

    def test_fixed_seed_is_reproducible(self):
        first, _ = execute({}, 128)
        second, _ = execute({}, 128)

        self.assertEqual(first["counts"], second["counts"])


class QuantumServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = QuantumService()
        self.context = FakeContext()

    def test_bell_is_dispatched_through_registry(self):
        request = quantum_pb2.QuantumRequest(
            function_name="bell",
            input_json=json.dumps({"source": "test"}),
            shots=64,
        )

        response = self.service.Invoke(request, self.context)
        result = json.loads(response.result_json)

        self.assertEqual(response.backend, "aer_simulator")
        self.assertEqual(result["input"], {"source": "test"})
        self.assertEqual(sum(result["counts"].values()), 64)

    def test_unknown_function_returns_not_found(self):
        request = quantum_pb2.QuantumRequest(function_name="missing")

        with self.assertRaises(RpcAbort) as raised:
            self.service.Invoke(request, self.context)

        self.assertEqual(raised.exception.code, grpc.StatusCode.NOT_FOUND)

    def test_malformed_json_returns_invalid_argument(self):
        request = quantum_pb2.QuantumRequest(
            function_name="bell",
            input_json="{not-json}",
        )

        with self.assertRaises(RpcAbort) as raised:
            self.service.Invoke(request, self.context)

        self.assertEqual(raised.exception.code, grpc.StatusCode.INVALID_ARGUMENT)

    def test_invalid_shots_returns_invalid_argument(self):
        request = SimpleNamespace(
            function_name="bell",
            input_json="{}",
            shots=-1,
        )

        with self.assertRaises(RpcAbort) as raised:
            self.service.Invoke(request, self.context)

        self.assertEqual(raised.exception.code, grpc.StatusCode.INVALID_ARGUMENT)

    def test_backend_failure_returns_internal_without_error_details(self):
        def failing_handler(inputs, shots):
            raise RuntimeError("secret backend details")

        request = quantum_pb2.QuantumRequest(function_name="failing", shots=1)
        with patch.dict(FUNCTION_HANDLERS, {"failing": failing_handler}):
            with self.assertRaises(RpcAbort) as raised:
                self.service.Invoke(request, self.context)

        self.assertEqual(raised.exception.code, grpc.StatusCode.INTERNAL)
        self.assertNotIn("secret", raised.exception.details)


if __name__ == "__main__":
    unittest.main()
