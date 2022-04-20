from typing import List

from alab_experiment_helper.sample import Sample
from alab_experiment_helper.tasks.base import task


@task("Mixing")
def mixing(samples: List[Sample], recipes: ...):
    """
    Mixing task.

    :param samples: List of samples to be mixed.
    :param recipes: List of recipes.
    """
    ...
