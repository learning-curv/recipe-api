import psycopg2
import psycopg2.extras

conn = None
cursor = None

SQL_FIND_RECIPES = """
    select 
        recipe_data->>'title',
        recipe_data->>'description'
    from "recipe-schema".recipes
    order by recipe_data->>'title'
"""

def connect():
    conn = psycopg2.connect(
        database="recipedb",
        host="recipe-db",
        user="postgres",
        password="admin",
        port="5432",
    )

    cursor = conn.cursor()

    return cursor

def find_recipes_paged(cursor, offset, limit):
    if not cursor:
        return None

    query = SQL_FIND_RECIPES

    if offset:
        query += f" offset {offset}"

    if limit:
        query += f" limit {limit}"
    
    cursor.execute(query)
    return cursor.fetchall()
