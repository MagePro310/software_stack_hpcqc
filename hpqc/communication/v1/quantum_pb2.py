# -*- coding: utf-8 -*-
# Generated-equivalent module for proto/hpqc/communication/v1/quantum.proto.
# Re-generate with scripts/generate_proto.sh after editing the .proto file.

from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf.internal import builder as _builder

_fdp = _descriptor_pb2.FileDescriptorProto()
_fdp.name = "hpqc/communication/v1/quantum.proto"
_fdp.package = "hpqc.communication.v1"
_fdp.syntax = "proto3"

T_STRING = 9
T_UINT32 = 13
LABEL_OPTIONAL = 1


def _add_message(name, fields):
    msg = _fdp.message_type.add()
    msg.name = name
    for number, field_name, field_type in fields:
        field = msg.field.add()
        field.number = number
        field.name = field_name
        field.type = field_type
        field.label = LABEL_OPTIONAL
    return msg


_add_message(
    "QuantumRequest",
    [
        (1, "function_name", T_STRING),
        (2, "input_json", T_STRING),
        (3, "shots", T_UINT32),
    ],
)

_add_message(
    "QuantumResponse",
    [
        (1, "result_json", T_STRING),
        (2, "backend", T_STRING),
    ],
)

_service = _fdp.service.add()
_service.name = "QuantumService"
_method = _service.method.add()
_method.name = "Invoke"
_method.input_type = ".hpqc.communication.v1.QuantumRequest"
_method.output_type = ".hpqc.communication.v1.QuantumResponse"

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(_fdp.SerializeToString())
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR,
    "hpqc.communication.v1.quantum_pb2",
    globals(),
)
