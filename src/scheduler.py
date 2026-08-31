from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Optional


@dataclass
class ScheduleConfig:
    """
    Configuration for FinOps pipeline scheduling.
    """

    interval_minutes: int = 60
    enabled: bool = True

    def __post_init__(self):
        if self.interval_minutes <= 0:
            raise ValueError(
                "interval_minutes must be greater than 0"
            )


def calculate_next_run(
    last_run: datetime,
    interval_minutes: int
) -> datetime:
    """
    Calculate the next scheduled execution time.
    """

    if interval_minutes <= 0:
        raise ValueError(
            "interval_minutes must be greater than 0"
        )

    return (
        last_run
        + timedelta(minutes=interval_minutes)
    )


def is_schedule_due(
    current_time: datetime,
    next_run: datetime
) -> bool:
    """
    Determine whether a scheduled execution is due.
    """

    return current_time >= next_run


def execute_scheduled_run(
    pipeline_function: Callable[[], object]
):
    """
    Execute the FinOps pipeline through a callback.
    """

    if not callable(pipeline_function):
        raise TypeError(
            "pipeline_function must be callable"
        )

    return pipeline_function()


def run_scheduler_cycle(
    current_time: datetime,
    last_run: Optional[datetime],
    config: ScheduleConfig,
    pipeline_function: Callable[[], object]
):
    """
    Execute one scheduler evaluation cycle.

    Returns:
        (execution_result, next_run)

    If the scheduler is disabled or the run is not due,
    execution_result is None.
    """

    if not config.enabled:
        return None, None

    if last_run is None:
        next_run = current_time
    else:
        next_run = calculate_next_run(
            last_run,
            config.interval_minutes
        )

    if not is_schedule_due(
        current_time,
        next_run
    ):
        return None, next_run

    result = execute_scheduled_run(
        pipeline_function
    )

    next_run = calculate_next_run(
        current_time,
        config.interval_minutes
    )

    return result, next_run
