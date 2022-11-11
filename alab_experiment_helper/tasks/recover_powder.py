from typing import List

from alab_experiment_helper.tasks.base import task


@task("RecoverPowder", 1)
def recover_powder(
    num_balls: int = 10,
    crucible_shake_duration_seconds: float = 30,
    vial_shake_duration_seconds: float = 300,
):
    """
    Recover powder from crucible into a plastic vial.
    """
    return {
        "num_balls": num_balls,
        "crucible_shake_duration_seconds": crucible_shake_duration_seconds,
        "vial_shake_duration_seconds": vial_shake_duration_seconds,
    }
