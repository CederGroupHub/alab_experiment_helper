from alab_experiment_helper.sample import Sample
from alab_experiment_helper.tasks.base import task


@task("Ending", 1)
def ending(end_position: str):
    """
    Store the sample in the storage positions
    """
    return {
        "end_position": end_position,
    }
