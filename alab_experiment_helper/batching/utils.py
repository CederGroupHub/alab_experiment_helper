from typing import Any, Callable, List, Dict
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from alab_experiment_helper.batch import Batch
import datetime

### graph manipulation functions
def experiment_to_digraph(batch: Batch) -> nx.DiGraph:
    exp_dict = batch.to_dict()  # generate task order
    g = nx.DiGraph()

    for task in exp_dict["tasks"]:
        g.add_node(
            task["_id"],
            type=task["type"],
            parameters=task["parameters"],
            capacity=task["capacity"],
            samples=task["samples"],
            parameters_per_sample={s: task["parameters"] for s in task["samples"]},
        )
        for prev_task_id in task["prev_tasks"]:
            # prev_task_id = exp_dict["tasks"][prev_task_index]["_id"]
            g.add_edge(prev_task_id, task["_id"])
    return g


def get_subgraphs(graph: nx.DiGraph) -> List[nx.DiGraph]:
    """Return subgraphs of a DiGraph. A subgraph is a set of connected nodes that are not connected to any other nodes in the graph.

    Args:
        graph (nx.DiGraph): directed graph of an experiment

    Returns:
        List[nx.Digraph]: list of subgraphs of the directed graph.
    """
    subgraphs = [
        graph.subgraph(c) for c in nx.connected_components(graph.to_undirected())
    ]
    return subgraphs


def subgraph_from_node(graph: nx.DiGraph, node_id: Any) -> nx.DiGraph:
    """Returns a subgraph containing the node with node_id.

    Args:
        graph (nx.DiGraph): directed graph of an experiment
        node_id (Any): id of the node whose subgraph to extract

    Returns:
        nx.DiGraph: subgraph of graph containing node_id
    """
    subgraph_nodes = set([node_id])
    subgraph_nodes.update(nx.descendants(graph, node_id))
    subgraph_nodes.update(nx.ancestors(graph, node_id))

    return nx.subgraph(graph, subgraph_nodes)


def plot_task_graph(graph, pos_function=None, ax=None):
    if ax is None:
        fig, ax = plt.subplots()
    color_key = {}
    node_colors = []
    for node_id, node in graph.nodes(data=True):
        if node["type"] not in color_key:
            color_key[node["type"]] = plt.cm.tab10(len(color_key))
        node_colors.append(color_key[node["type"]])

    if pos_function is None:
        try:
            pos = nx.nx_agraph.graphviz_layout(graph, prog="dot")
        except:
            pos = nx.spring_layout(graph)
    else:
        pos = pos_function(graph)
    nx.draw(
        graph,
        pos=pos,
        with_labels=False,
        labels={n: nd["type"] for n, nd in graph.nodes(data=True)},
        node_color=node_colors,
        node_size=50,
        ax=ax,
    )

    legend_elements = [
        Line2D([0], [0], marker="o", color=c, label=l, linestyle="")
        for l, c in color_key.items()
    ]
    plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc="upper left")


def sampledict_to_graph(sampledict: Dict) -> nx.DiGraph:
    graph = nx.DiGraph()  #
    for task in sampledict["tasks"]:
        graph.add_node(
            task["_id"],
            type=task["type"],
            capacity=task["capacity"],
            samples=[sampledict["_id"]],
            parameters=task["parameters"],
            parameters_per_sample={sampledict["_id"]: task["parameters"]},
        )
    for task0, task1 in zip(sampledict["tasks"], sampledict["tasks"][1:]):
        graph.add_edge(task0["_id"], task1["_id"])
    return graph


def samples_in_graph(graph: nx.DiGraph) -> List:
    """Returns a list of all samples in the graph.

    Args:
        graph (nx.DiGraph): graph to check

    Returns:
        List: list of all samples in the graph
    """
    samples = set()
    for _, node in graph.nodes(data=True):
        samples.update(node["samples"])
    return list(samples)


def is_graph_saturated(graph: nx.DiGraph) -> bool:
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


### Batching functions
def merge_nodes(
    graph: nx.DiGraph,
    node_type: str,
    parent_graph: nx.DiGraph = None,
    merge_allowed_fn: Callable = None,
    similarity_fn: Callable = None,
) -> nx.DiGraph:
    """_summary_

    Args:
        graph (nx.DiGraph): experimental graph (or subgraph) to merge nodes in
        node_type (str): type (ie Task type) of nodes to merge
        parent_graph (nx.DiGraph, optional): Parent graph to merge. This is required if merging subgraphs, as subgraphs cannot be edited (simply point to nodes within a parent graph). Edits based on subgraphs will be made to the parent graph. Defaults to None, which implies graph == parent_graph.
        merge_allowed_fn (Callable, optional): Function evaluated to decide whether two nodes can be merged. Should return a boolean. For example, merging nodes for heating in a furnace should check if the furnace profiles required of the two nodes are identical. Defaults to None, implies that any nodes with node_type can be merged if capacity allows.
        similarity_fn (Callable, optional): Function evaluated to decide how similar two nodes are (Higher = more similar). We will sort nodes by similarity to prioritize merges between similar nodes. Defaults to None, implies that nodes are equally similar. #TODO: implement this
    Returns:
        nx.DiGraph: graph with nodes merged. Note that changes to parent_graph are made in place.
    """

    if parent_graph is None:
        parent_graph = graph
    node_ids = list(graph.nodes)
    removed_nodes = []
    for reference_node_id in node_ids:
        if reference_node_id in removed_nodes:
            continue
        # reference_node_id = node_ids[reference_index]
        try:
            ref = graph.nodes[reference_node_id]
        except:
            break  # we merged nodes, so ran out of entries early. This is fine, just end the loop.
        replace = []
        capacity = ref["capacity"]
        ref_samples = ref["samples"]
        ref_params_per_sample = ref["parameters_per_sample"]

        for tid, task in graph.nodes(data=True):
            if tid == reference_node_id:
                continue
            if task["type"] != ref["type"]:
                continue
            if task["type"] != node_type:
                continue
            if len(task["samples"]) + len(ref_samples) > capacity:
                continue
            if merge_allowed_fn is not None:
                if not merge_allowed_fn(ref, task):
                    continue

            replace.append(tid)
            ref_samples.extend(task["samples"])
            ref_params_per_sample.update(task["parameters_per_sample"])

            if len(ref_samples) == capacity:
                break

        if len(replace) == 0:
            continue

        for replace_id in replace:
            for prev in parent_graph.predecessors(replace_id):
                parent_graph.add_edge(prev, reference_node_id)
            for next in parent_graph.successors(replace_id):
                parent_graph.add_edge(reference_node_id, next)
            parent_graph.remove_node(replace_id)
            removed_nodes.append(replace_id)
        parent_graph.nodes[reference_node_id]["samples"] = ref_samples
        parent_graph.nodes[reference_node_id][
            "parameters_per_sample"
        ] = ref_params_per_sample
    return graph
