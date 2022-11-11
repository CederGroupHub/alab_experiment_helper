from pathlib import Path
from typing import List, Union, Dict

from alab_experiment_helper.tasks.base import task


@task("Dispensing", 16)
def dispensing(
    powder_dispenses: Dict[str, float],
    heating_duration: int = 300,
    ethanol_volume: int = 10000,
    transfer_volume: int = 8000,
    mixer_speed: int = 2000,
    mixer_duration: int = 900,
    min_transfer_mass: int = 5,
):
    """
    Dispense samples according to the given recipes in ``.csv`` format.

    The number of input samples must be equal to the number of recipes * replicates.

    Args:
        powder_dispenses: A dictionary of powder names and their dispense masses.
        heating_duration: The duration of the heating step in seconds.
        ethanol_volume: The volume of ethanol to dispense in microliters.
        transfer_volume: The volume of ethanol to transfer in microliters.
        mixer_speed: The speed of the mixer in RPM.
        mixer_duration: The duration of the mixer in seconds.
        min_transfer_mass: The minimum mass of powder to transfer in milligrams.

    """

    return {
        "powder_dispenses": powder_dispenses,
        "heating_duration": heating_duration,
        "ethanol_volume": ethanol_volume,
        "transfer_volume": transfer_volume,
        "mixer_speed": mixer_speed,
        "mixer_duration": mixer_duration,
        "min_transfer_mass": min_transfer_mass,
    }
