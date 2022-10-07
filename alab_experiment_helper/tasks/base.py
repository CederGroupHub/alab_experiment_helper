import uuid
from functools import wraps
from typing import Any, List, TypeVar, Union, Callable

from alab_experiment_helper.sample import Sample


_TFunc = TypeVar("_TFunc", bound=Callable[..., Any])


def task(name:str, capacity:int):  # -> Callable[[Any], Any]:
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
            if len(samples) > capacity:
                raise ValueError(
                    f"Task {name} can only handle {capacity} samples, but got {len(samples)} samples!"
                )

            experiment = samples[0].experiment
            task_id = str(uuid.uuid4())
            experiment.add_task(
                task_id=task_id,
                task_name=name,
                task_params=task_params,
                samples=samples,
            )

            for sample in samples:
                sample.add_task(task_id=task_id)
            return samples if not single_sample else samples[0]

        return wrapper

    return _task
