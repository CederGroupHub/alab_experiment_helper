from alab_experiment_helper.tasks.base import task


@task("Disposing", 1)
def disposing():
    """
    Store the sample in the storage positions
    """
    return {}
