import time
from typing import Optional

from pynput import keyboard


class KeyboardMonitor:
    _last_key_time = None

    _session_start_time: Optional[float] = None
    _session_char_count: int = 0

    def __init__(self, calculator, storage):
        self._calculator = calculator
        self._storage = storage

    def start_monitoring(self) -> None:
        with keyboard.Listener(on_press=self.on_key_press) as listener:
            listener.join()

    def on_key_press(self, key) -> None:
        if self._is_space(key):
            if self._session_char_count != 0:
                self._calculator.compute_raw_wpm(
                    start_time=self._session_start_time,
                    char_count=self._session_char_count,
                )

            self._storage.save_wpm(self._calculator.get_wpm(), format="elapsed")

            self._session_start_time = None
            self._session_char_count = 0
        else:
            if hasattr(key, "char") and key.char:
                if self._session_start_time is None:
                    self._session_start_time = time.time()

                self._session_char_count += 1

    def _is_space(self, key):
        if hasattr(key, "space") and self._session_start_time:
            return True

        return False
