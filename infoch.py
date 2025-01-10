import re
from os import environ

id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot information
SESSION = environ.get('SESSION', 'Media_search')
BOT_TOKEN = environ.get('BOT_TOKEN', "7659748288:AAFbyf4IJ8qhdp0ALGQiPsAgXh4A2HJsW-Q")
PORT = int(environ.get('PORT', '8080'))

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', False))
PICS = (environ.get('PICS', 'https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg')).split()

# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '6168162777').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1001722984461').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_grp = environ.get('AUTH_GROUP')
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://sushankm16:4i1WAfPYKWyqPIDD@cluster0.sngp9pz.mongodb.net/?retryWrites=true&w=majority")
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Telegram_files')

# FSUB
auth_channel = environ.get('AUTH_CHANNEL', '')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
REQ_CHANNEL = environ.get("REQ_CHANNEL", '-1001935365147')
REQ_CHANNEL = int(REQ_CHANNEL) if REQ_CHANNEL and id_pattern.search(REQ_CHANNEL) else False
JOIN_REQS_DB = environ.get("JOIN_REQS_DB", DATABASE_URI)

# Others
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1001623633000'))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'VJ_Bot_Disscussion')
P_TTI_SHOW_OFF = is_enabled((environ.get('P_TTI_SHOW_OFF', "True")), False)
BOOK_REVIEW = is_enabled((environ.get('BOOK_REVIEW', "True")), True)
SINGLE_BUTTON = is_enabled((environ.get('SINGLE_BUTTON', "True")), False)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", """<b>ɴᴀᴍᴇ: <code>{file_name}</code> \n\nJᴏɪɴ Nᴏᴡ: [⚡ VJ Bots⚡](https://t.me/VJ_Bots)</b>""")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
BOOK_TEMPLATE = environ.get(
    "BOOK_TEMPLATE",
    "<b>Query: {query}</b>\n\n📚 **Title**: {title}\n✍️ **Author(s)**: {authors}\n⭐ **Rating**: {rating}/5\n📖 **Description**: {description}\n📅 **Published**: {published_date}"
)
LONG_DESCRIPTION = is_enabled(environ.get("LONG_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "False"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '-1001722984461')).split()]
MELCOW_NEW_USERS = is_enabled((environ.get('MELCOW_NEW_USERS', "False")), True)
PROTECT_CONTENT = is_enabled((environ.get('PROTECT_CONTENT', "False")), False)
PUBLIC_FILE_STORE = is_enabled((environ.get('PUBLIC_FILE_STORE', "True")), True)

LOG_STR = "Current Customized Configurations are:-\n"
LOG_STR += ("Book Review is enabled. Bot will be showing book details for your queries.\n" if BOOK_REVIEW else "Book Review is disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found, Users will be redirected to send /start to Bot PM instead of sending files directly\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled. Files will be sent in PM.\n")
LOG_STR += ("SINGLE_BUTTON is Found, filename and file size will be shown in a single button instead of two separate buttons\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled. Filename and file size will be shown as different buttons.\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}. Your files will be sent along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found. Default captions of file will be used.\n")
LOG_STR += ("Long descriptions are enabled for book reviews." if LONG_DESCRIPTION else "Long descriptions are disabled for book reviews.\n")
LOG_STR += ("Spell Check Mode Is Enabled. The bot will suggest related books if a book is not found.\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled.\n")
LOG_STR += (f"MAX_LIST_ELM Found. Long lists will be shortened to first {MAX_LIST_ELM} elements.\n" if MAX_LIST_ELM else "Full list of details will be shown. Restrict them by adding a value to MAX_LIST_ELM.\n")
LOG_STR += f"Your current BOOK_TEMPLATE is {BOOK_TEMPLATE}"