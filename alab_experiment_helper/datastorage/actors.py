from alab_data import Actor
from alab_data.views import ActorView

actorview = ActorView()


def set_alab_actors():
    """Creates the ALab v1.0 actors in the alab_data permanent data store. "Actors" include any pieces/groups of hardware that perform experimental steps (synthesis or characterization)"""
    for label in ["A", "B", "C", "D"]:
        tube_furnace_actor = Actor(
            name=f"TubeFurnace_{label}",
            description="One of four automated tube furnaces in the Ceder ALab v1.0. This is in room 30-105 at Lawrence Berkeley National Lab. The furnace is a modified tube furnace from MTI. It is capable of high-temperature sintering under controlled gas environments at atmospheric pressure.",
            tags=["ceder", "alab_v1.0", "heating"],
        )
        actorview.add(tube_furnace_actor, if_already_in_db="skip")

        box_furnace_actor = Actor(
            name=f"BoxFurnace_{label}",
            description="One of four automated box furnaces in the Ceder ALab v1.0. This is in room 30-105 at Lawrence Berkeley National Lab. It is capable of high-temperature sintering in room air environment.",
            tags=["ceder", "alab_v1.0", "heating"],
        )
        actorview.add(box_furnace_actor, if_already_in_db="skip")

    verticalshaker = Actor(
        name="VerticalShaker",
        description="A modified vertical shaker in the Ceder ALab v1.0. This is used to grind powder in ceramic crucibles and plastic vials. The grinding is typically done to prepare sintered samples for characterization by diffraction and scanning electron microscopy. This shaker is in room 30-105 at Lawrence Berkeley National Lab.",
        tags=["ceder", "alab_v1.0", "grinding"],
    )
    actorview.add(verticalshaker, if_already_in_db="skip")

    diffractometer = Actor(
        name="AerisDiffractometer",
        description="An automated diffractometer (model Aeris-xxx. This is in room 30-105 at Lawrence Berkeley National Lab",
        tags=["ceder", "alab_v1.0", "characterization", "diffraction"],
    )
    actorview.add(diffractometer, if_already_in_db="skip")

    labman = Actor(
        name="LabmanPowderDoser",
        description="A system that weighs and mixes powders into crucibles. This is in room 30-105 at Lawrence Berkeley National Lab.",
        tags=["ceder", "alab_v1.0", "weighing", "mixing", "powders", "dosing"],
    )
    actorview.add(labman, if_already_in_db="skip")
