from alab_experiment_helper.sample import Sample
from alab_experiment_helper.tasks.base import task


@task("Scraping")
def scraping(samples: Sample, duration_min: int = 6, ball_number: int = 8):
    """

    Args:
        samples:
        duration_min:
        ball_number:

    Returns:

    """
    return {
        "time": duration_min,
        "ball_number": ball_number,
    }
