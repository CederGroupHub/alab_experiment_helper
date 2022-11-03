import time
from urllib import request
from .view import QueueView
from .batching import (
    experiment_to_digraph,
    get_subgraphs,
    subgraph_from_node,
    merge_nodes,
)
from typing import List
import networkx as nx


class QueueWorker:
    MAX_WAIT_TIME_SECONDS = 60 * 30  # 30 minutes

    def __init__(self, api_url = "localhost", api_port = 8896):
        self.queue = QueueView()
        self.API_URL = f"{api_url}:{api_port}"

    def _process_experiments(self):
        pending = self.queue.get_pending_experiments()
        pending_graphs = [experiment_to_digraph(e) for e in pending]
        batched_graphs = self._batch_graphs(pending_graphs)
        for bg in batched_graphs:
            if (self.get_graph_age(bg) >= self.MAX_WAIT_TIME_SECONDS) or (self.is_graph_saturated(bg)):
                experiment = digraph_to_experiment(bg) #TODO
                self._start_experiment(experiment)

    def get_graph_age(self, graph: nx.DiGraph) -> float:
        """Get the age (seconds) of the oldest node in the graph.

        Args:
            graph (nx.DiGraph): graph to get age of

        Returns:
            float: age (seconds) of the oldest node in the graph
        """
        return time.time() - min([node["submitted_at"] for _, node in graph.nodes(data=True)])

    def is_graph_saturated(self, graph: nx.DiGraph) -> bool:
        """Check if all nodes within the graph are at maximum capacity (ie number of samples == capacity).

        Args:
            graph (nx.DiGraph): graph to check

        Returns:
            bool: True if all nodes are saturated, False otherwise
        """
        for _, node in graph.nodes(data=True):
            if len(node["samples"]) < node["capacity"]:
                return False
        return True

    def _start_experiment(self, experiment):
        try:
            self._send_experiment_to_management(experiment)
        except Exception as e:
            print(f"Error sending experiment to alab_management: {e}")
        else:
            self.queue.remove_experiment(experiment) #remove from the queue. #TODO get original experiment ID's prior to batching

    def _send_experiment_to_management(self, experiment):
        response = request.post(f"{self.API_URL}/api/experiment/submit", json=experiment.to_dict())
        if response.status_code != 200:
            raise Exception(f"Failed to send experiment to management. Response: {response.text}")
        
    def _batch_graphs(self, graphs: List[nx.DiGraph]) -> List[nx.DiGraph]:
        """Batch graphs to optimally use available task capacity. Existing graphs (i.e. an experiment submitted by the user) will never be broken up.

        Args:
            graphs (List[nx.Digraph]): list of graphs to batch

        Returns:
            List[nx.DiGraph]: list of graphs after batching. This is hopefully shorter than the input list.
        """

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

        #TODO for now, dispenses will be condensed randomly. We may want to put similar powder dispenses together to consolidate errors from powder handling (ie a jammed powder dosing head) to fewer workflows. clustering/ranking by Jaccard similarity of required powder sets should work.
        for subgraph in get_subgraphs(total_graph):
            merge_nodes(subgraph, "Dispensing", parent_graph=total_graph)
        merge_nodes(total_graph, "Dispensing")

        return get_subgraphs(total_graph)

    