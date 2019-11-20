from threading import Lock


class AtomicCounter:
    def __init__(self, value: int = 0):
        self.lock = Lock()
        self.value = value

    def set(self, value: int = 0):
        with self.lock:
            self.value = value

    def increment_then_get(self, step: int = 1):
        with self.lock:
            self.value += step
            return self.value
