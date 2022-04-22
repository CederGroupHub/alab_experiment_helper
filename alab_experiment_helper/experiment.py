from pathlib import Path
from typing import List, Dict, Any, Literal

from .sample import Sample


class Experiment:
    def __init__(self, name: str):
        self.name = name
        self._samples: List[Sample] = []
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def add_sample(self, name: str) -> Sample:
        sample = Sample(name, experiment=self)
        self._samples.append(sample)
        return sample

    def add_task(self, task_id: str, task_name: str,
                 task_params: Dict[str, Any], samples: List[Sample]) -> None:
        if task_id in self._tasks:
            return
        self._tasks[task_id] = {
            "type": task_name,
            "parameters": task_params,
            "samples": [sample.name for sample in samples]
        }

    def to_dict(self):
        samples = []
        tasks = []
        task_ids = {}

        for sample in self._samples:
            samples.append(sample.to_dict())
            last_task_id = None
            for task_id in sample.tasks:
                task = self._tasks[task_id]
                if task_id not in task_ids:
                    task_ids[task_id] = len(tasks)
                    task["next_tasks"] = set()
                    tasks.append(task)
                if last_task_id is not None:
                    tasks[task_ids[last_task_id]]["next_tasks"].add(task_ids[task_id])

                last_task_id = task_id

        for task in tasks:
            task["next_tasks"] = list(task["next_tasks"])

        return {
            "name": self.name,
            "samples": samples,
            "tasks": tasks,
        }

    def generate_input_file(self, filename: str, fmt: Literal["json", "yaml"] = "json") -> None:
        with Path(filename).open("w", encoding="utf-8") as f:
            if fmt == "json":
                import json

                json.dump(self.to_dict(), f, indent=2)
            elif fmt == "yaml":
                import yaml

                yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)

    def visualize(self, path: str, fmt: Literal["png", "jpg", "pdf", "svg"] = "png") -> None:
        import graphviz

        tasks = self.to_dict()["tasks"]
        graph = graphviz.Digraph(name=self.name, format=fmt)
        for i, task in enumerate(tasks):
            graph.node(str(i), task["type"])
            for next_task in task["next_tasks"]:
                graph.edge(str(i), str(next_task))
        graph.render(filename="figures", directory=path, view=True)
