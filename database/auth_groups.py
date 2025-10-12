from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

# Reuse DB connection from users_db.py (assume db_client/db defined there)
from .users_db import db  # Import your db instance

async def is_authorized_chat(chat_id: int) -> bool:
    chat = await db.authorized_chats.find_one({"chat_id": chat_id})
    return bool(chat)

async def add_authorized_chat(chat_id: int, admin_id: int) -> bool:
    if await is_authorized_chat(chat_id):
        return False
    await db.authorized_chats.insert_one({
        "chat_id": chat_id,
        "added_by": admin_id,
        "added_at": datetime.now()
    })
    return True

async def remove_authorized_chat(chat_id: int) -> bool:
    result = await db.authorized_chats.delete_one({"chat_id": chat_id})
    return result.deleted_count > 0

async def get_authorized_chats() -> list:
    return await db.authorized_chats.find().to_list(length=100)
