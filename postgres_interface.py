import psycopg2
import psycopg2.extras

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
        recipe_data->>'description'
    from "recipe-schema".recipes
    order by recipe_data->>'title'
"""


def create_recipe(rs):
    return {"title": rs[0], "description": rs[1]}


def find_recipes_paged(serverParams):
    return find_paged(SQL_FIND_RECIPES, serverParams, create_recipe)
