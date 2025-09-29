import time
from typing import Optional

from pynput import keyboard

from wpm_widget._core.wpm_calculator import WPMCalculator


class KeyboardMonitor:
    _last_key_time = None
    _calculator = WPMCalculator()

    _session_start_time: Optional[float] = None
    _session_char_count: int = 0

    def start_monitoring(self) -> None:
        with keyboard.Listener(on_press=self.on_key_press) as listener:
            listener.join()

    def stop_monitoring(self): ...

    def on_key_press(self, key) -> None:
        if self._is_space(key):
            self._calculator.compute_raw_wpm(
                start_time=self._session_start_time,
                char_count=self._session_char_count,
            )

            self._session_start_time = None
            self._session_char_count = 0
        else:
            if hasattr(key, "char") and key.char:
                if self._session_start_time is None:
                    self._session_start_time = time.time()

                self._session_char_count += 1

    def get_typing_session(self): ...

    def _is_space(self, key):
        if hasattr(key, "space") and self._session_start_time:
            return True

        return False
