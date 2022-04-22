from typing import List

from alab_experiment_helper.sample import Sample
from alab_experiment_helper.tasks.base import task


@task("Heating")
def simple_heating(samples: List[Sample], temperature: int, duration_hour: float,
                   ramp_rate_per_min: int = 5):
    """
    Simple heating task. The furnace will be ramped up with the given ``ramp_temp_per_min`` and
    then hold at this temperature for the given ``duration_hour`` at given ``temperature``. After
    dwelling, it will be cooled down to some temperature (set by the driver, e.g. 400 °C) and be taken
    out of the furnace.

    Args:
        samples: List of samples to heat.
        temperature: Temperature (°C) to heat to, which should be a number between 0 and 1100. It specifies the
          temperature of dwelling.
        duration_hour: Duration of heating in hours (e.g. 12 hours). It specifies the duration hours of dwelling.
          It will first be converted to minute (rounded to integer) in the driver code.
        ramp_rate_per_min: Temperature change per minute during heating up process (e.g. 5 °C/min). By default, it
          is 5 °C/min.
    """
    if len(samples) > 8:
        raise ValueError("Heating task can only be applied to 8 samples at a time.")
    if temperature < 0 or temperature > 1100:
        raise ValueError("Temperature must be between 0 and 1100 °C.")
    if duration_hour < 0 or duration_hour > 16:
        raise ValueError("Duration must be between 0 and 16 hours.")
    if ramp_rate_per_min < 0 or ramp_rate_per_min > 20:
        raise ValueError("Ramp temperature per minute must be between 0 and 20 °C.")

    return {
        "setpoints": [
            [temperature, temperature / ramp_rate_per_min],
            [temperature, duration_hour * 60.],
        ],
    }


@task("Heating")
def heating(samples: List[Sample], setpoints: List[List[int]]):
    if len(samples) > 8:
        raise ValueError("Heating task can only be applied to 4 samples at a time.")

    return {
        "setpoints": setpoints
    }
