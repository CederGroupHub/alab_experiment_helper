import datetime
from enum import Enum
from typing import Any, Dict, List
from alab_experiment_helper.sample import Sample
import pymongo
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId


class SampleStatus(Enum):
    PENDING = "pending"  # waiting to be batched and sent to alab_management
    RUNNING = "running"  # being processed by alab_management
    READYFORDATABASE = "readyfordatabase"  # completed on alab_management. now ready for data to be moved to permanent database
    COMPLETE = "complete"  # both experiment and data handling are complete
    FAILED = "failed"  # experiment failed on alab_management


class SampleView:
    def __init__(self):
        self._db = pymongo.MongoClient(
            host="localhost",
            port=27017,
        )["ALabHelper"]
        self._collection = self._db["samples"]

    def add_sample(self, sample: Sample):
        entry = sample.to_dict()
        entry["_id"] = ObjectId(entry["_id"])  # convert string to ObjectId
        entry["created_at"] = entry["updated_at"] = datetime.datetime.now()
        entry["status"] = SampleStatus.PENDING.value
        result = self._collection.insert_one(entry)

        return result.inserted_id

    def remove_sample(self, sample_id: ObjectId):
        result = self._collection.delete_one({"_id": sample_id})
        if result.deleted_count == 0:
            raise ValueError("No sample with id {} found".format(sample_id))

    def get_sample(self, sample_id: ObjectId) -> Dict[str, Any]:
        """Returns a sample with given id."""
        result = self._collection.find_one({"_id": sample_id})
        if result is None:
            raise ValueError("No sample with id {} found".format(sample_id))
        return result

    def _get_by_status(self, status: SampleStatus) -> List[Dict[str, Any]]:
        """Returns all samples with given status, sorted from oldest -> youngest."""
        return list(
            self._collection.find({"status": status.value}).sort(
                "created_at", pymongo.ASCENDING
            )
        )

    def get_pending(self) -> List[Dict[str, Any]]:
        """Returns all pending samples, sorted from oldest -> youngest."""
        return self._get_by_status(SampleStatus.PENDING)

    def get_running(self) -> List[Dict[str, Any]]:
        """Returns all running samples, sorted from oldest -> youngest."""
        return self._get_by_status(SampleStatus.RUNNING)

    def get_readyfordatabase(self) -> List[Dict[str, Any]]:
        """Returns all samples that are ready for database, sorted from oldest -> youngest."""
        return self._get_by_status(SampleStatus.READYFORDATABASE)

    def get_completed(self) -> List[Dict[str, Any]]:
        """Returns all completed samples, sorted from oldest -> youngest."""
        return self._get_by_status(SampleStatus.COMPLETE)

    def get_failed(self) -> List[Dict[str, Any]]:
        """Returns all failed samples, sorted from oldest -> youngest."""
        return self._get_by_status(SampleStatus.FAILED)

    def set_status(self, sample_id: ObjectId, status: SampleStatus):
        """Changes the status of a sample."""
        result = self._collection.update_one(
            {"_id": sample_id},
            {"$set": {"status": status.value, "updated_at": datetime.datetime.now()}},
        )
        if result.modified_count == 0:
            raise ValueError("No sample with id {} found".format(sample_id))

    def mark_as_running(
        self, sample_id: ObjectId, alab_management_experiment_id: ObjectId
    ):
        """Marks a sample as running and record the experiment id corresponding to the sample's batch on alab_management."""
        result = self._collection.update_one(
            {"_id": sample_id},
            {
                "$set": {
                    "status": SampleStatus.RUNNING.value,
                    "alab_management_experiment_id": alab_management_experiment_id,
                    "updated_at": datetime.datetime.now(),
                }
            },
        )
        if result.modified_count == 0:
            raise ValueError("No sample with id {} found".format(sample_id))

    def _clear_collection(self):
        self._collection.drop()
