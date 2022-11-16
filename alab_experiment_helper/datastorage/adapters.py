from alab_management.experiment_view import ExperimentView

from alab_data import Sample, Actor, Action, Measurement, Material, views, WholeIngredient, Ingredient
from alab_data.data.nodes import BaseObject

import json
from bson import ObjectId

experiment_view = ExperimentView() #TODO config filepath
sv_data = views.SampleView()

def management_to_data(experiment:dict):
    """Upload the results from a completed experiment (on alab_management, ie the hardware manager) to the permanent data store (on alab_data, ie final experimental graph)

    Args:
        experiment (dict): 
    """
    raise NotImplementedError("Still a WIP!") #TODO
    sample_objects = dict()
    for entry in experiment["samples"]:
        new_sample_entry = Sample(
            name=entry["name"]
        )
        new_sample_entry._id = ObjectId(entry["sample_id"])
        sample_objects[entry["name"]] = new_sample_entry


    node_dict = dict()

    measurement_types = ["Diffraction"]
    batch_types = ["Heating", "HeatingWithAtmosphere"]

    for sample, sampleobj in sample_objects.items():
        sampleobj: Sample
        current_material = None
        for entry in experiment["tasks"]:
            if sample not in entry["samples"]:
                continue
            if entry["task_id"] in node_dict: #implies this is a batched task
                newnode:Action = node_dict.get(entry["task_id"])
                
                newnode.add_ingredient(WholeIngredient(current_material))
                current_material = Material(
                    name = f"{current_material.name} - {entry['type']}"
                )
                newnode.add_generated_material(current_material)

            else:
                if entry["type"] in measurement_types:
                    newnode = Measurement(
                        name=entry["type"],
                        material = current_material,
                        actor=tubeactor, #TODO get this from the task results
                    )
                else:
                    if current_material:
                        ing = [WholeIngredient(current_material)]
                    else:
                        ing = []
                    newnode = Action(
                        name=entry["type"],
                        ingredients = ing,
                        actor=tubeactor, #TODO get this from task results
                    )
                    current_material = newnode.make_generic_generated_material()
                node_dict[entry["task_id"]] = newnode
            sampleobj.add_node(newnode)
            if not isinstance(newnode, Measurement):
                sampleobj.add_node(current_material)
        # sv_data.add(sampleobj)

    all_incoming = [node.id for sample in sample_objects.values() for node in sample.nodes ]

    for sample in sample_objects.values():
    sv_data.add(sample, additional_incoming_node_ids=all_incoming)