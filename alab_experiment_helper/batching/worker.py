import datetime
import requests
from ..views.sample import SampleView, SampleStatus
from .utils import (
    experiment_to_digraph,
    get_subgraphs,
    samples_in_graph,
    subgraph_from_node,
    merge_nodes,
    sampledict_to_graph,
    is_graph_saturated,
)
from typing import Any, Dict, Iterable, List
import networkx as nx
from bson import ObjectId
import time


class QueueWorker:
    MAX_WAIT_TIME_SECONDS = 60 * 30  # 30 minutes
    PROCESSING_INTERVAL = 1  # seconds between trying to batch and submit experiments

    API_ENDPOINTS = {
        "submit_experiment": "/api/experiment/submit",
        "experiment_status": "/api/experiment/",
    }

    def __init__(self, api_url="https://localhost", api_port=8896):
        self._sampleview = SampleView()
        self.API_URL = f"{api_url}:{api_port}"

    def run(self):
        while True:
            self.process_pending_samples()
            self.look_for_completed_samples()
            time.sleep(self.PROCESSING_INTERVAL)

    ### Batching and starting samples that are pending in the queue
    def process_pending_samples(self):
        pending = self._sampleview.get_pending()
        pending_graphs = [sampledict_to_graph(s) for s in pending]
        batched_graphs = self._batch_graphs(pending_graphs)

        for bg in batched_graphs:
            if (self._get_graph_age(bg) >= self.MAX_WAIT_TIME_SECONDS) or (
                is_graph_saturated(bg)
            ):
                # experiment = self._build_alabmanagement_experiment(bg)  # TODO
                self._start_experiment(bg)

    def _get_graph_age(self, graph: nx.DiGraph) -> int:
        """Get the age of the graph in seconds

        Args:
            graph (nx.DiGraph): graph to get age of

        Returns:
            int: age of graph in seconds
        """
        sample_creation_times = []
        for sample in samples_in_graph(graph):
            entry = self._sampleview.get_sample(ObjectId(sample))
            sample_creation_times.append(entry["created_at"])
        oldest_sample_creation_time = min(sample_creation_times)
        return (datetime.datetime.now() - oldest_sample_creation_time).seconds

    def _batch_graphs(self, graphs: List[nx.DiGraph]) -> List[nx.DiGraph]:
        """Batch graphs to optimally use available task capacity. Existing graphs (i.e. an experiment submitted by the user) will never be broken up.

        Args:
            graphs (List[nx.Digraph]): list of graphs to batch

        Returns:
            List[nx.DiGraph]: list of graphs after batching. This is hopefully shorter than the input list.
        """
        if len(graphs) == 0:
            return []
        total_graph = graphs[0]
        for g in graphs[1:]:
            total_graph = nx.compose(total_graph, g)

        ## batch furnace tasks first
        merge_nodes(
            total_graph,
            "Heating",
            merge_allowed_fn=lambda x, y: x["parameters"] == y["parameters"],
        )
        merge_nodes(
            total_graph,
            "HeatingWithAtmosphere",
            merge_allowed_fn=lambda x, y: x["parameters"] == y["parameters"],
        )

        ## batch all other tasks. For now, this is just Dispensing from the Labman.

        # TODO for now, dispenses will be condensed randomly. We may want to put similar powder dispenses together to consolidate errors from powder handling (ie a jammed powder dosing head) to fewer workflows. clustering/ranking by Jaccard similarity of required powder sets should work.
        for subgraph in get_subgraphs(total_graph):
            merge_nodes(subgraph, "Dispensing", parent_graph=total_graph)
        merge_nodes(total_graph, "Dispensing")

        return get_subgraphs(total_graph)

    def _start_experiment(self, experiment_graph: nx.DiGraph):
        experiment = self._build_alabmanagement_experiment(experiment_graph)

        try:
            alab_management_experiment_id = self._send_experiment_to_management(
                experiment
            )
        except Exception as e:
            print(f"Error sending experiment to alab_management: {e}")
        else:
            for sample in experiment["samples"]:
                self._sampleview.mark_as_running(
                    sample_id=ObjectId(sample["_id"]),
                    alab_management_experiment_id=ObjectId(
                        alab_management_experiment_id
                    ),
                )

    def _send_experiment_to_management(self, experiment: Dict[str, Any]) -> ObjectId:
        response = requests.post(
            f"{self.API_URL}/api/experiment/submit", json=experiment
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to send experiment to management server. Server response: {response.text}"
            )
        resp_json = response.json()
        return ObjectId(resp_json["data"]["exp_id"])

    def _build_alabmanagement_experiment(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Build an experiment for alabmanagement from a graph.

        Args:
            graph (nx.DiGraph): graph to build experiment from

        Returns:
            Dict: experiment for alabmanagement
        """
        experiment = {
            "name": "Experiment",  # TODO unique name? maybe not required
            "samples": [],
            "tasks": [],
        }
        _already_added_sampleids = {}
        _task_ids = []
        for task_id in nx.topological_sort(graph):
            node = graph.nodes[task_id]
            for sample_id in node["samples"]:
                if sample_id in _already_added_sampleids:
                    continue
                original_sample_name = self._sampleview.get_sample(sample_id)["name"]
                unique_sample_name = self._make_unique_sample_name(
                    original_sample_name, _already_added_sampleids.values()
                )
                _already_added_sampleids[sample_id] = unique_sample_name

                experiment["samples"].append(
                    {
                        "name": unique_sample_name,
                        "_id": str(sample_id),
                    }
                )

            _task_ids.append(task_id)
            task_entry = {
                "type": node["type"],
                "prev_tasks": list(graph.predecessors(task_id)),
                "samples": [_already_added_sampleids[s] for s in node["samples"]],
            }
            if node["type"] in ["Dispensing"]:
                task_entry["parameters"] = node["parameters_per_sample"]
            else:
                task_entry["parameters"] = node["parameters"]
            experiment["tasks"].append(task_entry)

        # convert prev tasks from _id to index to keep with alab_management convention
        for task in experiment["tasks"]:
            task["prev_tasks"] = [_task_ids.index(t) for t in task["prev_tasks"]]

        return experiment

    def _make_unique_sample_name(
        self, sample_name: str, existing_names: Iterable[str]
    ) -> str:
        """Make a unique sample name by appending a number to the end of the name if necessary."""
        if sample_name not in existing_names:
            return sample_name
        idx = 1
        new_name = f"{sample_name}_{idx}"
        while new_name in existing_names:
            idx += 1
            new_name = f"{sample_name}_{idx}"
        return new_name

    ### Handling completed or failed samples

    def look_for_completed_samples(self):
        """Process samples that have been completed by alabmanagement."""
        samples = self._sampleview.get_running()

        samples_per_experiment = {}
        for entry in samples:
            if entry["alab_management_experiment_id"] not in samples_per_experiment:
                samples_per_experiment[entry["alab_management_experiment_id"]] = []
            samples_per_experiment[entry["alab_management_experiment_id"]].append(
                entry["_id"]
            )

        for experiment_id, samples in samples_per_experiment.items():
            response = requests.get(
                f"{self.API_URL}{self.API_ENDPOINTS['experiment_status']}{experiment_id}"
            )
            if response.status_code != 200:
                print(f"Error getting experiment status: {response.text}")
                continue
            resp_json = response.json()
            if resp_json["status"] == "COMPLETED":
                for sample_id in samples:
                    self._digest_sample_for_alabdata(sample_id)
                    self._sampleview.set_status(sample_id, SampleStatus.COMPLETE)

    def _digest_sample_for_alabdata(self, sample_id: ObjectId):
        """Digest a sample for alabdata.

        Args:
            sample_id (ObjectId): sample to digest
        """
        # TODO
        return
