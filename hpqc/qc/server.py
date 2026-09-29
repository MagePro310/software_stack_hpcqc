"""Start the QC gRPC server."""

import argparse
from concurrent import futures

import grpc

from hpqc.communication.v1 import quantum_pb2_grpc
from hpqc.qc.service import QuantumService


def serve(host: str = "0.0.0.0", port: int = 50051) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    quantum_pb2_grpc.add_QuantumServiceServicer_to_server(QuantumService(), server)

    address = f"{host}:{port}"
    server.add_insecure_port(address)
    server.start()
    print(f"QC server listening on {address}")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal HPQC QC server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=50051)
    args = parser.parse_args()
    serve(args.host, args.port)


if __name__ == "__main__":
    main()
