"""Task queue management for quantum execution with FCFS dispatching."""

import concurrent.futures
import logging
import os
import threading

LOGGER = logging.getLogger(__name__)


class QuantumTaskQueue:
    """FCFS queue for coordinating quantum circuit execution across worker threads."""

    def __init__(self, max_concurrent: int | None = None):
        if max_concurrent is None:
            try:
                max_concurrent = int(os.getenv("HPQC_MAX_CONCURRENT", "1"))
            except ValueError:
                max_concurrent = 1
        self.max_concurrent = max_concurrent
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent)

        self._lock = threading.Lock()
        self._task_counter = 0
        self._pending_tasks = 0
        self._active_tasks = 0

        LOGGER.info("[SERVER]  QuantumTaskQueue initialized (max_concurrent=%d)", max_concurrent)

    def next_task_id(self) -> str:
        """Generates a sequential human-readable task identifier."""
        with self._lock:
            self._task_counter += 1
            return f"TASK-{self._task_counter:04d}"

    @property
    def queue_status(self) -> dict[str, int]:
        with self._lock:
            return {
                "pending": self._pending_tasks,
                "active": self._active_tasks,
                "max_concurrent": self.max_concurrent,
            }

    def execute_sync(self, func, *args, task_id: str | None = None, **kwargs):
        """Submit a task to the queue and block until it completes."""
        if task_id is None:
            task_id = self.next_task_id()

        with self._lock:
            self._pending_tasks += 1
            pending = self._pending_tasks
            active = self._active_tasks

        LOGGER.info("[QUEUE]   [%s] Queued (Pending: %d, Active: %d)", task_id, pending, active)

        def _worker_wrapper():
            with self._lock:
                self._pending_tasks -= 1
                self._active_tasks += 1
            LOGGER.info("[EXEC]    [%s] Starting execution on worker thread", task_id)
            try:
                return func(*args, **kwargs)
            finally:
                with self._lock:
                    self._active_tasks -= 1

        future = self.executor.submit(_worker_wrapper)
        return future.result()

    def shutdown(self, wait: bool = True):
        """Shutdown the underlying thread pool executor."""
        LOGGER.info("[SHUTDOWN] Draining task queue executor (wait=%s)...", wait)
        self.executor.shutdown(wait=wait)


# Global queue instance. Can be configured via HPQC_MAX_CONCURRENT env variable.
task_queue = QuantumTaskQueue()
