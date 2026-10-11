"""QC-side implementation of the minimal gRPC contract."""

import json
import logging
import time

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
        task_id = task_queue.next_task_id()
        start_time = time.perf_counter()

        peer = context.peer() if hasattr(context, "peer") and callable(context.peer) else "internal"
        function_name = request.function_name.strip()
        shots = request.shots or 1024

        try:
            inputs = json.loads(request.input_json or "{}")
        except json.JSONDecodeError as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            LOGGER.error("[ERROR]   [%s] Invalid JSON input (%.2f ms) from %s: %s", task_id, duration_ms, peer, exc)
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"invalid input_json: {exc}")

        # Format concise preview of inputs for clean terminal log
        input_str = json.dumps(inputs, separators=(",", ":"))
        input_preview = (input_str[:60] + "...") if len(input_str) > 60 else input_str

        LOGGER.info(
            "[REQUEST] [%s] Client: %s | Func: '%s' | Shots: %d | Input: %s",
            task_id,
            peer,
            function_name,
            shots,
            input_preview,
        )

        try:
            result, backend = task_queue.execute_sync(
                self._execute,
                function_name,
                inputs,
                shots,
                task_id=task_id,
            )
        except KeyError:
            duration_ms = (time.perf_counter() - start_time) * 1000
            LOGGER.error(
                "[ERROR]   [%s] Unknown quantum function '%s' (%.2f ms)",
                task_id,
                function_name,
                duration_ms,
            )
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"unknown quantum function: {function_name}",
            )
        except ValueError as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            LOGGER.error("[ERROR]   [%s] Invalid argument (%.2f ms): %s", task_id, duration_ms, exc)
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            LOGGER.exception(
                "[ERROR]   [%s] Execution failed for '%s' (%.2f ms): %s",
                task_id,
                function_name,
                duration_ms,
                exc,
            )
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"quantum function failed: {function_name} ({exc})",
            )

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Build informative summary of quantum output
        summary = ""
        if isinstance(result, dict):
            decoded = result.get("decoded_output")
            counts = result.get("counts", {})
            if decoded:
                decoded_count = counts.get(decoded, 0)
                pct = (decoded_count / shots * 100) if shots > 0 else 0
                summary = f"Decoded: '{decoded}' ({decoded_count}/{shots}, {pct:.1f}%)"
            elif counts:
                top_state = max(counts, key=counts.get)
                summary = f"Top state: '{top_state}' ({counts[top_state]}/{shots})"

        LOGGER.info(
            "[SUCCESS] [%s] Completed in %.2f ms | Backend: %s%s",
            task_id,
            duration_ms,
            backend,
            f" | {summary}" if summary else "",
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
