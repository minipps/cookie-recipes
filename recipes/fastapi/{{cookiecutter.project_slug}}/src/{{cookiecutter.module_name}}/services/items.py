from {{ cookiecutter.module_name }}.db.models import Item
from {{ cookiecutter.module_name }}.domain.items import ItemCreate, ItemRead


async def create_item(payload: ItemCreate) -> ItemRead:
    item = await Item.create(name=payload.name)
    return ItemRead.model_validate(item)


async def get_item(item_id: int) -> ItemRead | None:
    item = await Item.get_or_none(id=item_id)
    return ItemRead.model_validate(item) if item is not None else None
