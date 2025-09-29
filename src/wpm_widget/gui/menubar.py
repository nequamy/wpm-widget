import threading

import rumps

from wpm_widget._core import DataStorage, KeyboardMonitor, WPMCalculator
from wpm_widget.gui.stats_window import StatsWindow


class MenuBarApp(rumps.App):
    def __init__(self):
        super().__init__("0 WPM")

        self.storage = DataStorage()
        self.calculator = WPMCalculator()
        self.monitor = KeyboardMonitor(self.calculator, self.storage)
        self.stats_window = StatsWindow(self.storage)
        self.monitor_thread = threading.Thread(target=self.monitor.start_monitoring)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        self.timer = rumps.Timer(self.update_wpm, 1)
        self.timer.start()

    def update_wpm(self, _):
        wpm = int(self.calculator.get_wpm())
        self.title = f"{wpm} WPM"

    @rumps.clicked("Show Stats")
    def show_stats(self, _):
        pass
        # self.stats_window.show_stats()
