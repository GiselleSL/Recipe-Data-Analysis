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

    def __init__(
        self, file_path, file_type="json", entity_class=None, entity_fields=None
    ):
        self._file_path = file_path
        self._file_type = file_type
        self._entity_class = entity_class
        self._entity_fields = entity_fields

    def map_entity_fields(self, entity_data):
        entity_args = {}
        for field, key in self._entity_fields:
            entity_args[field] = entity_data[key]
        return entity_args

    def load_entities_by_class(self):
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

    def load_entities(self):
        with open(self._file_path, "r") as f:
            if self._file_type == "json":
                data = json.load(f)
                if self._entity_fields is None:
                    return data
                entities = [
                    dict((k, item[k]) for k in self._entity_fields) for item in data
                ]
            elif self._file_type == "csv":
                reader = csv.DictReader(f)
                data = [dict(row) for row in reader]
                if self._entity_fields is None:
                    return data
                entities = [
                    dict((k, item[k]) for k in self._entity_fields) for item in data
                ]
            else:
                raise ValueError(f"Unsupported file type: {self._file_type}")
        return entities


# * ------------------------------- CLASS RECIPE ------------------------------- #
@dataclass  # decorador Python genera automáticamente los métodos __init__, __repr__, y __eq__
class Recipe:
    """Class for representing a recipe"""

    recipe_id: str = None
    title: str = None
    source: str = None
    cuisine: str = None
    ingredients: List[str] = None

    def __str__(self):
        return f"{self.recipe_id} : {self.title} ({self.cuisine}) from {self.source}"

    def add_ingredients(self, ingredients_list):
        self.ingredients_list = ingredients_list

    # def find_recipe_per_ingredient(self, ingredient_id):
    #     return [
    #         recipe
    #         for recipe in [self]
    #         if any(
    #             ingredient.entity_id == ingredient_id for ingredient in self.ingredients
    #         )
    #     ]

    def match_recipe_with_ingredients(self, relation_recipe_ingredient):
        """
        integra a la clase una lista con el id de los ingredientes que la componen
        """
        ingredients_by_recipe = []
        for relation in relation_recipe_ingredient:
            recipe_id_in_relation = relation["Recipe ID"]
            if self.recipe_id == recipe_id_in_relation:
                ingredients_by_recipe.append(relation["Entity ID"])

        self.ingredients = ingredients_by_recipe


# * ----------------------------- CLASS INGREDIENT ----------------------------- #
@dataclass
class Ingredient:
    """Class for representing a Ingredient"""

    entity_id: str = None
    original_name: str = (
        None  # 04 - informacion referente al nombre y la cantidad del ingrediente
    )
    aliased_name: str = None
    synonyms: List[str] = None
    category: str = None

    def __str__(self):
        return f"{self.entity_id} : {self.aliased_name} ({self.synonyms}) Category: {self.category}"


# * ------------------------- CLASS COMPOUND INGREDIENT ------------------------ #
@dataclass
class CompoundIngredient(Ingredient):
    contituent: List[str] = None


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

#* --- Function for matching a list of ingredients to a corresponding recipe -- #
def match_recipelist_with_ingredientslis(relation, recipe):
    
    # Crea un diccionario para almacenar los recipe_id con el mismo entity_id
    recipe_por_entity = {}

    # Itera sobre los datos y agrega cada recipe_id al diccionario correspondiente en recipe_por_entity
    for info in relation:
        recipe_id = info["Recipe ID"]
        entity_id = info["Entity ID"]
        if recipe_id not in recipe_por_entity:
            recipe_por_entity[recipe_id] = [entity_id]
        else:
            recipe_por_entity[recipe_id].append(entity_id)

    for rec in recipe:
        if rec.recipe_id in recipe_por_entity:
            rec.ingredients = recipe_por_entity[rec.recipe_id]


# * ------------------------- TESTING THE FUNTIONALITY ------------------------- #
recipe_dl = DataLoader(
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

ingredient_dl = DataLoader(
    file_path="database/02_Ingredients.json",
    entity_class=Ingredient,
    file_type="json",
    entity_fields=[
        ("entity_id", "Entity ID"),
        ("category", "Category"),
        ("synonyms", "Ingredient Synonyms"),
        ("aliased_name", "Aliased Ingredient Name"),
    ],
)

compound_ingredient_dl = DataLoader(
    file_path="database/03_Compound_Ingredients.json",
    entity_class=CompoundIngredient,
    file_type="json",
    entity_fields=[
        ("aliased_name", "Compound Ingredient Name"),
        ("synonyms", "Compound Ingredient Synonyms"),
        ("entity_id", "entity_id"),
        ("contituent", "Contituent Ingredients"),
        ("category", "Category"),
    ],
)

relation_rec_ing_dl = DataLoader(
    file_path="database/04_Recipe-Ingredients_Aliases.json",
    entity_class=None,
    file_type="json",
)

recipe = recipe_dl.load_entities_by_class()
print("Recipe 1: ", recipe[1].recipe_id)
ingredient = ingredient_dl.load_entities_by_class()
print("Ingredient 1: ", ingredient[1].entity_id)
compound_ingredient = compound_ingredient_dl.load_entities_by_class()
print("Compound Ingredient: ", compound_ingredient[1].entity_id)
relation = relation_rec_ing_dl.load_entities()
print("relation: ", relation[1])


recipe[1].match_recipe_with_ingredients(relation)
print("RECIPE 1: ", recipe[1])
print(recipe[1].ingredients)

# list_of_ing = ingredientsList(ingredient3, 1)
# print (list_of_ing)
# all_ingredients = merge_ingredient_list(ingredient2, all_ingredients)
# print(all_ingredients[3])

# # list_ingredient_1 = ingredient_1.entities[0]
# # print (list_ingredient_1.data["recipe_id"])

# # list_ingredient_1 = ingredient_1.entities[2]
# # print(list_ingredient_1.data)
# # print(list_ingredient_1.data["entity_id"])

# # list_recipe_1 = recipe_1.entities[2]
# # print(list_recipe_1.data)

# # print("Ingredientes1 [287]:", ingredient_1.entities[287])
# # print("Ingredientes3 [2]:", ingredient_3.entities[2])

# # merge_ingredint_291 = merge_ingredients(
# #     ingredient_1.entities[287], ingredient_3.entities[2]
# # )
# # print(merge_ingredint_291)

# # merge = merge_ingredient_lists(ingredient_1.entities, ingredient_3.entities)
# # print("Merged Ingrediets:", merge[287])

# ingrediente1 = recipe_1.load_entities()
# print(ingrediente1[1])
