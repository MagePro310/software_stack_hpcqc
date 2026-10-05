"""HPC-side client for the minimal HPC-QC gRPC protocol."""

import argparse
import json

import grpc

from hpqc.communication.v1 import quantum_pb2, quantum_pb2_grpc


class QuantumClient:
    def __init__(self, server: str):
        self._server = server
        self._channel = grpc.insecure_channel(server)
        self._stub = quantum_pb2_grpc.QuantumServiceStub(self._channel)

    def close(self) -> None:
        self._channel.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def invoke(self, function_name: str, inputs: dict | list | None = None, shots: int = 1024):
        request = quantum_pb2.QuantumRequest(
            function_name=function_name,
            input_json=json.dumps(inputs if inputs is not None else {}),
            shots=shots,
        )
        response = self._stub.Invoke(request)
        return {
            "backend": response.backend,
            "result": json.loads(response.result_json),
        }

    def bell(self, inputs: dict | None = None, shots: int = 1024):
        return self.invoke("bell", inputs, shots)


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal HPQC HPC client")
    parser.add_argument("--server", default="localhost:50051")
    parser.add_argument("--function", default="bell")
    parser.add_argument("--input", default="{}", help="JSON object")
    parser.add_argument("--shots", type=int, default=1024)
    args = parser.parse_args()

    client = QuantumClient(args.server)
    try:
        result = client.invoke(
            args.function,
            json.loads(args.input),
            args.shots,
        )
        print(json.dumps(result, indent=2))
    finally:
        client.close()


if __name__ == "__main__":
    main()
