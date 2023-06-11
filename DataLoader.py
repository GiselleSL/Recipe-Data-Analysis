import csv
import json
from dataclasses import asdict, dataclass
from typing import List

""" 
This Python code provides a set of classes and functions for working with recipes and ingredients 
It includes a DataLoader class for loading data from CSV or JSON files and creating a list of objects of a specified class. 
The Recipe class represents a recipe, while the Ingredient class represents an ingredient with various properties.
The Recipe_with_Ingredients subclass of Recipe includes a list of Ingredient objects as an additional attribute.

The ingredientsList function can be used to filter a list of Ingredient objects by recipe ID, 
The merge_ingredients function merges duplicate Ingredient objects with the same entity ID. 

This code is designed to help obtain and organize recipe and ingredient data, 
making it easier to work with in other parts of a larger program.
"""


# * ----------------------------- CLASS DATALOADER ----------------------------- #
class DataLoader:
    """Clase generica para procesar la informacion ya sea de un csv o un json"""

    def __init__(self, file_path, entity_class, file_type="json", entity_fields=None):
        self._file_path = file_path
        self._entity_class = entity_class
        self._file_type = file_type
        self._entity_fields = entity_fields if entity_fields is not None else []

    def map_entity_fields(self, entity_data):
        entity_args = {}
        for field, key in self._entity_fields:
            entity_args[field] = entity_data[key]
        return entity_args

    def load_entities(self):
        with open(self._file_path, "r") as f:
            if self._file_type == "json":
                data = json.load(f)
                entities = [
                    self._entity_class(**self.map_entity_fields(item)) for item in data
                ]
            elif self.file_type == "csv":  # TODO: falta probar cargando un csv
                reader = csv.DictReader(f)
                data = [dict(row) for row in reader]
                entities = [
                    self._entity_class(**self.map_entity_fields(item)) for item in data
                ]
            else:
                raise ValueError(f"Unsupported file type: {self._file_type}")
        # self.entities = entities
        return entities


# * ------------------------------- CLASS RECIPE ------------------------------- #
@dataclass  # decorador Python genera automáticamente los métodos __init__, __repr__, y __eq__
class Recipe:
    """Class for representing a recipe"""

    recipe_id: str = None
    title: str = None
    source: str = None
    cuisine: str = None

    def __str__(self):
        # for attr in [
        #     "recipe_id",
        #     "title",
        #     "source",
        #     "cousine",
        # ]:
        #     val1 = getattr(self, attr)
        #     if val1 is not None and val1 != "":
        return f"{self.recipe_id} : {self.title} ({self.cuisine}) from {self.source}"

    def add_ingredients(self, ingredients_list):
        self.ingredients_list = ingredients_list


# * ----------------------------- CLASS INGREDIENT ----------------------------- #
@dataclass
class Ingredient:
    """Class for representing a Ingredient"""

    entity_id: str = None
    aliased_name: str = None
    aliased_name2: str = None
    recipe_id: int = None
    original_name: str = None
    synonyms: List[str] = None
    category: str = None
    compaund_name: str = None
    synonyms_compaund: List[str] = None
    contituent: List[str] = None
    compaund_category: str = None


# * ---- Funtion for creating a list of ingredients with the same Recipe ID ---- #
def ingredientsList(ingredient, recipe_id):
    """Filter a list of Ingredient objects to include only those with a matching recipe_id.

    Args:
        ingredient (List[Ingredient]): A list of Ingredient objects to filter.
        recipe_id (str): The recipe_id to match.

    Returns:
        List[Ingredient]: A new list containing only the Ingredient objects with the
            specified recipe_id.
    """
    ing = []
    ingredients_list = []
    for ing in ingredient:
        if ing.recipe_id == recipe_id:
            ingredients_list.append(ing)
    return ingredients_list


# * ----------------- Function to merge two Ingredient objects ----------------- #
def merge_ingredients(ingredient1, ingredient2):
    """Merge two Ingredient objects with the same entity_id into a single object.

    Args:
        ingredient1 (Ingredient): The first Ingredient object to merge
        ingredient2 (Ingredient): The second Ingredient objet to merge

    Returns:
        Ingredient: A new Ingredient object with the common attributes of the input objects.
            If the input objects have different values for an attribute, the value from
            ingredient2 takes precedence.
    """
    if ingredient1.entity_id == ingredient2.entity_id:
        new_ingredient = Ingredient(entity_id=ingredient1.entity_id)

        for attr in [
            "recipe_id",
            "original_name",
            "aliased_name",
            "aliased_name2",
            "synonyms",
            "category",
            "compaund_name",
            "synonyms_compaund",
            "contituent",
            "compaund_category",
        ]:
            val1 = getattr(ingredient1, attr)
            val2 = getattr(ingredient2, attr)
            if val2 is not None and val2 != "":
                setattr(new_ingredient, attr, val2)
            else:
                setattr(new_ingredient, attr, val1)

    else:
        print("The ingredients do not have the same entity_id")
    return new_ingredient


def merge_ingredient_lists(ingredients1, ingredients2):
    merged_ingredients = []
    for ingredient1 in ingredients1:
        found_match = False
        for ingredient2 in ingredients2:
            if ingredient1.entity_id == ingredient2.entity_id:
                merged_ingredients.append(merge_ingredients(ingredient1, ingredient2))
                found_match = True
                break
        if not found_match:
            merged_ingredients.append(ingredient1)
    for ingredient2 in ingredients2:
        found_match = False
        for ingredient1 in ingredients1:
            if ingredient1.entity_id == ingredient2.entity_id:
                found_match = True
                break
        if not found_match:
            merged_ingredients.append(ingredient2)
    return merged_ingredients


# #* ------------------------- TESTING THE FUNTIONALITY ------------------------- #
recipe_1 = DataLoader(
    file_path="database/01_Recipe_Details.json",
    entity_class=Recipe,
    file_type="json",
    entity_fields=[
        ("recipe_id", "Recipe ID"),
        ("title", "Title"),
        ("source", "Source"),
        ("cuisine", "Cuisine"),
    ],
)

ingredient_1 = DataLoader(
    file_path="database/02_Ingredients.json",
    entity_class=Ingredient,
    file_type="json",
    entity_fields=[
        ("entity_id", "Entity ID"),
    ],
)

ingredient_2 = DataLoader(
    file_path="database/03_Compound_Ingredients.json",
    entity_class=Ingredient,
    file_type="json",
    entity_fields=[
        ("compaund_name", "Compound Ingredient Name"),
        ("synonyms_compaund", "Compound Ingredient Synonyms"),
        ("entity_id", "entity_id"),
        ("contituent", "Contituent Ingredients"),
        ("compaund_category", "Category"),
    ],
)

ingredient_3 = DataLoader(
    file_path="database/04_Recipe-Ingredients_Aliases.json",
    entity_class=Ingredient,
    file_type="json",
    entity_fields=[
        ("entity_id", "Entity ID"),
        ("recipe_id", "Recipe ID"),
        ("original_name", "Original Ingredient Name"),
        ("aliased_name2", "Aliased Ingredient Name"),
    ],
)


# list_ingredient_1 = ingredient_1.entities[0]
# print (list_ingredient_1.data["recipe_id"])

# list_ingredient_1 = ingredient_1.entities[2]
# print(list_ingredient_1.data)
# print(list_ingredient_1.data["entity_id"])

# list_recipe_1 = recipe_1.entities[2]
# print(list_recipe_1.data)

# print("Ingredientes1 [287]:", ingredient_1.entities[287])
# print("Ingredientes3 [2]:", ingredient_3.entities[2])

# merge_ingredint_291 = merge_ingredients(
#     ingredient_1.entities[287], ingredient_3.entities[2]
# )
# print(merge_ingredint_291)

# merge = merge_ingredient_lists(ingredient_1.entities, ingredient_3.entities)
# print("Merged Ingrediets:", merge[287])

ingrediente1 = recipe_1.load_entities()
print(ingrediente1[1])
