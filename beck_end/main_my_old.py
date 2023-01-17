from typing import Union
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .fight_models import FightConfig


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    data: list


@app.get("/")
def read_root():
    return {"Hello": "World!!!"}


@app.put("/save_settings")
def save_settings(item: Item):
    print(f"{item=}")
    for elem in item.data:
        print(elem["group_name"])
    with open("data/save.json", "w", encoding="utf-8") as file:
        json.dump(item.dict(), file, indent=2)
        # json.dump(item, file, indent=2)
    return {"result": "ok"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/fight")
def send_schems():
    # json_compatible_item_data = jsonable_encoder(FightConfig().schema_json())
    # return JSONResponse(content=json_compatible_item_data)
    return JSONResponse(json.loads(FightConfig().schema_json()))


@app.get("/fight_info")
def send_full_info():
    with open("data/save.json", "r", encoding="utf-8") as file:
        # json.dump(item.dict(), file, indent=2)
        info = json.load(file)
    return JSONResponse(info)
