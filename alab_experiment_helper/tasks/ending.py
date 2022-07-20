from alab_experiment_helper.sample import Sample
from alab_experiment_helper.tasks.base import task


@task("Ending")
def ending(sample: Sample):
    """
    Store the sample in the storage positions
    """
    return {}
