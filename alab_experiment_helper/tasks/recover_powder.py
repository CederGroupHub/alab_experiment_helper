from typing import List

from alab_experiment_helper.sample import Sample
from alab_experiment_helper.tasks.base import task


@task("RecoverPowder")
def recover_powder(
    sample: Sample,
    num_balls: int = 1,
    crucible_shake_duration_seconds: float = 120,
    vial_shake_duration_seconds: float = 0,
):
    """
    Recover powder from crucible into a plastic vial.
    """
    return {
        "sample": sample.name,
        "num_balls": num_balls,
        "crucible_shake_duration_seconds": crucible_shake_duration_seconds,
        "vial_shake_duration_seconds": vial_shake_duration_seconds,
    }
