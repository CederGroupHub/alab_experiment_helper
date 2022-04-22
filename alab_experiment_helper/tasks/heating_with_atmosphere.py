from typing import List, Literal

from alab_experiment_helper.sample import Sample
from alab_experiment_helper.tasks.base import task


@task("HeatingWithAtmosphere")
def heating_with_atmosphere(samples: List[Sample], setpoints: List[List[int]],
                            atmosphere: Literal["Ar", "N2", "vacuum"], flow_rate: float = 100):
    """
    Annealing in the tube furnaces. You can select the atmosphere for heating. Four samples at a time for heating.

    Args:
        samples: the samples to heat
        setpoints: list of [temperature, duration], e.g., [[300, 60], [300, 7200]] means to heat up to 300°C in 60 min
          in and keep it at 300°C for 12 h.
        atmosphere: the gas atmosphere for the operation. You can choose between ``Ar``, ``N2`` and ``vacuum``.
        flow_rate: the flow rate of the gas in the furnace.
    """
    if len(samples) > 4:
        raise ValueError("The number of samples should be <= 4")
    if atmosphere not in ["Ar", "N2", "vacuum"]:
        raise ValueError("The atmosphere should be either ``Ar``, ``N2`` or ``vacuum``")
    if flow_rate < 0 or flow_rate > 1000:
        raise ValueError("The flow rate should be between 0 and 1000")

    return {
        "setpoints": setpoints,
        "atmosphere": atmosphere,
        "flow_rate": flow_rate,
    }
