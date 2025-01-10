import logging
import logging.config

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
import requests  # Added for the book review functionality

class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=500,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        await super().start()
        await Media.ensure_indexes()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")

    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Iterate through a chat sequentially."""
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + new_diff + 1)))
            for message in messages:
                yield message
                current += 1

    async def book_review(self, query):
        """Fetch book review information."""
        api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if "items" in data:
                book = data["items"][0]
                title = book["volumeInfo"].get("title", "N/A")
                authors = ", ".join(book["volumeInfo"].get("authors", []))
                description = book["volumeInfo"].get("description", "No description available.")
                return f"**Title:** {title}\n**Authors:** {authors}\n\n**Description:** {description}"
            else:
                return "No results found for your query."
        else:
            return "Failed to fetch book information. Please try again later."


# Replaced IMDb command with the book review command
@app.on_message(filters.command("book") & ~filters.edited)
async def handle_bookreview(client, message):
    query = " ".join(message.command[1:])
    if not query:
        await message.reply("Please provide the title of a book.")
        return

    review = await app.book_review(query)
    await message.reply_text(review)


app = Bot()
app.run()