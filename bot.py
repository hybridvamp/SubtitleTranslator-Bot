from firebase import firebase
from creds import cred
from googletrans import Translator
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from process import (
    check,
    count,
    update,
    dt,
    format_time,
    insertlog,
    updateFile,
    logreturn,
    today_date,
)
from strings import (
    eta_text,
    help_text,
    welcome,
    caption,
    cancel_text,
    trcancel_text,
    trcancelkey,
    mmtypes,
    about,
    langs,
    empty,
    err1,
    err2,
    err3,
    err4,
    err5,
)
import time
import math
import io
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

firebase = firebase.FirebaseApplication(cred.DB_URL)
app = Client(
    "subtitle-translator-bot-subtranss",
    api_id=cred.API_ID,
    api_hash=cred.API_HASH,
    bot_token=cred.BOT_TOKEN,
)

@app.on_message(filters.command(["start"]))
def start(client, message):
    client.send_message(
        chat_id=message.chat.id,
        text=f"`Hi` **{message.from_user.first_name}**\n{welcome}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("About", callback_data="about"),
                    InlineKeyboardButton("Help", callback_data="help"),
                ],
                [
                    InlineKeyboardButton("Updates Channel", url="t.me/HYBRID_Bots"),
                    InlineKeyboardButton("Support", url="t.me/hybrid_chat"),
                ],
            ]
        ),
    )
    check_udate = dt(message.chat.id)
    if check_udate is None:
        update(message.chat.id, 0, "free")
    if not today_date == check_udate:
        update(message.chat.id, 0, "free")

@app.on_message(filters.command(["about"]))
def abouts(client, message):
    client.send_message(
        chat_id=message.chat.id,
        reply_to_message_id=message.id,
        text=about,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Updates Channel", url="t.me/HYBRID_Bots"),
                    InlineKeyboardButton("Support", url="t.me/hybrid_chat"),
                ]
            ]
        ),
    )

@app.on_message(filters.command(["help"]))
def helps(client, message):
    client.send_message(
        chat_id=message.chat.id,
        reply_to_message_id=message.id,
        text=help_text,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Updates Channel", url="t.me/HYBRID_Bots"),
                    InlineKeyboardButton("Support", url="t.me/hybrid_chat"),
                ]
            ]
        ),
    )

@app.on_message(filters.command(["cancel"]))
def cancel(client, message):
    canc = client.send_message(
        chat_id=message.chat.id,
        reply_to_message_id=message.id,
        text="`Changing status...`",
    )
    check_udate = dt(message.chat.id)
    if check_udate is None:
        update(message.chat.id, 0, "free")
    if not today_date == "waiting":
        update(message.chat.id, 0, "free")
    canc.edit(cancel_text)


"""@app.on_message(filters.command(["log"]))
def stats(client, message):
    stat = client.send_message(
        chat_id=message.chat.id,
        reply_to_message_id=message.id,
        text="`Fetching details`",
    )
    txt = logreturn()
    stat.edit(txt)"""

@app.on_message(filters.text)
def texts(client, message):
    message.reply_text(empty)

@app.on_message(filters.document)
def doc(client, message):
    res = message.reply_text("**Analysing file...**", True)
    mimmetype = message.document.mime_type
    if mimmetype in mmtypes:
        dts = dt(message.chat.id)
        if not today_date == dts:
            update(message.chat.id, 0, "free")
        status_bot = check(message.chat.id)
        counts = count(message.chat.id)
        if status_bot is None:
            update(message.chat.id, 0, "free")
        elif status_bot == "free":
            update(message.chat.id, counts, "waiting")
            # message.reply_chat_action("typing")
            res.edit(
                text="choose the desired language",
                reply_markup=InlineKeyboardMarkup(langs) 
            )
        else:
            res.edit(err1)
    else:
        res.edit(err2)

def translate_subtitles(subtitle, translator, lang):
    translated_lines = []
    for line in subtitle:
        try:
            translation = translator.translate(line, dest=lang)
            translated_lines.append(translation.text)
        except Exception:
            translated_lines.append(None)
    return translated_lines

@app.on_callback_query()
def data(client, callback_query: CallbackQuery):
    then = time.time()
    rslt = callback_query.data

    if rslt == "about":
        callback_query.message.edit(
            text=about,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Updates Channel", url="t.me/HYBRID_Bots"),
                        InlineKeyboardButton("Back", callback_data="start"),
                    ]
                ]
            ),
        )
    elif rslt == "close":
        callback_query.message.delete()
    elif rslt == "help":
        callback_query.message.edit(
            text=help_text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("close", callback_data="close"),
                        InlineKeyboardButton("Back", callback_data="start"),
                    ]
                ]
            ),
        )
    elif rslt == "start":
        callback_query.message.edit(
            text=welcome,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("About", callback_data="about"),
                        InlineKeyboardButton("Help", callback_data="help"),
                    ]
                ]
            ),
        )
    else:
        lang = rslt
        msg = callback_query.message
        message = msg.reply_to_message
        location = os.path.join("./FILES", str(message.chat.id))

        if not os.path.isdir(location):
            os.makedirs(location)

        file_path = os.path.join(location, message.document.file_name)
        subdir = client.download_media(message=message, file_name=file_path)
        translator = Translator()
        outfile = f"{subdir.replace('.srt', '')}_{lang}.srt"
        msg.delete()

        counts = count(message.chat.id)

        if counts > 10:
            message.reply_text(err3)
            os.remove(subdir)
            update(message.chat.id, counts, "free")
        else:
            tr = message.reply_text(f"Translating to {lang}", True)
            counts += 1
            update(message.chat.id, counts, "waiting")
            process_failed = False

            try:
                with io.open(subdir, "r", encoding="utf-8") as file:
                    subtitle = file.readlines()
            except Exception as e:
                print(f"Error reading subtitle file: {e}")
                tr.edit(err4)
                update(message.chat.id, counts, "free")
                return

            subtitle[0] = "1\n"

            try:
                translated_lines = translate_subtitles(subtitle, translator, lang)
            except Exception as e:
                print(f"Error during translation: {e}")
                tr.edit(str(e))
                update(message.chat.id, counts, "free")
                return

            with io.open(outfile, "w", encoding="utf-8") as f:
                total = len(subtitle)
                done = 0

                for i, translated_line in enumerate(translated_lines):
                    if translated_line is not None:
                        f.write("\n" + translated_line)
                        done += 1
                    else:
                        try:
                            receive = translator.translate(subtitle[i], dest=lang)
                            f.write(receive.text + "\n")
                            done += 1
                        except Exception:
                            pass

                    speed = done / (time.time() - then)
                    percentage = round(done * 100 / total, 2)
                    eta = format_time(int((total - done) / speed))

                    if done % 20 == 0:
                        try:
                            tr.edit(
                                text=eta_text.format(
                                    message.document.file_name,
                                    done,
                                    total,
                                    percentage,
                                    round(speed),
                                    eta,
                                    "".join(["●" for i in range(math.floor(percentage / 7))]),
                                    "".join(["○" for i in range(14 - math.floor(percentage / 7))]),
                                )
                            )
                        except Exception:
                            pass

            except Exception as e:
                print(e)
                tr.edit(str(e))
                counts -= 1
                update(message.chat.id, counts, "free")
                process_failed = True

            if not process_failed:
                tr.delete()
                if os.path.exists(outfile):
                    message.reply_document(
                        document=outfile, thumb="logo.jpg", quote=True, caption=caption
                    )
                    update(message.chat.id, counts, "free")
                    insertlog()
                    updateFile()
                    os.remove(subdir)
                    os.remove(outfile)
                else:
                    pass


app.run()
