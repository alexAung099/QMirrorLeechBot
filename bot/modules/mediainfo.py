# https://github.com/Appeza/tg-mirror-leech-bot

from telegram import Message
import os
from subprocess import run
from bot.helper.ext_utils.shortenurl import short_url
from telegram.ext import CommandHandler
from bot import LOGGER, dispatcher, app
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage
from helper.ext_utils.telegraph_helper import telegraph


def mediainfo(update, context):
    message:Message = update.effective_message
    help_msg = "\n<b>By replying to message (including media):</b>"
    help_msg += f"\n<code>/{BotCommands.MediaInfoCommand}" + " {message}" + "</code>"
    if not message.reply_to_message: return sendMessage(help_msg, context.bot, update)
    if not message.reply_to_message.media: return sendMessage(help_msg, context.bot, update)
    sent = sendMessage('Running mediainfo. Downloading your file.', context.bot, update)
    file = None
    try:
        VtPath = os.path.join("Mediainfo", str(message.from_user.id))
        if not os.path.exists("Mediainfo"): os.makedirs("Mediainfo")
        if not os.path.exists(VtPath): os.makedirs(VtPath)
        filename = os.path.join(VtPath, message.reply_to_message.document.file_name)
        file = app.download_media(message=message.reply_to_message.document, file_name=filename)
    except Exception as e:
        LOGGER.error(e)
        try: os.remove(file)
        except: pass
        file = None
    if not file: return editMessage("Error when downloading. Try again later.", sent)
    cmd = ['mediainfo', f'"{file}"']
    LOGGER.info(cmd)
    try: os.remove(file)
    except: pass
    process = run(cmd, capture_output=True, shell=True)
    reply = f"<h2>MediaInfo: {message.reply_to_message.document.file_name}</h2>"
    stderr = process.stderr.decode()
    stdout = process.stdout.decode()
    if len(stdout) != 0:
        reply += f"<b>Stdout:</b><br><br><pre>{stdout}</pre><br><br><br>"
        LOGGER.info(f"mediainfo - {cmd} - {stdout}")
    if len(stderr) != 0:
        reply += f"<b>Stderr:</b><br><br><pre>{stderr}</pre>"
        LOGGER.error(f"mediainfo - {cmd} - {stderr}")
    help = telegraph.create_page(title='MediaInfo', content=reply)["path"]
    editMessage(short_url(f"https://telegra.ph/{help}"), sent)


mediainfo_handler = CommandHandler(BotCommands.MediaInfoCommand, mediainfo,
    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(mediainfo_handler)
