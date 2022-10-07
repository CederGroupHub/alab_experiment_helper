from typing import Literal

from alab_experiment_helper.sample import Sample
from alab_experiment_helper.tasks.base import task


@task("Diffraction", 1)
def xrd(schema: Literal["fast_10min", "slow_30min"] = "fast_10min"):
    """
    Do xrd on the given sample with the given ``schema``. The schema is either ``fast_10min`` or ``slow_30min``.

    Args:
        sample: Sample to do xrd on.
        schema: Schema to use. By default, a fast 10min schema is used. Options = ["fast_10min", "slow_30min"]
    """
    return {
        "schema": schema,
    }
