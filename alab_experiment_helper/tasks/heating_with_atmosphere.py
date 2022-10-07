from typing import List, Literal

from alab_experiment_helper.sample import Sample
from alab_experiment_helper.tasks.base import task


@task("HeatingWithAtmosphere", 4)
def heating_with_atmosphere(
    setpoints: List[List[int]],
    atmosphere: Literal["Ar", "N2"],
    flow_rate_ccm: float = 100,
):
    """
    Annealing in the tube furnaces. You can select the atmosphere for heating. Four samples at a time for heating.
    The parameter setpoints is a list of [temperature, duration] pairs. The temperature is in °C and the duration
    is in minutes. The range of flow_rate should be between 0 and 1000.

    Args:
        samples: the samples to heat
        setpoints: list of [temperature, duration], e.g., [[300, 60], [300, 7200]] means to heat up to 300°C in 60 min
          in and keep it at 300°C for 12 h.
        atmosphere: the gas atmosphere for the operation. You can choose between ``Ar``, ``N2`` and ``vacuum``.
        flow_rate: the flow rate of the gas in the furnace.
    """
    # if len(samples) > 4:
    #     raise ValueError("The number of samples should be <= 4")
    if atmosphere not in ["Ar", "N2", "vacuum"]:
        raise ValueError("The atmosphere should be either ``Ar``, ``N2`` or ``vacuum``")
    if flow_rate_ccm < 0 or flow_rate_ccm > 1000:
        raise ValueError(
            "The flow rate should be between 0 and 1000"
        )  # TODO units of flow rate?

    # TODO make sure ramp rates, temperature ranges are respected in setpoints
    return {
        "setpoints": setpoints,
        "atmosphere": atmosphere,
        "flow_rate": flow_rate_ccm,
    }


@task("HeatingWithAtmosphere", 4)
def simple_heating_with_atmosphere(
    heating_time_minutes: float,
    heating_temperature_celsius: float,
    atmosphere: Literal["Ar", "N2"],
    ramp_rate_celsius_per_min: int = 5,
    flow_rate_ccm: float = 100,
):
    """
    Annealing in the tube furnaces. You can select the atmosphere for heating. Four samples at a time for heating.
    The parameter setpoints is a list of [temperature, duration] pairs. The temperature is in °C and the duration
    is in minutes. The range of flow_rate should be between 0 and 1000.

    Args:
        samples: the samples to heat
        setpoints: list of [temperature, duration], e.g., [[300, 60], [300, 7200]] means to heat up to 300°C in 60 min
          in and keep it at 300°C for 12 h.
        atmosphere: the gas atmosphere for the operation. You can choose between ``Ar``, ``N2`` and ``vacuum``.
        flow_rate: the flow rate of the gas in the furnace.
    """
    # if len(samples) > 4:
    #     raise ValueError("The number of samples should be <= 4")
    if atmosphere not in ["Ar", "N2"]:
        raise ValueError("The atmosphere should be either ``Ar``, ``N2`` or ``vacuum``")
    if flow_rate_ccm < 0 or flow_rate_ccm > 1000:  # TODO check the bounds. units?
        raise ValueError(
            "The flow rate should be between 0 and 1000"
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
        "setpoints": setpoints,
        "atmosphere": atmosphere,
        "flow_rate": flow_rate_ccm,
    }
