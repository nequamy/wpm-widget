import time
from collections import deque


class WPMCalculator:
    _wpm_queue = deque(maxlen=10)

    def compute_raw_wpm(self, start_time: float, char_count: int):
        time_word: float = (time.time() - start_time) / 60

        self._wpm_queue.append(round(char_count / 5 / time_word, 2))

        wpm = sum(self._wpm_queue) / len(self._wpm_queue)

        print("WPM - {0},\t Clear WPM - {1}".format(int(wpm), wpm))
        print("queue - {0}".format(self._wpm_queue))
