import concurrent.futures
import logging

LOGGER = logging.getLogger(__name__)

class QuantumTaskQueue:
    def __init__(self, max_concurrent: int = 1):
        """
        Initializes the FCFS task queue.
        ThreadPoolExecutor uses a strict FIFO queue internally.
        """
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent)
        LOGGER.info(f"QuantumTaskQueue initialized with max_concurrent={max_concurrent}")

    def execute_sync(self, func, *args, **kwargs):
        """
        Submit a task to the FCFS queue and block until it completes.
        Returns the result of the function or raises its exception.
        """
        future = self.executor.submit(func, *args, **kwargs)
        return future.result()

# Global queue instance, configured to allow 1 concurrent execution for now.
# In the future, this can be dynamically adjusted based on available resources.
task_queue = QuantumTaskQueue(max_concurrent=1)
