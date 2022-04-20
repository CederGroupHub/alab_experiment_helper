from typing import List, Literal

from alab_experiment_helper.sample import Sample
from alab_experiment_helper.tasks.base import task


@task("HeatingWithAtmosphere")
def heat_with_atmosphere(samples: List[Sample], setpoints: List[List[int]],
                         atmosphere: Literal["Ar", "N2", "vacuum"]):
    if len(samples) > 4:
        raise ValueError("The number of samples should be <= 4")
    return {
        "setpoints": setpoints,
        "atmosphere": atmosphere,
    }