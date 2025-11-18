"""
Timer Utility
시간 측정 유틸리티
"""
import time
from typing import Optional


class Timer:
    """간단한 시간 측정 타이머"""

    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def start(self) -> None:
        """타이머 시작"""
        self.start_time = time.time()
        self.end_time = None

    def stop(self) -> float:
        """타이머 종료 및 경과 시간 반환 (초)"""
        if self.start_time is None:
            raise RuntimeError("Timer has not been started")

        self.end_time = time.time()
        return self.elapsed()

    def elapsed(self) -> float:
        """경과 시간 반환 (초)"""
        if self.start_time is None:
            return 0.0

        end = self.end_time if self.end_time is not None else time.time()
        return end - self.start_time

    def reset(self) -> None:
        """타이머 리셋"""
        self.start_time = None
        self.end_time = None
