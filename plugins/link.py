from pyrogram import Client, filters
from pyrogram.types import Message
from database.auth_groups import is_authorized_chat, add_authorized_chat, remove_authorized_chat, get_authorized_chats  # New DB module
from info import BIN_CHANNEL, LOG_CHANNEL, ADMINS, IS_SHORTLINK, BOT_USERNAME
from utils import get_shortlink  # For shortlinks if enabled
from avbot import av_verification  # Verification check
from database.users_db import db  # For premium/ban checks
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def generate_link(client: Client, file_message: Message) -> str:
    """Forward file to BIN_CHANNEL and generate direct/stream link."""
    try:
        # Forward to BIN_CHANNEL
        forwarded = await client.forward_messages(BIN_CHANNEL, file_message.chat.id, file_message.id)
        
        # Generate base link
        hash_str = forwarded.id  # Simplified; use get_hash if available from web/utils/file_properties.py
        base_link = f"https://t.me/{BOT_USERNAME}/{forwarded.id}?hash={hash_str}"
        
        # Shorten if enabled
        link = await get_shortlink(base_link) if IS_SHORTLINK else base_link
        
        # Log to LOG_CHANNEL
        await client.send_message(
            LOG_CHANNEL,
            f"Link generated in group {file_message.chat.id} by {file_message.from_user.id}\nLink: {link}"
        )
        return link
    except Exception as e:
        logger.error(f"Error generating link: {str(e)}")
        raise

@Client.on_message(filters.command("link") & filters.group & filters.reply)
async def link_handler(client: Client, message: Message):
    """Handle /link in authorized groups only."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Check if group is authorized
    if not await is_authorized_chat(chat_id):
        await message.reply("❌ This group is not authorized. Contact admin to authorize.")
        return
    
    # FSUB check (from avbot.py)
    if not await is_user_joined(client, message):
        return
    
    # Ban check
    if await db.is_user_blocked(user_id):
        await message.reply("🚫 You are banned from using this bot.")
        return
    
    # Verification for non-premium
    if not await db.has_premium_access(user_id):
        if not await av_verification(client, message):
            return
    
    # Replied media check
    replied_msg = message.reply_to_message
    if not replied_msg or not replied_msg.media:
        await message.reply("❌ Reply to a file/video/audio with /link.")
        return
    
    if not (replied_msg.document or replied_msg.video or replied_msg.audio):
        await message.reply("❌ Reply to a valid media type (document/video/audio).")
        return
    
    # Size limit (Telegram max 2GB)
    if replied_msg.document and replied_msg.document.file_size > 2 * 1024 * 1024 * 1024:
        await message.reply("❌ File too large (>2GB).")
        return
    
    await message.reply("🔄 Generating link...")
    
    try:
        link = await generate_link(client, replied_msg)
        file_name = replied_msg.document.file_name if replied_msg.document else "Media"
        file_size = replied_msg.document.file_size / (1024 * 1024) if replied_msg.document else 0
        await message.reply(
            f"**File:** {file_name}\n**Size:** {file_size:.1f} MB\n\n**Direct Link:** {link}\n\nPowered by {BOT_USERNAME}",
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")
        await client.send_message(LOG_CHANNEL, f"Error in /link (group {chat_id}): {str(e)}")

# Admin Commands for Authorized Groups (in PM)
@Client.on_message(filters.command("add_auth") & filters.private & filters.user(ADMINS))
async def add_auth_handler(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("Usage: /add_auth -1001234567890")
        return
    try:
        chat_id = int(message.command[1])
        if await add_authorized_chat(chat_id, message.from_user.id):
            await message.reply(f"✅ Group {chat_id} authorized.")
        else:
            await message.reply("❌ Group already authorized.")
    except ValueError:
        await message.reply("Invalid group ID.")

@Client.on_message(filters.command("rm_auth") & filters.private & filters.user(ADMINS))
async def rm_auth_handler(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("Usage: /rm_auth -1001234567890")
        return
    try:
        chat_id = int(message.command[1])
        if await remove_authorized_chat(chat_id):
            await message.reply(f"✅ Group {chat_id} removed.")
        else:
            await message.reply("❌ Group not found.")
    except ValueError:
        await message.reply("Invalid group ID.")

@Client.on_message(filters.command("auth_list") & filters.private & filters.user(ADMINS))
async def auth_list_handler(client: Client, message: Message):
    chats = await get_authorized_chats()
    if not chats:
        await message.reply("No authorized groups.")
        return
    text = "📋 Authorized Groups:\n" + "\n".join([f"- {c['chat_id']} (Added by {c['added_by']} on {c['added_at']})" for c in chats])
    await message.reply(text)
