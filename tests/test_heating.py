from unittest import TestCase

from alab_experiment_helper.batch import Batch
from alab_experiment_helper.tasks.heating import simple_heating


class TestHeating(TestCase):
    def setUp(self) -> None:
        self.experiment = Batch("test_heating")

    def test_heating_simple(self):
        sample = self.experiment.add_sample("test_heating_sample")
        [sample] = simple_heating([sample], temperature=300, duration_hour=10)
        simple_heating([sample], temperature=300, duration_hour=10)
        print(self.experiment.to_dict())

    def test_heating_multiple(self):
        samples = [
            self.experiment.add_sample(f"test_heating_sample_{i}") for i in range(4)
        ]
        samples = simple_heating(samples, temperature=300, duration_hour=10)
        simple_heating(samples, temperature=300, duration_hour=10)
        print(self.experiment.to_dict())
