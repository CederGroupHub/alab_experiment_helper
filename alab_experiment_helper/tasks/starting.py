from alab_experiment_helper.sample import Sample
from alab_experiment_helper.tasks.base import task


@task("Starting", 1)
def starting(start_position: str):
    """
    Store the sample in the storage positions
    """
    return {
        "start_position": start_position,
    }
