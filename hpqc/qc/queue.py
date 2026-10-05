import concurrent.futures
import logging
import os

LOGGER = logging.getLogger(__name__)

class QuantumTaskQueue:
    def __init__(self, max_concurrent: int | None = None):
        """
        Initializes the FCFS task queue.
        ThreadPoolExecutor uses a strict FIFO queue internally.
        """
        if max_concurrent is None:
            try:
                max_concurrent = int(os.getenv("HPQC_MAX_CONCURRENT", "1"))
            except ValueError:
                max_concurrent = 1
        self.max_concurrent = max_concurrent
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent)
        LOGGER.info(f"QuantumTaskQueue initialized with max_concurrent={max_concurrent}")

    def execute_sync(self, func, *args, **kwargs):
        """
        Submit a task to the FCFS queue and block until it completes.
        Returns the result of the function or raises its exception.
        """
        future = self.executor.submit(func, *args, **kwargs)
        return future.result()

    def shutdown(self, wait: bool = True):
        """Shutdown the underlying thread pool executor."""
        self.executor.shutdown(wait=wait)

# Global queue instance. Can be configured via HPQC_MAX_CONCURRENT env variable.
task_queue = QuantumTaskQueue()
