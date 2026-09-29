# Generated-equivalent gRPC helpers for quantum.proto.

import grpc

from hpqc.communication.v1 import quantum_pb2 as quantum__pb2


class QuantumServiceStub:
    def __init__(self, channel):
        self.Invoke = channel.unary_unary(
            "/hpqc.communication.v1.QuantumService/Invoke",
            request_serializer=quantum__pb2.QuantumRequest.SerializeToString,
            response_deserializer=quantum__pb2.QuantumResponse.FromString,
        )


class QuantumServiceServicer:
    def Invoke(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented")
        raise NotImplementedError()


def add_QuantumServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "Invoke": grpc.unary_unary_rpc_method_handler(
            servicer.Invoke,
            request_deserializer=quantum__pb2.QuantumRequest.FromString,
            response_serializer=quantum__pb2.QuantumResponse.SerializeToString,
        )
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "hpqc.communication.v1.QuantumService",
        rpc_method_handlers,
    )
    server.add_generic_rpc_handlers((generic_handler,))
