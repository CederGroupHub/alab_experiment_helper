from typing import Any, List, Dict, TYPE_CHECKING, Optional, Union
from pydantic import (
    BaseModel,
    constr,
    validator,
    Field,
)  # pylint: disable=no-name-in-module

from bson import ObjectId

# if TYPE_CHECKING:
#     from .batch import Batch


class Sample:
    def __init__(self, name: str, tags: List[str] = None, **metadata):
        self.name = name
        self._tasks: List[str] = []
        self.tags = tags or []
        self.metadata = metadata
        self._id = str(ObjectId())

    def add_task(
        self,
        task_id: str,
        task_name: str,
        task_parameters: Dict[str, Any],
        capacity: int,
    ) -> None:
        task_entry = {
            "_id": str(task_id),
            "type": task_name,
            "parameters": task_parameters,
            "capacity": capacity,
            "samples": [self._id],
            "prev_tasks": [],
        }
        if len(self._tasks) > 0:
            task_entry["prev_tasks"].append(self._tasks[-1]["_id"])
        self._tasks.append(task_entry)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": str(self._id),
            "name": self.name,
            "tags": self.tags,
            "tasks": self._tasks,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Sample":
        instance = cls(
            name=data["name"],
            tags=data["tags"],
            **data["metadata"],
        )
        instance._tasks = data["tasks"]
        instance._id = data["_id"]

        return instance

    @property
    def tasks(self):
        return self._tasks

    def __eq__(self, other):
        return self._id == other._id


### Format checking for API inputs


class TaskInputFormat(BaseModel):
    id: Optional[Any] = Field(None, alias="id")
    type: str
    parameters: Dict[str, Any]
    capacity: int
    prev_tasks: List[str]
    samples: List[Union[str, Any]]

    @validator("id")
    def must_be_valid_objectid(cls, v):
        try:
            ObjectId(v)
        except:
            raise ValueError(f"Received invalid _id: {v} is not a valid ObjectId!")
        return v

    @validator("capacity")
    def must_be_positive(cls, v):
        if v < 0:
            raise ValueError(f"Capacity must be positive, received {v}")
        return v

    @validator("samples")
    def samples_must_be_valid_objectid(cls, v):
        for sample_id in v:
            try:
                ObjectId(sample_id)
            except:
                raise ValueError(
                    f"Received invalid sample_id: {sample_id} is not a valid ObjectId!"
                )
        return v

    @validator("prev_tasks")
    def prevtasks_must_be_valid_objectid(cls, v):
        for task_id in v:
            try:
                ObjectId(task_id)
            except:
                raise ValueError(
                    f"Received invalid sample_id: {task_id} is not a valid ObjectId!"
                )
        return v


class SampleInputFormat(BaseModel):
    """
    Format check for API for Sample submission. Sample's must follow this format to be accepted into the batching queue.
    """

    id: Optional[Any] = Field(None, alias="id")
    name: constr(regex=r"^[^$.]+$")  # type: ignore # noqa: F722
    tags: List[str]
    tasks: List[TaskInputFormat]
    metadata: Dict[str, Any]

    @validator("id")
    def must_be_valid_objectid(cls, v):
        try:
            ObjectId(v)
        except:
            raise ValueError(f"Received invalid _id: {v} is not a valid ObjectId!")
        return v
