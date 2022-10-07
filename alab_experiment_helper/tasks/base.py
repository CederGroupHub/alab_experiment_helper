import uuid
from functools import wraps
from typing import Any, List, TypeVar, Union, Callable
from math import ceil
from alab_experiment_helper.experiment import Experiment
from alab_experiment_helper.sample import Sample


_TFunc = TypeVar("_TFunc", bound=Callable[..., Any])


def task(name: str, capacity: int):  # -> Callable[[Any], Any]:
    def _task(f) -> _TFunc:
        @wraps(f)
        def wrapper(
            samples: Union[Sample, List[Sample]], *task_args, **task_kwargs: Any
        ) -> Union[Sample, List[Sample]]:
            """
            This function is called by the experiment helper to create a task.
            """
            task_params = f(*task_args, **task_kwargs)

            single_sample = False
            if isinstance(samples, Sample):
                samples = [samples]
                single_sample = True
            # if len(samples) > capacity:
            #     raise ValueError(
            #         f"Task {name} can only handle {capacity} samples, but got {len(samples)} samples!"
            #     )

            experiment: Experiment = samples[
                0
            ].experiment  # assume all samples fall under same experiment

            # if we have more samples than capacity, we need to split them into multiple tasks
            batches = ceil(len(samples) / capacity)
            for i in range(batches):
                task_id = str(uuid.uuid4())
                batch_samples = samples[i * capacity : (i + 1) * capacity]
                experiment.add_task(
                    task_id=task_id,
                    task_name=name,
                    task_params=task_params,
                    samples=batch_samples,
                )
                for sample in batch_samples:
                    sample.add_task(task_id)

            return samples if not single_sample else samples[0]

        return wrapper

    return _task
