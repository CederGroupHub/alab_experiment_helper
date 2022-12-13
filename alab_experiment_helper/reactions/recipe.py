from typing import List, Dict

import pydantic
from pydantic import root_validator


class Material(pydantic.BaseModel):
    formula: str
    mol: float
    molmass: float

    @root_validator
    def analyze(cls, values) -> Dict:
        values["mass"] = values["mol"] * values["molmass"]
        return values

    def __mul__(self, other: float) -> "Material":
        if not isinstance(other, (int, float)):
            raise TypeError("Can only multiply by a number")
        elif other < 0:
            raise ValueError("Can only multiply by a positive number")
        return Material(formula=self.formula, mol=self.mol * other, molmass=self.molmass)

    def __truediv__(self, other: float) -> "Material":
        if not isinstance(other, (int, float)):
            raise TypeError("Can only divide by a number")
        elif other < 0:
            raise ValueError("Can only divide by a positive number")
        return Material(formula=self.formula, mol=self.mol / other, molmass=self.molmass)

    def __str__(self):
        return f"{self.formula} ({self.mol*1000:.3f} mmol, {self.mass:.4f} g)"

    __repr__ = __str__


class Recipe(pydantic.BaseModel):
    precursors: List[Material]
    target: Material
    balanced_reaction: Dict[str, Dict[str, float]]

    def __mul__(self, other: float) -> "Recipe":
        return Recipe(
            precursors=[precursor * other for precursor in self.precursors],
            target=self.target * other,
            balanced_reaction=self.balanced_reaction,
        )

    def __truediv__(self, other: float) -> "Recipe":
        return Recipe(
            precursors=[precursor / other for precursor in self.precursors],
            target=self.target / other,
            balanced_reaction=self.balanced_reaction,
        )

    @classmethod
    def build_recipe(
            cls,
            balanced_reaction: Dict,
            precursor_dict_list: List[Dict],
            target_dict: Dict
    ) -> "Recipe":
        target = Material(
            formula=target_dict["material_formula"],
            mol=balanced_reaction["right"][target_dict["material_formula"]],
            molmass=target_dict["molmass"],
        )
        precursors = []
        for precursor_dict in precursor_dict_list:
            if precursor_dict["material_formula"] in balanced_reaction["left"]:
                precursor = Material(
                    formula=precursor_dict["material_formula"],
                    mol=balanced_reaction["left"][precursor_dict["material_formula"]],
                    molmass=precursor_dict["molmass"],
                )
                precursors.append(precursor)

        return Recipe(precursors=precursors, target=target, balanced_reaction=balanced_reaction)
