from wpm_widget._core import DataStorage, KeyboardMonitor, WPMCalculator


def main(*args, **kwargs):
    calculator = WPMCalculator()
    storage = DataStorage()
    monitor = KeyboardMonitor(calculator=calculator, storage=storage)
    monitor.start_monitoring()


if __name__ == "__main__":
    main()
