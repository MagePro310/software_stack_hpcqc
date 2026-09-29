"""Registry for quantum functions supported by the QC server."""

from collections.abc import Callable
from typing import Any, TypeAlias

from hpqc.qc.services import bell

QuantumFunctionResult: TypeAlias = tuple[dict[str, Any], str]
QuantumFunctionHandler: TypeAlias = Callable[[Any, int], QuantumFunctionResult]


FUNCTION_HANDLERS: dict[str, QuantumFunctionHandler] = {
    "bell": bell.execute,
}

