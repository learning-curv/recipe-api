from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, parse_obj_as, ValidationError
import requests

from postgres_interface import find_recipes_paged, find_all_ingredients


class Token(BaseModel):
    type: int | None = None
    name: str | None = None


class Messure(BaseModel):
    time: int
    unit: str


class Ingredients(BaseModel):
    name: str
    unit: str | None = None
    notes: str | None = None
    amount: str


class IngredientGroup(BaseModel):
    title: str | None = None
    ingredients: list[Ingredients]


class Instruction(BaseModel):
    title: str | None = None
    instructions: list[str]


class Recipe(BaseModel):
    link: str
    title: str
    author: str | None = None
    servings: int
    cook_time: Messure
    prep_time: Messure
    description: str
    ingredient_groups: list[IngredientGroup]
    instruction_groups: list[Instruction]


# id          | bfa6d474-57e4-4878-93c2-7ad31933f32b
# recipe_data | {"link": "https://www.thechunkychef.com/spiced-soft-molasses-cookies/", "title": "Spiced Soft Molasses Cookies", "author": null, "servings": "24", "cook_time": {"time": "15", "unit": "minutes"}, "prep_time": {"time": "10", "unit": "minutes"}, "description": "Soft and perfectly spiced, these cookies will soon become one of your favorite! These cookies are soft and chewy, with that classic dark molasses flavor!", "ingredient_groups": [{"title": null, "ingredients": [{"name": "packed brown sugar", "unit": "cup", "notes": null, "amount": "1"}, {"name": "vegetable shortening", "unit": "cup", "notes": null, "amount": "3/4"}, {"name": "molasses", "unit": "cup", "notes": null, "amount": "1/4"}, {"name": "egg", "unit": null, "notes": null, "amount": "1"}, {"name": "all purpose flour", "unit": "cups", "notes": null, "amount": "2 1/4"}, {"name": "baking soda", "unit": "tsp", "notes": null, "amount": "2"}, {"name": "ground cinnamon", "unit": "tsp", "notes": null, "amount": "1"}, {"name": "ground ginger", "unit": "tsp", "notes": null, "amount": "1"}, {"name": "ground cloves", "unit": "tsp", "notes": null, "amount": "1/2"}, {"name": "salt", "unit": "tsp", "notes": null, "amount": "1/4"}]}], "instruction_groups": [{"title": null, "instructions": ["Preheat oven to 325 degrees.", "In a large bowl, beat brown sugar, shortening, molasses, and egg until combined. Stir in remaining ingredients.", "Shape dough into rounded balls, about 1” in diameter. Place some granulated sugar in a small bowl and roll balls in the sugar.", "Place the cookie balls onto a parchment paper lined baking sheet, about 2” apart.", "Bake for 13-16 minutes until just set and cookies appear dry and cracked.", "Remove from baking sheet to cooling rack"]}]}

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/hello_world")
def hello_world():
    return "Hello world"


@app.get("/api/recipes")
async def get_all_recipes(offset: int = 0, limit: int = 10):
    return find_recipes_paged({"offset": offset, "limit": limit})

@app.get("/api/recipes/cook/{user_id}")
async def get_all_ingredients(user_id: str, threshold: float = 0):
    return find_all_ingredients(user_id, 1 - threshold)


@app.get("/api/recipe/{recipe_id}")
async def token(recipe_id: str, q: str | None = None):
    # postgres select where id = recipe_id
    # return recipe_data
    api_data = {
        "link": "https://www.thechunkychef.com/spiced-soft-molasses-cookies/",
        "title": "Spiced Soft Molasses Cookies",
        "author": None,
        "servings": "24",
        "cook_time": {"time": "15", "unit": "minutes"},
        "prep_time": {"time": "10", "unit": "minutes"},
        "description": "Soft and perfectly spiced, these cookies will soon become one of your favorite! These cookies are soft and chewy, with that classic dark molasses flavor!",
        "ingredient_groups": [
            {
                "title": None,
                "ingredients": [
                    {
                        "name": "packed brown sugar",
                        "unit": "cup",
                        "notes": None,
                        "amount": "1",
                    },
                    {
                        "name": "vegetable shortening",
                        "unit": "cup",
                        "notes": None,
                        "amount": "3/4",
                    },
                    {"name": "molasses", "unit": "cup", "notes": None, "amount": "1/4"},
                    {"name": "egg", "unit": None, "notes": None, "amount": "1"},
                    {
                        "name": "all purpose flour",
                        "unit": "cups",
                        "notes": None,
                        "amount": "2 1/4",
                    },
                    {
                        "name": "baking soda",
                        "unit": "tsp",
                        "notes": None,
                        "amount": "2",
                    },
                    {
                        "name": "ground cinnamon",
                        "unit": "tsp",
                        "notes": None,
                        "amount": "1",
                    },
                    {
                        "name": "ground ginger",
                        "unit": "tsp",
                        "notes": None,
                        "amount": "1",
                    },
                    {
                        "name": "ground cloves",
                        "unit": "tsp",
                        "notes": None,
                        "amount": "1/2",
                    },
                    {"name": "salt", "unit": "tsp", "notes": None, "amount": "1/4"},
                ],
            }
        ],
        "instruction_groups": [
            {
                "title": None,
                "instructions": [
                    "Preheat oven to 325 degrees.",
                    "In a large bowl, beat brown sugar, shortening, molasses, and egg until combined. Stir in remaining ingredients.",
                    "Shape dough into rounded balls, about 1” in diameter. Place some granulated sugar in a small bowl and roll balls in the sugar.",
                    "Place the cookie balls onto a parchment paper lined baking sheet, about 2” apart.",
                    "Bake for 13-16 minutes until just set and cookies appear dry and cracked.",
                    "Remove from baking sheet to cooling rack",
                ],
            }
        ],
    }
    try:
        return parse_obj_as(Recipe, api_data)

    except ValidationError as e:
        return e.errors()


@app.put("/api/recipe/{recipe_id}")
async def update_recipe(recipe_id: str, recipe: Recipe):
    # postgres update table for recipe_id

    return {
        "link": recipe.link,
        "title": recipe.title,
        "author": recipe.author,
        "servings": recipe.servings,
        "cook_time": recipe.cook_time,
        "prep_time": recipe.prep_time,
        "description": recipe.description,
        "ingredient_groups": recipe.ingredient_groups,
        "instruction_groups": recipe.instruction_groups,
    }


@app.get("/api/token/{token_id}")
async def token(token_id: int, q: str | None = None):
    api_data = {"name": 12345, "type": "123av"}
    try:
        return parse_obj_as(Token, api_data)

    except ValidationError as e:
        return e.errors()


@app.put("/api/token/{token_id}")
async def update_token(token_id: int, token: Token):
    return {"token_id": token_id, "name": token.name, "type": token.type}
