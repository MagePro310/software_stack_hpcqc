"""Start the QC gRPC server."""

import argparse
from concurrent import futures
import logging
import signal
import sys

import grpc

from hpqc.communication.v1 import quantum_pb2_grpc
from hpqc.qc.service import QuantumService
from hpqc.qc.services import FUNCTION_HANDLERS
from hpqc.qc.queue import task_queue
from hpqc.qc.logging_config import setup_qc_logging

LOGGER = logging.getLogger(__name__)


def _print_startup_banner(
    address: str,
    max_workers: int,
    queue_concurrency: int,
    log_level: str,
    debug_qiskit: bool,
) -> None:
    """Print an informative startup summary for server operators."""
    funcs = list(FUNCTION_HANDLERS.keys())
    qiskit_mode = "VERBOSE PASSES" if debug_qiskit else "NOISE FILTERED"

    banner = (
        "\n"
        "================================================================================\n"
        "  HPQC QUANTUM SERVER (gRPC)\n"
        "--------------------------------------------------------------------------------\n"
        f"  • Endpoint            : {address}\n"
        f"  • gRPC Worker Threads : {max_workers}\n"
        f"  • Task Queue (FCFS)   : Concurrency = {queue_concurrency}\n"
        f"  • Registered Services : {funcs}\n"
        f"  • Quantum Backend     : AerSimulator (Qiskit Aer)\n"
        f"  • Log Level / Qiskit  : {log_level} ({qiskit_mode})\n"
        "================================================================================\n"
    )
    print(banner, flush=True)


def serve(
    host: str = "0.0.0.0",
    port: int = 50051,
    max_workers: int = 8,
    log_level: str = "INFO",
    debug_qiskit: bool = False,
) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    quantum_pb2_grpc.add_QuantumServiceServicer_to_server(QuantumService(), server)

    address = f"{host}:{port}"
    server.add_insecure_port(address)
    server.start()

    _print_startup_banner(
        address=address,
        max_workers=max_workers,
        queue_concurrency=task_queue.max_concurrent,
        log_level=log_level,
        debug_qiskit=debug_qiskit,
    )
    LOGGER.info("[SERVER]  Server listening on %s, ready for HPC connections.", address)

    def _handle_exit(signum, frame):
        LOGGER.info("[SHUTDOWN] Signal %s received, stopping QC server...", signum)
        task_queue.shutdown(wait=False)
        server.stop(grace=2)
        sys.exit(0)

    signal.signal(signal.SIGINT, _handle_exit)
    signal.signal(signal.SIGTERM, _handle_exit)

    try:
        server.wait_for_termination()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.info("[SHUTDOWN] QC server stopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description="HPQC Quantum Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=50051, help="Port to listen on (default: 50051)")
    parser.add_argument("--max-workers", type=int, default=8, help="Number of gRPC worker threads (default: 8)")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level for QC server (default: INFO)",
    )
    parser.add_argument("--no-color", action="store_true", help="Disable colored log output in terminal")
    parser.add_argument(
        "--debug-qiskit",
        action="store_true",
        help="Enable verbose Qiskit transpiler passmanager logs (default: False)",
    )
    args = parser.parse_args()

    setup_qc_logging(
        log_level=args.log_level,
        enable_color=False if args.no_color else None,
        debug_qiskit=args.debug_qiskit,
    )

    serve(
        host=args.host,
        port=args.port,
        max_workers=args.max_workers,
        log_level=args.log_level,
        debug_qiskit=args.debug_qiskit,
    )


if __name__ == "__main__":
    main()
