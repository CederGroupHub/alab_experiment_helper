from abc import ABC, abstractmethod
from functools import wraps
from math import ceil
from typing import Any, Callable, Dict, List, TypeVar, Union
from bson import ObjectId
from alab_experiment_helper.batch import Batch
from alab_experiment_helper.sample import Sample

# from functools import wraps
# from typing import Any, List, TypeVar, Union, Callable
# from math import ceil
# from alab_experiment_helper.experiment import Experiment
# from alab_experiment_helper.sample import Sample


# class BaseTask(ABC):
#     def __init__(self, name: str, capacity: int, _id: ObjectId = None):
#         self.name = name
#         self.capacity = capacity
#         if _id is None:
#             self._id = ObjectId()
#         else:
#             self._id = _id

#     @abstractmethod
#     def get_parameters(self) -> Dict[str, Any]:
#         """This should return a dictionary with any parameters needed to run the task.

#         For example, a heating task might return:
#         {
#             "temperature_celsiue": 100,
#             "duration_minutes": 60,
#         }

#         Returns:
#             Dict[str, Any]: dictionary of task parameters
#         """
#         return {}

#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             "_id": self._id,
#             "name": self.name,
#             "capacity": self.capacity,
#             "parameters": self.get_parameters(),
#         }


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

            if isinstance(samples, Sample):
                samples = [samples]
            for sample in samples:
                sample.add_task(
                    task_id=str(ObjectId()),
                    task_name=name,
                    task_parameters=task_params,
                    capacity=capacity,
                )

        return wrapper

    return _task
