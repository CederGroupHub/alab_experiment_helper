from unittest import TestCase

from alab_experiment_helper.batch import Batch
from alab_experiment_helper.tasks.heating_with_atmosphere import heating_with_atmosphere


class TestHeating(TestCase):
    def setUp(self) -> None:
        self.experiment = Batch("test_heating")

    def test_heating_simple(self):
        sample = self.experiment.add_sample("test_heating_sample")
        [sample] = heating_with_atmosphere(
            [sample], setpoints=[[300, 60], [300, 6000]], atmosphere="Ar"
        )
        heating_with_atmosphere(
            [sample], setpoints=[[300, 60], [300, 6000]], atmosphere="Ar"
        )
        print(self.experiment.to_dict())

    def test_heating_multiple(self):
        samples = [
            self.experiment.add_sample(f"test_heating_sample_{i}") for i in range(4)
        ]
        samples = heating_with_atmosphere(
            samples, setpoints=[[300, 60], [300, 6000]], atmosphere="Ar"
        )
        heating_with_atmosphere(
            samples, setpoints=[[300, 60], [300, 6000]], atmosphere="Ar"
        )
        print(self.experiment.to_dict())
