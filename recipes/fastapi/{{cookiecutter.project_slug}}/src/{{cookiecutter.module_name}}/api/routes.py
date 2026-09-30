from fastapi import APIRouter, HTTPException

from {{ cookiecutter.module_name }}.domain.items import ItemCreate, ItemRead
from {{ cookiecutter.module_name }}.services import items

router = APIRouter()


@router.post("/items", status_code=201)
async def create_item(payload: ItemCreate) -> ItemRead:
    return await items.create_item(payload)


@router.get("/items/{item_id}")
async def get_item(item_id: int) -> ItemRead:
    item = await items.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
