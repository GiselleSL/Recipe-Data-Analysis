# * ----------------------------- NECESARY IMPORTS ----------------------------- #
import json
from collections import Counter

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# * ----------------------------- CLASS DATALOADER ----------------------------- #
class DataLoader:
    """Clase genérica para procesar información de un archivo csv o json."""

    def __init__(self, file_path, file_type="json"):
        self._file_path = file_path
        self._file_type = file_type

    def load_data(self):
        if self._file_type == "json":
            with open(self._file_path, "r") as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        elif self._file_type == "csv":
            df = pd.read_csv(self._file_path)
        else:
            raise ValueError(f"Unsupported file type: {self._file_type}")

        return df


# ------------------------------------- + ------------------------------------ #
def detect_uncommon_ingredients(dataloader, threshold=5):
    """
    Function that detects uncommon ingredients in a dataloader that has recipes and ingredients in columns.

    Args:
    - dataloader: object that contains the recipe and ingredient data. Must be a pandas.DataFrame with at least
    two columns: one for the recipes and one for the ingredients.
    - threshold: minimum number of times an ingredient must appear in the dataloader to be considered common.
    Default is 5.

    Returns:
    - list of uncommon ingredients.
    """
    # Get the ingredients from all recipes
    ingredients = (
        dataloader["Ingredient_Name"].str.split(",").explode().str.strip().tolist()
    )

    # Count the frequency of each ingredient
    frequency = Counter(ingredients)

    # Filter the uncommon ingredients
    uncommon = [
        ingredient for ingredient, count in frequency.items() if count < threshold
    ]

    return uncommon


# ------------------------------------- + ------------------------------------ #


def filter_uncommon_ingredients(dataloader, uncommon_ingredients):
    """
    Function that filters the dataloader to only include the recipes that contain uncommon ingredients.

    Args:
    - dataloader: object that contains the recipe and ingredient data. Must be a pandas.DataFrame with at least
    two columns: one for the recipes and one for the ingredients.
    - uncommon_ingredients: list of uncommon ingredients to filter the dataloader by.

    Returns:
    - filtered dataloader containing only the recipes that contain uncommon ingredients.
    """
    # Convert the list of uncommon ingredients to a set for faster lookup
    uncommon_set = set(uncommon_ingredients)
    # Filter the dataloader to only include the recipes that contain uncommon ingredients

    filtered_dataloader = dataloader[
        dataloader["Ingredient_Name"]
        .astype(str)
        .apply(
            lambda x: any(item for item in uncommon_set if item.lower() in x.lower())
        )
    ]

    return filtered_dataloader


def filter_recipes_by_ingredients(dataloader, uncommon_ingredients, colum):
    """
    Function that filters the dataloader to exclude the recipes that contain certain ingredients.

    Args:
    - dataloader: object that contains the recipe and ingredient data. Must be a pandas.DataFrame with at least
    two columns: one for the recipes and one for the ingredients.
    - uncommon_ingredients: list of uncommon ingredients to filter the dataloader by.

    Returns:
    - filtered dataloader containing only the recipes that do not contain the specified ingredients.
    """
    # Convert the list of uncommon ingredients to a set for faster lookup
    uncommon_set = set(uncommon_ingredients)
    # Filter the dataloader to exclude the recipes that contain uncommon ingredients
    filtered_dataloader = dataloader[
        ~dataloader[colum]
        .astype(str)
        .apply(
            lambda x: any(item for item in uncommon_set if item.lower() in x.lower())
        )
    ]

    return filtered_dataloader


def jaccard_similarity(set1, set2):
    """
    Función que calcula la similitud de Jaccard entre dos conjuntos
    :param set1: Primer conjunto
    :param set2: Segundo conjunto
    :return: Valor de similitud de Jaccard entre los dos conjuntos
    """
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union


def find_similar_recipes(df, threshold=0.5):
    """
    Función que encuentra recetas similares dentro de un DataFrame utilizando el índice de Jaccard
    :param df: DataFrame de pandas con las recetas y los ingredientes
    :param threshold: Umbral de similitud para determinar cuándo dos recetas son similares
    :return: Dictionary con las recetas similares y el número de ingredientes compartidos
    """
    # Convierte los ingredientes de las recetas en conjuntos
    df["Ingredient_Set"] = df["Ingredient_Name"].apply(set)

    # Crea un diccionario vacío para almacenar las recetas similares
    similar_recipes_dict = {}

    # Itera sobre todas las combinaciones posibles de recetas y calcula la similitud de Jaccard entre ellas
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            set1 = df.loc[i, "Ingredient_Set"]
            set2 = df.loc[j, "Ingredient_Set"]
            sim = jaccard_similarity(set1, set2)
            if sim >= threshold:
                recipe1 = df.loc[i, "Title"]
                recipe2 = df.loc[j, "Title"]
                num_shared_ingredients = len(set1 & set2)
                if recipe1 not in similar_recipes_dict:
                    similar_recipes_dict[recipe1] = {}
                similar_recipes_dict[recipe1][recipe2] = num_shared_ingredients
                if recipe2 not in similar_recipes_dict:
                    similar_recipes_dict[recipe2] = {}
                similar_recipes_dict[recipe2][recipe1] = num_shared_ingredients

    # Devuelve el diccionario con las recetas similares
    return similar_recipes_dict


def detect_common_and_popular_ingredients(df):
    # Crea un diccionario para contar el número de veces que aparece cada ingrediente en cada región
    region_ingredients_count = {}
    for region in df["Cuisine"].unique():
        region_ingredients_count[region] = Counter(
            ingredient
            for ingredients in df.loc[df["Cuisine"] == region, "Ingredient_Name"]
            for ingredient in ingredients
        )

    # Encuentra los ingredientes más populares en cada región
    region_popular_ingredients = {}
    for region, count in region_ingredients_count.items():
        region_popular_ingredients[region] = [
            ingredient for ingredient, ingredient_count in count.most_common(10)
        ]

    # Encuentra los ingredientes que más se repiten en común entre las regiones
    common_ingredients = set.intersection(
        *[set(count.keys()) for count in region_ingredients_count.values()]
    )
    common_ingredients_count = Counter(
        ingredient
        for ingredient in df["Ingredient_Name"]
        if ingredient in common_ingredients
    )
    most_common_ingredients = [
        ingredient
        for ingredient, ingredient_count in common_ingredients_count.most_common(10)
    ]

    return region_popular_ingredients, most_common_ingredients


def detect_common_ingredients(df):
    # Convierte la columna de ingredientes en una lista de conjuntos
    df["Ingredient_Name"] = df["Ingredient_Name"].apply(set)

    # Calcula la matriz de similitud de Jaccard para todas las recetas
    jaccard_matrix = pd.DataFrame(index=df.index, columns=df.index)
    for i in range(len(df)):
        for j in range(len(df)):
            # Calcula la intersección y unión de los ingredientes de las dos recetas
            intersection = len(df.iloc[i]["In"] & df.iloc[j]["Ingredient_Name"])
            union = len(df.iloc[i]["Ingredient_Name"] | df.iloc[j]["Ingredient_Name"])

            # Calcula la similitud de Jaccard
            if union > 0:
                jaccard_similarity = intersection / union
            else:
                jaccard_similarity = 0

            # Guarda la similitud en la matriz de similitud
            jaccard_matrix.iloc[i, j] = jaccard_similarity

    # Filtra las recetas que tienen al menos dos ingredientes en común
    common_recipes = set()
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            if jaccard_matrix.iloc[i, j] >= 0.5:
                common_recipes.add(i)
                common_recipes.add(j)

    return df.loc[list(common_recipes)]
