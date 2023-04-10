import psycopg2
import psycopg2.extras

from itertools import groupby
from functools import reduce

conn = None
cursor = None


def connect():
    conn = psycopg2.connect(
        database="recipedb",
        host="recipe-db",
        user="postgres",
        password="admin",
        port="5432",
    )

    cursor = conn.cursor()

    return conn, cursor


def _process_results(results, mapper_func):
    return list(map(mapper_func, results))

def find_all(base_query, mapper_func):
    conn, cursor = connect()

    cursor.execute(base_query)

    processed = _process_results(cursor.fetchall(), mapper_func)

    conn.commit()
    conn.close()

    return processed


def find_paged(base_query, serverParams, mapper_func):
    conn, cursor = connect()

    query = base_query

    if serverParams:
        if serverParams["offset"]:
            query += f" offset {serverParams['offset']}"

        if serverParams["limit"]:
            query += f" limit {serverParams['limit']}"

    cursor.execute(query)

    processed = _process_results(cursor.fetchall(), mapper_func)

    conn.commit()
    conn.close()

    return processed


# The following should move somewhere else (a per datatype 'persistence' module?)

SQL_FIND_RECIPES = """
    select 
        recipe_data->>'title',
        recipe_data->>'description',
        recipe_data->>'author',
        recipe_data->>'image-link',
        recipe_data->>'servings',
        recipe_data->>'prep-time',
        recipe_data->>'cook-time'
    from "recipe-schema".recipes
    order by recipe_data->>'title'
"""

SQL_FIND_INGREDIENTS = """
    with ingredients as (
        select 
            id,
            (jsonb_array_elements(
                jsonb_array_elements(
                    recipe_data->'ingredient_groups'
                )->'ingredients'
            )->>'name') as ing2
        from "recipe-schema".recipes
    ) select id, jsonb_agg(ing2) as ing from ingredients
    group by id
"""

SQL_FIND_USER_INGREDIENTS = """
    select ingredient 
    from "recipe-schema".user_ingredients
    where user_id = '{0}'
"""

SQL_FIND_RECIPES_COOKABLE = """
    select
        recipe_data->>'title',
        recipe_data->>'description',
        recipe_data->>'author',
        recipe_data->>'image-link',
        recipe_data->>'servings',
        recipe_data->>'prep-time',
        recipe_data->>'cook-time'
    from "recipe-schema".recipes 
    where id::text = any(array{0})
"""


def create_recipe(rs):
    return {
        "title": rs[0],
        "description": rs[1],
        "author": rs[2],
        "image-link": rs[3],
        "servings": rs[4],
        "prep-time": rs[5],
        "cook-time": rs[6],
    }

def create_ingredients(rs):
    return {
        "id": rs[0],
        "ingredients": rs[1]
    }


def find_recipes_paged(serverParams):
    return find_paged(SQL_FIND_RECIPES, serverParams, create_recipe)


def is_subset(user_ingredients, recipe_ingredients, threshold = 0):
    ingredients_copy = recipe_ingredients.copy()

    for ui in user_ingredients:
        for ri in ingredients_copy:
            if ui.lower() in ri.lower():
                ingredients_copy.remove(ri)

    return len(ingredients_copy) / len(recipe_ingredients) <= threshold

def find_all_ingredients(user_id, threshold = 0):
    ingredients = find_all(SQL_FIND_INGREDIENTS, create_ingredients)
    print(SQL_FIND_USER_INGREDIENTS.format(user_id))
    user_ingredients = find_all(SQL_FIND_USER_INGREDIENTS.format(user_id), lambda rs: rs[0])

    # return user_ingredients

    # return set([x['id'] for ui in user_ingredients for x in ingredients for i in x['ingredients'] if ui in i])
    cookable_ids = [i['id'] for i in ingredients if is_subset(user_ingredients, i['ingredients'], threshold)]
    cookable_recipes = find_all(SQL_FIND_RECIPES_COOKABLE.format(cookable_ids), create_recipe)

    return cookable_recipes



    # for x in ingredients:
    #     if set(x['ingredients']).issubset(set(user_ingredients)):

                    


    # processed = list(map(process_word, ingredients))

    # processed = sorted(processed, key=lambda i: i['id'])

    # grouped = [{"id": key, "ingredients": list(map(lambda x: ' '.join(x['nouns']), list(value)))} for (key, value) in  groupby(processed, lambda i: i['id'])]
        
    # return ingredients


