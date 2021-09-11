import motor.motor_asyncio as motor
from typing import Any, Dict, Optional


class DictDB:
    """
    Simplified MongoDB collection wrapper
    MotorCollection methods also works
    """

    def __init__(self, col: motor.AsyncIOMotorCollection):
        self.col = col

    async def get(self, _id: Any) -> Optional[Dict[str, Any]]:
        return await self.col.find_one({"_id": _id})

    async def set(self, _id: Any, **values):
        await self.col.update_one({"_id": _id}, {"$set": values}, upsert=True)

    async def inc(self, _id: Any, field: str, amount: float):
        await self.col.update_one({"_id": _id}, {"$inc": {field: amount}})

    async def push(self, _id: Any, field: str, value: Any):
        await self.col.update_one({"_id": _id}, {"$push": {field: value}})

    async def pull(self, _id: Any, field: str, value: Any):
        await self.col.update_one({"_id": _id}, {"$pull": {field: value}})

    async def remove(self, _id: Any):
        await self.col.delete_one({"_id": _id})

    def __getattr__(self, name: str) -> Any:
        return getattr(self.col, name)


class NullDB(DictDB):
    """
    Same interface as MongoDict but does nothing
    """

    def __init__(self, *args, **kwargs):
        pass

    async def get(self, _id: Any) -> Optional[Dict[str, Any]]:
        return

    async def set(self, _id: Any, **values):
        pass

    async def inc(self, _id: Any, field: str, amount: float):
        pass

    async def push(self, _id: Any, field: str, value: Any):
        pass

    async def pull(self, _id: Any, field: str, value: Any):
        pass

    async def remove(self, _id: Any):
        pass

    async def null_coro(self, *args, **kwargs):
        return

    def __getattr__(self, name: str) -> Any:
        return self.null_coro


class JsonDB(DictDB):
    ...  # TODO
