from alab_experiment_helper import Experiment
import pymongo
from pymongo.collection import Collection
from pymongo.database import Database


class QueueView:
    def __init__(self):
        self._db = pymongo.MongoClient(
            host="localhost",
            port=27017,
        )["ALabHelper"]
        self._jobs = self._db["jobs"]

    def add_experiment(self, experiment: Experiment):
        self._jobs.insert_one(experiment.to_dict())
