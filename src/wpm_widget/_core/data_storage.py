import sqlite3
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path


class DataStorage:
    _db_path: str = "data/wpm_data.db"
    _last_aggregation: dict = {
        "minute": None,
        "hour": None,
        "day": None,
        "week": None,
        "month": None,
    }

    def __init__(self):
        Path("data").mkdir(exist_ok=True)

        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS wpm_data (
            timestamp TEXT,
            wpm REAL,
            period TEXT
        )
        """
        self._conn.execute(sql)
        self._conn.commit()

        self._start_aggregation_timer()

    def save_wpm(self, wpm: float, format: str = "elapsed"):
        now = datetime.now().isoformat()
        sql = "INSERT INTO wpm_data (timestamp, wpm, period) VALUES (?, ?, ?)"
        self._conn.execute(sql, (now, wpm, format))
        self._conn.commit()

    def get_current_average(self) -> float:
        today = datetime.now().date().isoformat()

        sql = """
        SELECT AVG(wpm) FROM wpm_data
        WHERE date(timestamp) = ? AND period = 'minute'
        """

        cursor = self._conn.execute(sql, (today,))
        result = cursor.fetchone()[0]

        return result if result else 0.0

    def _start_aggregation_timer(self):
        def aggregate_loop():
            while True:
                time.sleep(30)
                self._aggregate(datetime.now())

        thread = threading.Thread(target=aggregate_loop, daemon=True)
        thread.start()

    def _aggregate(self, curr_time):
        if self._should_aggregate_minute(curr_time):
            self._aggregate_last_minute()

        if self._should_aggregate_hour(curr_time):
            self._aggregate_last_hour()

        if self._should_aggregate_day(curr_time):
            self._aggregate_last_day()

        if self._should_aggregate_week(curr_time):
            self._aggregate_last_week()

        if self._should_aggregate_month(curr_time):
            self._aggregate_last_month()

    def _should_aggregate_minute(self, time) -> bool:
        curr_min = time.replace(second=0, microsecond=0)
        last_min = self._last_aggregation["minute"]

        if last_min is None:
            self._last_aggregation["minute"] = curr_min
            return False

        if curr_min > last_min:
            self._last_aggregation["minute"] = curr_min
            return True

        return False

    def _should_aggregate_hour(self, time) -> bool:
        curr_hour = time.replace(minute=0, second=0, microsecond=0)
        last_hour = self._last_aggregation["hour"]

        if last_hour is None or curr_hour > last_hour:
            self._last_aggregation["hour"] = curr_hour
            return True

        return False

    def _should_aggregate_day(self, time) -> bool:
        curr_day = time.replace(hour=0, minute=0, second=0, microsecond=0)
        last_day = self._last_aggregation["day"]

        if last_day is None or curr_day > last_day:
            self._last_aggregation["day"] = curr_day
            return True

        return False

    def _should_aggregate_week(self, time) -> bool:
        start_of_week = time - timedelta(days=time.weekday())
        curr_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        last_week = self._last_aggregation["week"]

        if last_week is None or curr_week > last_week:
            self._last_aggregation["week"] = curr_week
            return True

        return False

    def _should_aggregate_month(self, time) -> bool:
        curr_month = time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = self._last_aggregation["month"]

        if last_month is None or curr_month > last_month:
            self._last_aggregation["month"] = curr_month
            return True

        return False

    def _aggregate_last_minute(self) -> None:
        prev_minute = datetime.now() - timedelta(minutes=1)
        start = prev_minute.replace(second=0, microsecond=0)
        end = start + timedelta(minutes=1)

        sql = """
        SELECT AVG(wpm) FROM wpm_data
        WHERE timestamp >= ? AND timestamp < ? AND period = 'elapsed'
        """

        cursor = self._conn.execute(sql, (start.isoformat(), end.isoformat()))
        result = cursor.fetchone()[0]

        if result:
            self.save_wpm(wpm=result, format="minute")
            self._cleanup_data(start, end, "elapsed")

    def _aggregate_last_hour(self) -> None:
        prev_hour = datetime.now() - timedelta(hours=1)
        start = prev_hour.replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)

        sql = """
        SELECT AVG(wpm) FROM wpm_data
        WHERE timestamp >= ? AND timestamp < ? AND period = 'minute'
        """

        cursor = self._conn.execute(sql, (start.isoformat(), end.isoformat()))
        result = cursor.fetchone()[0]

        if result:
            self.save_wpm(wpm=result, format="hour")
            self._cleanup_data(start, end, "minute")

    def _aggregate_last_day(self) -> None:
        prev_day = datetime.now() - timedelta(days=1)
        start = prev_day.replace(hour=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        sql = """
        SELECT AVG(wpm) FROM wpm_data
        WHERE timestamp >= ? AND timestamp < ? AND period = 'hour'
        """

        cursor = self._conn.execute(sql, (start.isoformat(), end.isoformat()))
        result = cursor.fetchone()[0]

        if result:
            self.save_wpm(wpm=result, format="day")
            self._cleanup_data(start, end, "hour")

    def _aggregate_last_week(self) -> None:
        now = datetime.now()
        start_of_current_week = now - timedelta(days=now.weekday())
        start_of_prev_week = start_of_current_week - timedelta(days=7)

        start = start_of_prev_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)

        sql = """
        SELECT AVG(wpm) FROM wpm_data
        WHERE timestamp >= ? AND timestamp < ? AND period = 'day'
        """

        cursor = self._conn.execute(sql, (start.isoformat(), end.isoformat()))
        result = cursor.fetchone()[0]

        if result:
            self.save_wpm(wpm=result, format="week")
            self._cleanup_data(start, end, "day")

    def _aggregate_last_month(self) -> None:
        now = datetime.now()

        if now.month == 1:
            start = datetime(now.year - 1, 12, 1)
            end = datetime(now.year, 1, 1)
        else:
            start = datetime(now.year, now.month - 1, 1)
            end = datetime(now.year, now.month, 1)

        sql = """
        SELECT AVG(wpm) FROM wpm_data
        WHERE timestamp >= ? AND timestamp < ? AND period = 'week'
        """

        cursor = self._conn.execute(sql, (start.isoformat(), end.isoformat()))
        result = cursor.fetchone()[0]

        if result:
            self.save_wpm(wpm=result, format="month")
            self._cleanup_data(start, end, "week")

    def _cleanup_data(self, start_time, end_time, period_to_delete):
        sql = """
        DELETE FROM wpm_data
        WHERE timestamp >= ? AND timestamp < ? AND period = ?
        """
        self._conn.execute(
            sql, (start_time.isoformat(), end_time.isoformat(), period_to_delete)
        )
        self._conn.commit()

    def get_elapsed_data(self):
        sql = """
        SELECT timestamp, wpm, period FROM wpm_data
        WHERE period = 'elapsed'
        """

        cursor = self._conn.execute(sql)
        return cursor.fetchall()

    def get_minute_data(self):
        sql = """
        SELECT timestamp, wpm, period FROM wpm_data
        WHERE period = 'minute'
        """

        cursor = self._conn.execute(sql)
        return cursor.fetchall()

    def get_hour_data(self):
        sql = """
        SELECT timestamp, wpm, period FROM wpm_data
        WHERE period = 'hour'
        """

        cursor = self._conn.execute(sql)
        return cursor.fetchall()

    def get_day_data(self):
        sql = """
        SELECT timestamp, wpm, period FROM wpm_data
        WHERE period = 'day'
        """

        cursor = self._conn.execute(sql)
        return cursor.fetchall()

    def get_week_data(self):
        sql = """
        SELECT timestamp, wpm, period FROM wpm_data
        WHERE period = 'week'
        """

        cursor = self._conn.execute(sql)
        return cursor.fetchall()

    def get_month_data(self):
        sql = """
        SELECT timestamp, wpm, period FROM wpm_data
        WHERE period = 'month'
        """

        cursor = self._conn.execute(sql)
        return cursor.fetchall()
