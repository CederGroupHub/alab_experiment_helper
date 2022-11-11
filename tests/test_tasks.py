import pytest

from alab_experiment_helper import Batch
from alab_experiment_helper.tasks import *


@pytest.fixture
def experiment():
    return Batch("test")


def test_tasks(experiment: Batch):
    samples = [experiment.add_sample(name="sample_" + str(i)) for i in range(16)]
    sample_group_1 = samples[0:8]
    sample_group_2 = samples[8:12]
    sample_group_3 = samples[12:16]

    dispensing(samples, input_file_path="example.csv")

    heating(sample_group_1, [[300, 60], [300, 600]])
    heating_with_atmosphere(sample_group_2, [[300, 60], [300, 600]], atmosphere="Ar")
    heating_with_atmosphere(sample_group_3, [[300, 60], [300, 600]], atmosphere="N2")

    for sample in samples:
        scraping(sample, duration_min=6, ball_number=8)
        xrd(sample, schema="fast_10min")
        disposing(sample)

    experiment.generate_input_file("test.json", "json")
    # experiment.visualize(".")
