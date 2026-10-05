"""Start the QC gRPC server."""

import argparse
from concurrent import futures
import logging

import grpc

from hpqc.communication.v1 import quantum_pb2_grpc
from hpqc.qc.service import QuantumService
from hpqc.qc.queue import task_queue

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
LOGGER = logging.getLogger(__name__)


def serve(host: str = "0.0.0.0", port: int = 50051, max_workers: int = 8) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    quantum_pb2_grpc.add_QuantumServiceServicer_to_server(QuantumService(), server)

    address = f"{host}:{port}"
    server.add_insecure_port(address)
    server.start()
    LOGGER.info(
        "QC server listening on %s (max_workers=%d, queue_concurrency=%d)",
        address,
        max_workers,
        task_queue.max_concurrent,
    )

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        LOGGER.info("Shutting down QC server...")
        task_queue.shutdown(wait=False)
        server.stop(grace=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal HPQC QC server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=50051, help="Port to listen on (default: 50051)")
    parser.add_argument("--max-workers", type=int, default=8, help="Number of gRPC worker threads (default: 8)")
    args = parser.parse_args()
    serve(args.host, args.port, args.max_workers)


if __name__ == "__main__":
    main()
