import datetime
from enum import Enum
from typing import Any, Dict, List
from alab_experiment_helper.sample import Sample
from alab_experiment_helper.batch import Batch
import pymongo
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId


class BatchStatus(Enum):
    PENDING = "pending"  # waiting to be batched and sent to alab_management
    RUNNING = "running"  # being processed by alab_management
    READYFORDATABASE = "readyfordatabase"  # completed on alab_management. now ready for data to be moved to permanent database
    COMPLETE = "complete"  # both batch and data handling are complete
    FAILED = "failed"  # batch failed on alab_management


class BatchView:
    def __init__(self):
        self._db = pymongo.MongoClient(
            host="localhost",
            port=27017,
        )["ALabHelper"]
        self._collection = self._db["batches"]

    def add(self, batch: Batch):
        entry = batch.to_dict()
        entry["created_at"] = entry["updated_at"] = datetime.datetime.now()
        entry["status"] = BatchStatus.PENDING.value
        result = self._collection.insert_one(entry)

        return result.inserted_id

    def remove(self, batch_id: ObjectId):
        result = self._collection.delete_one({"_id": batch_id})
        if result.deleted_count == 0:
            raise ValueError("No sample with id {} found".format(batch_id))

    def get(self, batch_id: ObjectId) -> Dict[str, Any]:
        """Returns a sample with given id."""
        return list(self._collection.find_one({"_id": batch_id}))

    def _get_by_status(self, status: BatchStatus) -> List[Dict[str, Any]]:
        """Returns all samples with given status, sorted from oldest -> youngest."""
        return list(
            self._collection.find({"status": status.value}).sort(
                "created_at", pymongo.ASCENDING
            )
        )

    def get_pending(self) -> List[Dict[str, Any]]:
        """Returns all pending samples, sorted from oldest -> youngest."""
        return self._get_by_status(BatchStatus.PENDING)

    def get_running(self) -> List[Dict[str, Any]]:
        """Returns all running samples, sorted from oldest -> youngest."""
        return self._get_by_status(BatchStatus.RUNNING)

    def get_completed(self) -> List[Dict[str, Any]]:
        """Returns all completed samples, sorted from oldest -> youngest."""
        return self._get_by_status(BatchStatus.COMPLETE)

    def get_failed(self) -> List[Dict[str, Any]]:
        """Returns all failed samples, sorted from oldest -> youngest."""
        return self._get_by_status(BatchStatus.FAILED)

    def set_status(self, batch_id: ObjectId, status: BatchStatus):
        """Changes the status of a sample."""
        result = self._collection.update_one(
            {"_id": batch_id},
            {"$set": {"status": status.value, "updated_at": datetime.datetime.now()}},
        )
        if result.modified_count == 0:
            raise ValueError("No sample with id {} found".format(batch_id))
