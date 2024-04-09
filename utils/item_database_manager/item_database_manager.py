from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .models import Item, Property, Skill


class ItemDatabaseManager:

    def __init__(self, connection_url: str):
        self._connection_url = connection_url
        self._engine = create_async_engine(self._connection_url, echo=True)
        self._async_session = async_sessionmaker(bind=self._engine)
        self._session = None

    async def __aenter__(self):
        await self.setup()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def setup(self) -> None:
        self._session = self._async_session()

    async def close(self) -> None:
        await self._session.close()

    async def search_items(self, query: str) -> Sequence[Item]:
        statement = select(Item).where(Item.title.icontains(query))
        result = await self._session.execute(statement)
        items = result.scalars().all()

        return items
    
    async def insert_or_replace_item(self, item: Item) -> None:
        await self.delete_item(item.item_id)
        self._session.add(item)

        await self._session.commit()

    async def delete_item(self, item_id: int) -> None:
        existing_item = await self.get_item(item_id)
        if existing_item is not None:
            await self._session.delete(existing_item)

        await self._session.commit()

    async def get_item(self, item_id: int) -> Item | None:
        statement = select(Item).where(Item.item_id == item_id)
        result = await self._session.execute(statement)
        item = result.scalars().first()

        return item

    async def get_item_properties(self, item: Item) -> list[Property]:
        item_properties = await item.awaitable_attrs.properties
        return item_properties
    
    async def get_item_skills(self, item: Item) -> list[Skill]:
        item_skills = await item.awaitable_attrs.skills
        return item_skills
