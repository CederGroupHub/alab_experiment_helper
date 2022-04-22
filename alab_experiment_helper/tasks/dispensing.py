from pathlib import Path
from typing import List, Union

from alab_experiment_helper.sample import Sample
from alab_experiment_helper.tasks.base import task


@task("Dispensing")
def dispensing(
        samples: List[Sample],
        input_file_path: Union[str, Path],
):
    """
    Dispense samples according to the given recipes in ``.csv`` format.

    The number of input samples should be equal to the number of recipes * replicates.

    Args:
        samples: the samples to be operated on, in this setting, each sample is a crucible
        input_file_path: the path to the input file, which is a csv file.
    """
    if not isinstance(input_file_path, Path):
        input_file_path = Path(input_file_path)
    # with input_file_path.open("r", encoding="utf-8") as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     total_sample_num = sum(row["replicates"] for row in reader)
    #     if len(samples) != total_sample_num:
    #         raise ValueError("Unmatched number of samples and recipes!")
    return {
        "input_file_path": input_file_path.as_posix(),
    }
