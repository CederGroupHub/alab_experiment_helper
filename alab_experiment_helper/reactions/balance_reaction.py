from functools import lru_cache
from typing import List, Optional

from material_parser import MaterialParser
from reaction_completer import balance_recipe
from reaction_completer.periodic_table import PT

from alab_experiment_helper.reactions.recipe import Recipe

mp = MaterialParser()


class ParserError(Exception):
    pass


class BalanceError(Exception):
    pass


@lru_cache(maxsize=128)
def generate_recipe(
        target: str,
        precursor_list: List[str],
        target_mass_g: Optional[float] = None,
        target_mol: Optional[float] = None,
) -> Recipe:
    """
    Generate a recipe for the target material.

    Args:
        target: the target material
        precursor_list: the list of precursor materials
        target_mass_g: the target mass in g
        target_mol: the target mol amount

    Returns:
        the recipe for the target material
    """
    target = parse_material_string(target)
    precursors = [parse_material_string(precursor) for precursor in precursor_list]

    if target_mass_g is not None and target_mol is not None:
        raise ValueError("Cannot specify both target mass and target mol")
    elif target_mass_g is not None:
        target_mol = target_mass_g / target["molmass"]
    elif target_mol is not None:
        pass
    else:
        raise ValueError("No target mol amount or mass was given!")

    balanced_reaction = balance_recipe(precursors, [target])
    if not balanced_reaction:
        raise BalanceError("Could not balance reaction")
    balanced_reaction = balanced_reaction[0][1]
    recipe = Recipe.build_recipe(balanced_reaction, precursors, target)
    return recipe * (target_mol / recipe.target.mol)


@lru_cache(maxsize=1024)
def parse_material_string(material_string: str) -> dict:
    material_dict = mp.parse_material_string(material_string)
    if not material_dict["material_formula"] or all(len(comp["elements"]) == 0 for comp in material_dict["composition"]):
        raise ParserError(f"Could not parse material string {material_string}")

    molmass = calculate_molmass(material_dict)
    material_dict["molmass"] = molmass
    return material_dict


def calculate_molmass(material_dict: dict) -> float:
    """
    Calculate the molecular mass of a material.

    Args:
        material_dict: the material to calculate the molecular mass

    Returns:
        the molecular mass of the material
    """
    molmass = 0
    for comp in material_dict["composition"]:
        comp_amount = float(comp["amount"])
        for element, amount in comp["elements"].items():
            molmass += float(PT[element]["atomicMass"].split("(")[0]) * float(amount) * comp_amount
    return molmass


if __name__ == '__main__':
    print(generate_recipe(
        "Na1.25Zr0.5Ge0.5Mg0.5Nb0.5(PO4)3",
        ["sodium oxide", "NH4H2PO4", "ZrO2", "SiO2", "GeO2", "In2O3", "MgO", "Nb2O5"],
        target_mass_g=4)
    )
