from typing import List, TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from .experiment import Experiment


class Sample:
    def __init__(self, name: str, experiment: "Experiment"):
        self.name = name
        self._tasks: List[str] = []
        self.experiment: "Experiment" = experiment

    def add_task(self, task_id: str):
        self._tasks.append(task_id)

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name
        }

    @property
    def tasks(self):
        return self._tasks
