from datetime import datetime
import time


def create_run_id():
    return datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )


def start_timer():
    return time.perf_counter()


def calculate_duration(start_time):
    return time.perf_counter() - start_time