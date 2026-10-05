import os
import time
from unittest.mock import patch
from hpqc.qc.queue import QuantumTaskQueue

def test_queue_execution():
    queue = QuantumTaskQueue(max_concurrent=1)
    
    def sample_task(x):
        return x * 2
        
    result = queue.execute_sync(sample_task, 21)
    assert result == 42
    queue.shutdown(wait=False)

def test_queue_order():
    queue = QuantumTaskQueue(max_concurrent=1)
    results = []

    def task(val, delay=0.01):
        time.sleep(delay)
        results.append(val)
        return val

    queue.execute_sync(task, 1)
    queue.execute_sync(task, 2)
    assert results == [1, 2]
    queue.shutdown(wait=False)

def test_queue_env_concurrency():
    with patch.dict(os.environ, {"HPQC_MAX_CONCURRENT": "3"}):
        queue = QuantumTaskQueue()
        assert queue.max_concurrent == 3
        queue.shutdown(wait=False)
