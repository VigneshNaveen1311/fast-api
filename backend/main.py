from fastapi import FastAPI, Query, Path
from pydantic import BaseModel

from typing import Annotated

class Item(BaseModel):
    name: str
    descxn: str | None = None
    price: float
    tax: float | None = None


app = FastAPI()

users= []
 
@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/users")
def get_users():
    return users

@app.post("/users")
def create_user(name: str):
    user = {"id": len(users)+1, "name": name}
    users.append(user)
    return {"message": "User has been added", "users": users}

@app.put("/users")
def update_user(id: int, name: str):
    for user in users:
        if user["id"] == id:
            user["name"] = name
            return {"message": "User has been updated", "user": user}
    return {"message": "ID not found"}

@app.delete("/users")
def delete_user(id:int):
    for user in users:
        if user["id"] == id:
            users.remove(user)
            return {"message": "User has been deleted", "users": users}
    return {"message": "User not found"}

@app.get("/user/{id}")
def get_user(id: int):
    for user in users:
        if user["id"] == id:
            return user
    return {"message": "User not found"}

@app.get("/user")
def get_user_by_query(id: int):
    for user in users:
        if user["id"] == id:
            return user
    return {"message": "User not found"}

@app.post("/items/")
async def create_item(item: Item):
    item.name = item.name.capitalize()
    return item
    #or use
    # item_dict = item.model_dump()
    # item_dict.update({"name":item.name.capitalize()})
    # return item_dict()
    # but this doesnt affect the actual stored data


#using both query and path parameters with request body
@app.put("/items/{item_id}") #item_id is path parameter
async def update_item(item_id: int, item: Item, q: str | 
                      None = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q: #q is query parameter
        result.update({'q': q})
    return result


@app.get("/items/{item_id}")
async def read_items(item_id: Annotated[int, Path(title="The ID of the item to get", description="The unique identifier of the item", gt=1)], 
                     q: Annotated[list | None, Query(max_length=2)] = ["a", "b"]):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results