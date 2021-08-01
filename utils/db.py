import motor.motor_asyncio as motor
from typing import Any, Dict, Optional

class MongoDict:
    """
    Extremely simplified mongodb collection wrapper
    """

    def __init__(self, col: motor.AsyncIOMotorCollection):
        self.col = col

    async def get(self, _id: Any) -> Optional[Dict]:
        return await self.col.find_one({'_id': _id})

    async def set(self, _id: Any, **values):
        await self.col.find_one_and_update(
            {'_id': _id},
            {'$set': values},
            upsert=True
        )

    async def delete(self, _id: Any):
        await self.col.delete_one({'_id': _id})

    def __getattr__(self, name: str) -> Any:
        return getattr(self.col, name)
