"""QC-side implementation of the minimal gRPC contract."""

import json
import logging

import grpc

from hpqc.communication.v1 import quantum_pb2, quantum_pb2_grpc
from hpqc.qc.services import FUNCTION_HANDLERS
from hpqc.qc.queue import task_queue


LOGGER = logging.getLogger(__name__)


class QuantumService(quantum_pb2_grpc.QuantumServiceServicer):
    """Receives a quantum-function request and returns its result.

    Quantum functions are registered in ``hpqc.qc.services``. Each handler owns
    its backend-specific execution while this class keeps the transport contract
    independent of Qiskit, another simulator, or a real QPU.
    """

    def Invoke(self, request, context):
        function_name = request.function_name.strip()
        shots = request.shots or 1024

        try:
            inputs = json.loads(request.input_json or "{}")
        except json.JSONDecodeError as exc:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"invalid input_json: {exc}")

        try:
            result, backend = task_queue.execute_sync(self._execute, function_name, inputs, shots)
        except KeyError:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"unknown quantum function: {function_name}",
            )
        except ValueError as exc:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))
        except RuntimeError:
            LOGGER.exception("quantum function %r failed", function_name)
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"quantum function failed: {function_name}",
            )

        return quantum_pb2.QuantumResponse(
            result_json=json.dumps(result, separators=(",", ":")),
            backend=backend,
        )

    @staticmethod
    def _execute(function_name, inputs, shots):
        try:
            handler = FUNCTION_HANDLERS[function_name]
        except KeyError:
            raise KeyError(function_name)
        if shots < 1:
            raise ValueError("shots must be >= 1")
        return handler(inputs, shots)
