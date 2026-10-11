"""Unit tests for QC Server logging configuration and formatting."""

import json
import logging
from unittest.mock import MagicMock
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from hpqc.qc.logging_config import setup_qc_logging, QCLogFormatter, NOISY_LOGGERS
from hpqc.qc.service import QuantumService
from hpqc.communication.v1 import quantum_pb2


def test_setup_qc_logging_suppresses_qiskit():
    setup_qc_logging(log_level="INFO", debug_qiskit=False)
    for name in NOISY_LOGGERS:
        logger = logging.getLogger(name)
        assert logger.level == logging.WARNING


def test_setup_qc_logging_debug_qiskit():
    setup_qc_logging(log_level="INFO", debug_qiskit=True)
    for name in NOISY_LOGGERS:
        logger = logging.getLogger(name)
        assert logger.level == logging.INFO


def test_formatter_plain_and_color():
    formatter_plain = QCLogFormatter(use_color=False)
    formatter_color = QCLogFormatter(use_color=True)

    record = logging.LogRecord(
        name="hpqc.test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="[REQUEST] Test message",
        args=(),
        exc_info=None,
    )

    out_plain = formatter_plain.format(record)
    assert "[INFO ] [REQUEST] Test message" in out_plain
    assert "\033[" not in out_plain

    out_color = formatter_color.format(record)
    assert "\033[" in out_color
    assert "Test message" in out_color


def test_transpiler_does_not_spam_when_suppressed(caplog):
    caplog.set_level(logging.INFO)
    setup_qc_logging(log_level="INFO", debug_qiskit=False)
    caplog.clear()

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    sim = AerSimulator()
    transpile(qc, sim)

    # Ensure no Qiskit passmanager or transpiler info records in captured logs
    for record in caplog.records:
        assert not record.name.startswith("qiskit.passmanager")
        assert not record.name.startswith("qiskit.compiler")


def test_service_invoke_logging_with_mock_context(caplog):
    caplog.set_level(logging.INFO)
    setup_qc_logging(log_level="INFO", debug_qiskit=False)
    caplog.clear()

    class MockContext:
        def __init__(self):
            self.aborted = False

        def peer(self):
            return "ipv4:127.0.0.1:54321"

        def abort(self, code, details):
            self.aborted = True

    service = QuantumService()
    ctx = MockContext()
    req = quantum_pb2.QuantumRequest(
        function_name="bell",
        input_json=json.dumps({"data": [0, 0]}),
        shots=100,
    )

    resp = service.Invoke(req, ctx)
    assert resp.backend == "aer_simulator"

    # Verify lifecycle log entries are recorded
    log_messages = [r.getMessage() for r in caplog.records]
    assert any("[REQUEST]" in m and "bell" in m for m in log_messages)
    assert any("[QUEUE]" in m for m in log_messages)
    assert any("[EXEC]" in m for m in log_messages)
    assert any("[SUCCESS]" in m and "aer_simulator" in m for m in log_messages)

