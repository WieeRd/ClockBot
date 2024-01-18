from typing import Any

import motor.motor_asyncio as motor


class DictDB:
    """
    Simplified MongoDB collection wrapper
    MotorCollection methods also works
    """

    def __init__(self, col: motor.AsyncIOMotorCollection) -> None:
        self.col = col

    async def get(self, _id: Any) -> dict[str, Any] | None:
        return await self.col.find_one({"_id": _id})

    async def set(self, _id: Any, **values) -> None:
        await self.col.update_one({"_id": _id}, {"$set": values}, upsert=True)

    async def inc(self, _id: Any, field: str, amount: float) -> None:
        await self.col.update_one({"_id": _id}, {"$inc": {field: amount}}, upsert=True)

    async def push(self, _id: Any, field: str, value: Any) -> None:
        await self.col.update_one({"_id": _id}, {"$push": {field: value}})

    async def pull(self, _id: Any, field: str, value: Any) -> None:
        await self.col.update_one({"_id": _id}, {"$pull": {field: value}})

    async def remove(self, _id: Any) -> None:
        await self.col.delete_one({"_id": _id})

    def __getattr__(self, name: str) -> Any:
        return getattr(self.col, name)


class NullDB(DictDB):
    """
    Same interface as DictDB but does nothing
    """

    def __init__(self, *args, **kwargs) -> None:
        pass

    async def get(self, _id: Any) -> dict[str, Any] | None:
        return

    async def set(self, _id: Any, **values) -> None:
        pass

    async def inc(self, _id: Any, field: str, amount: float) -> None:
        pass

    async def push(self, _id: Any, field: str, value: Any) -> None:
        pass

    async def pull(self, _id: Any, field: str, value: Any) -> None:
        pass

    async def remove(self, _id: Any) -> None:
        pass

    async def null_coro(self, *args, **kwargs) -> None:
        return

    def __getattr__(self, name: str) -> Any:
        return self.null_coro


class JsonDB(DictDB): ...  # TODO
