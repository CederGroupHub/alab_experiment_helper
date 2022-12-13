from typing import List, Literal

from alab_experiment_helper.sample import Sample
from alab_experiment_helper.tasks.base import task

ALLOWED_ATMOSPHERES = ["Ar", "O2", "2H_98Ar"]


@task("HeatingWithAtmosphere")
def heating_with_atmosphere(
    samples: List[Sample],
    setpoints: List[List[int]],
    atmosphere: Literal["Ar", "O2", "2H_98Ar"],
    flow_rate_ccm: float = 100,
):
    """
    Annealing in the tube furnaces. You can select the atmosphere for heating. Four samples at a time for heating.
    The parameter setpoints is a list of [duration, temperature] pairs. The temperature is in °C and the duration
    is in minutes. The range of flow_rate should be between 0 and 1000.

    Args:
        samples: the samples to heat
        setpoints: list of [duration (minutes), temperature (celsius)], e.g., [[60, 300], [7200, 300]] means to heat up to 300°C in 60 min
          in and keep it at 300°C for 12 h.
        atmosphere: the gas atmosphere for the operation. You can choose between ``Ar``, ``O2`` and ``2H_98Ar``.
        flow_rate: the flow rate of the gas in the furnace.
    """
    if len(samples) > 4:
        raise ValueError("The number of samples should be <= 4")
    if atmosphere not in ALLOWED_ATMOSPHERES:
        raise ValueError(f"The atmosphere should be one of {ALLOWED_ATMOSPHERES}")
    if flow_rate_ccm < 0 or flow_rate_ccm > 1000:
        raise ValueError(
            "The flow rate should be between 0 and 1000 ccm"
        )  # TODO units of flow rate?

    # TODO make sure ramp rates, temperature ranges are respected in setpoints
    return {
        "samples": [sample.name for sample in samples],
        "setpoints": setpoints,
        "atmosphere": atmosphere,
        "flow_rate": flow_rate_ccm,
    }


@task("HeatingWithAtmosphere")
def simple_heating_with_atmosphere(
    samples: List[Sample],
    heating_time_minutes: float,
    heating_temperature_celsius: float,
    atmosphere: Literal["Ar", "O2", "2H_98Ar"],
    ramp_rate_celsius_per_min: int = 5,
    flow_rate_ccm: float = 100,
):
    """Basic annealing in the tube furnaces. Ramp up to a set point, hold for some time, ramp down to room temperature.
    You can select the atmosphere for heating. Up to four samples at a time for heating.
    The The temperature is in °C and the duration, is in minutes. The range of flow_rate should be between 0 and 1000.

    Args:
        samples (List[Sample]): samples to heat. max four samples
        heating_time_minutes (float): duration (minutes) to hold at the set temperature
        heating_temperature_celsius (float): temperature (celsius) to heat to
        atmosphere (Literal[&quot;Ar&quot;, &quot;O2&quot;, &quot;2H_98Ar&quot;]): gas environment to heat in
        ramp_rate_celsius_per_min (int, optional): ramp rate (celsius/minute) to heat at. Defaults to 5.
        flow_rate_ccm (float, optional): gas flow rate, in cubic centimeters per minute. Defaults to 100.
    """
    if len(samples) > 4:
        raise ValueError("The number of samples should be <= 4")
    if atmosphere not in ALLOWED_ATMOSPHERES:
        raise ValueError(f"The atmosphere should be one of {ALLOWED_ATMOSPHERES}")
    if flow_rate_ccm < 0 or flow_rate_ccm > 1000:
        raise ValueError(
            "The flow rate should be between 0 and 1000 ccm"
        )  # TODO units of flow rate?
    if heating_time_minutes < 0:
        raise ValueError("The heating time should be >= 0")
    if (
        heating_temperature_celsius < 0 or heating_temperature_celsius > 1500
    ):  # TODO check the bounds
        raise ValueError("The heating temperature should be between 0 and 1500")
    if ramp_rate_celsius_per_min < 1 or ramp_rate_celsius_per_min > 20:
        raise ValueError("The ramp rate should be between 1 and 20 degrees C/minute")

    setpoints = [
        (
            heating_temperature_celsius,
            heating_temperature_celsius / ramp_rate_celsius_per_min,
        ),
        (heating_temperature_celsius, heating_time_minutes),
    ]

    return {
        "samples": [sample.name for sample in samples],
        "setpoints": setpoints,
        "atmosphere": atmosphere,
        "flow_rate": flow_rate_ccm,
    }
