import time
from collections import deque
from datetime import datetime


class WPMCalculator:
    _wpm_queue = deque(maxlen=10)
    _curr_wpm: int = 0

    def compute_raw_wpm(self, start_time: float, char_count: int):
        time_word: float = (time.time() - start_time) / 60

        self._curr_wpm = round(char_count / 5 / time_word, 2)
        self._wpm_queue.append(self._curr_wpm)

    def get_average_wpm(self):
        return round(sum(self._wpm_queue) / len(self._wpm_queue))

    def get_wpm(self):
        return self._curr_wpm
