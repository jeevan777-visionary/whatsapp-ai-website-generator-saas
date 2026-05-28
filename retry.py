from __future__ import annotations

import time
from typing import Callable


def with_retry(func: Callable, attempts: int = 3, delay: float = 2.0):
    last_error = None
    for _ in range(attempts):
        try:
            return func()
        except Exception as exc:
            last_error = exc
            time.sleep(delay)
    raise last_error
