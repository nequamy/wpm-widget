from wpm_widget._core import KeyboardMonitor


def main(*args, **kwargs):
    monitor = KeyboardMonitor()
    monitor.start_monitoring()


if __name__ == "__main__":
    main()
