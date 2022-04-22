import uuid
from functools import wraps
from typing import Any, List, Union, Callable

from alab_experiment_helper.sample import Sample


def task(name) -> Callable[[Any], Any]:
    def _task(f):
        @wraps(f)
        def wrapper(samples: Union[Sample, List[Sample]], *task_args,
                    **task_kwargs: Any) -> Union[Sample, List[Sample]]:
            """
            This function is called by the experiment helper to create a task.
            """
            task_params = f(samples, *task_args, **task_kwargs)

            single_sample = False
            if isinstance(samples, Sample):
                samples = [samples]
                single_sample = True

            experiment = samples[0].experiment
            task_id = str(uuid.uuid4())
            experiment.add_task(task_id=task_id, task_name=name, task_params=task_params, samples=samples)

            for sample in samples:
                sample.add_task(task_id=task_id)
            return samples if not single_sample else samples[0]

        return wrapper
    return _task
