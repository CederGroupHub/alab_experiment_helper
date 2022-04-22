from alab_experiment_helper.sample import Sample
from alab_experiment_helper.tasks.base import task


@task("Scraping")
def scraping(samples: Sample, duration_min: int = 6, ball_number: int = 8):
    """
    Move the sample out of crucibles with ball milling. The ``duration_min`` specifies the duration of the shaking,
    and the ``ball_number`` specifies the number of balls to be used (5mm Al2O3 balls).

    Args:
        samples: The sample to be operated on.
        duration_min: The duration of the shaking in minutes.
        ball_number: The number of balls to be used (dispensed by milling ball dispenser).
    """
    return {
        "time": duration_min,
        "ball_number": ball_number,
    }
