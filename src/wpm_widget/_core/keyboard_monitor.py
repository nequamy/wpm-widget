import time

from pynput import keyboard


class KeyboardMonitor:
    _last_key_time = None

    def start_monitoring(self) -> None:
        with keyboard.Listener(on_press=self.on_key_press) as listener:
            listener.join()

    def stop_monitoring(self): ...

    def on_key_press(self, key) -> None:
        current_time = time.time()

        if self._last_key_time:
            time_between_keys = current_time - self._last_key_time
            print(f"Time between keys {time_between_keys:.3f}s")

        self._last_key_time = current_time

    def get_typing_session(self): ...


monitor = KeyboardMonitor()
monitor.start_monitoring()
