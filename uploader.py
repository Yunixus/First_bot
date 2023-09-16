import uuid
from typing import Union

import sqlalchemy.orm
from pyrogram.parser import markdown
from sqlalchemy.orm import Session
from pyrogram import filters, Client, enums
from pyrogram.types import Message, InputMediaPhoto, InputMediaVideo, Chat, ChatPreview
from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,
                            InlineKeyboardButton)
import models.Channel
import models.Message
import models.Media
import models.StopWords
import models.posts_context

database_name = " "
api_id = 0
api_hash = " "
pyrogram_client = Client(api_id=api_id, api_hash=api_hash, name=" ")
chat_id= 0
network_members = []


@pyrogram_client.on_message(filters=filters.channel)
async def get_channel_update(bot: Client, message: Message):
    try:
        session = Session(bind=models.posts_context.engine)
        db_chats = session.query(models.Channel.Channel).filter(models.Channel.Channel.telegram_id==message.chat.id).all()
        db_chats_ids = [db_chat.telegram_id for db_chat in db_chats]
        if message.chat.id not in db_chats_ids:
            return
        caption = ""
        stop_words = [word.word for word in session.query(models.StopWords.stop_words).all()]
        entities = []
        urls = []

        if message.caption is not None:
            caption += message.caption
            _urls = list(filter(lambda x: 'link' in x.type.name.lower(), message.caption.entities))
            for url in _urls:
                urls.append(url.url)
            _urls = list(filter(lambda x: 'url' in x.type.name.lower(), message.caption.entities))
            for url in _urls:
                url = message.caption[url.offset:url.offset + url.length]
                urls.append(url)

        if message.text is not None:
            caption += message.text
            entities.extend(message.text.entities)
            _urls = list(filter(lambda x: 'link' in x.type.name.lower(), message.text.entities))
            for url in _urls:
                urls.append(url.url)
            _urls = list(filter(lambda x: 'url' in x.type.name.lower(), message.text.entities))
            for url in _urls:
                url = message.text[url.offset:url.offset + url.length]
                urls.append(url)

        for stop_word in stop_words:
            if stop_word in caption:
                caption = "advertisement"
                break

        for url in urls:
            try:
                chan_info: Union[Chat, ChatPreview] = await bot.get_chat(url)
                if chan_info.title != message.chat.title:
                    caption = "advertisement"
                    break
            except Exception as error:
                caption = "advertisement"
                break

        if message.media_group_id is None and message.media is None:
            return
        if message.media is not None:
            if message.media.name == "VIDEO_NOTE":
                return
        db_chat: models.Channel.Channel = next(iter(db_chats))
        db_message = models.Message.Message(id=uuid.uuid4(), message_channel=db_chat.id,
                                            telegram_id=message.id, media_group_id=message.media_group_id,
                                            text=caption)
        if message.media_group_id is None:
            session.add(db_message)
            session.commit()
            return
        other_message = session.query(models.Message.Message).filter(
            models.Message.Message.media_group_id == message.media_group_id).all()
        if len(other_message) == 0:
            session.add(db_message)
            session.commit()
    except Exception as error:
        print(f"error in method get_channel_update {error}")

async def send_message_to_group():
    updated = False
    while not updated:
        try:
            bot: Client = pyrogram_client
            session = Session(bind=models.posts_context.engine)
            db_channel: models.Channel.Channel = session.query(models.Channel.Channel).order_by(models.Channel.Channel.priority.desc()).first()
            if db_channel is None:
                return
            db_message = session.query(models.Message.Message).filter(models.Message.Message.message_channel==db_channel.id).first()
            messages_count = session.query(models.Message.Message).count()
            if messages_count == 0:
                return
            if db_message is None:
                db_channel.priority -= 1
                session.commit()
                continue
            if db_message.text == "advertisement":
                session.delete(db_message)
                session.commit()
                continue
            try:
                if db_message.media_group_id != -1:
                    await bot.copy_media_group(chat_id=chat_id, from_chat_id=db_channel.telegram_id, message_id=db_message.telegram_id,
                                               captions="")
                    updated = True
                else:
                    await bot.copy_message(chat_id=chat_id,from_chat_id=db_channel.telegram_id,message_id=db_message.telegram_id,
                                           caption="")
                    updated = True
            finally:
                db_channel.priority -= 1
                if db_channel.priority == 0:
                    db_channel.priority = 10
                session.delete(db_message)
                session.commit()
        except Exception as error:
            print(error)

@pyrogram_client.on_message(filters=filters.command("join_chat"))
async def join_chat(bot: Client, message: Message):
    try:
        chat_name = ""
        chat_id = -1
        session = Session(bind=models.posts_context.engine)
        if len(message.command) == 1:
            chat_history = bot.get_chat_history(message.chat.id, limit=1)
            async for history_message in chat_history:
                if history_message.forward_from_chat is not None:
                    chat_id = history_message.forward_from_chat.id
                    chat_name = history_message.forward_from_chat.title
                    dialogs = bot.get_dialogs()
                    dialogs_ids = [dialog.chat.id async for dialog in dialogs]
                    if chat_id not in dialogs_ids:
                        success = await bot.join_chat(chat_id=chat_id)
        else:
            chat = await bot.get_chat(message.command[-1])
            if chat.type.name.lower() == "channel":
                chat_id = chat.id
                chat_name = chat.title
                dialogs = bot.get_dialogs()
                dialogs_ids = [dialog.chat.id async for dialog in dialogs]
                if chat.id not in dialogs_ids:
                    success = await bot.join_chat(chat_id=chat.id)
        if chat_name == "":
            return
        channels: sqlalchemy.orm.Query = session.query(models.Channel.Channel).filter(models.Channel.Channel.telegram_id==chat_id).all()
        if len(channels) == 0:
            channel = models.Channel.Channel(id=uuid.uuid4(), telegram_id=chat_id,
                                             channel_name=chat_name)
            session.add(channel)
            session.commit()
            await bot.send_message(message.chat.id, f"Успешно подписалась на канал: {chat_name}")
    except Exception as error:
        try:
            await bot.send_message(message.chat.id, str(error))
        finally:
            print(str(error))

@pyrogram_client.on_message(filters=filters.command(["get_chats"]))
async def get_chats(bot: Client, message: Message):
    session = Session(bind=models.posts_context.engine)
    try:
        all_groups = session.query(models.Channel.Channel).all()
        result_lines = "Привет я подписана на следущие каналы:\n"
        for channel in all_groups:
            result_lines += f"- {channel.channel_name}\n"
        await bot.send_message(message.chat.id, result_lines)
    except Exception as error:
        print(error)

@pyrogram_client.on_message(filters.command(["get_count_posts"]))
async def get_count_posts(bot: Client, message: Message):
    session = Session(bind=models.posts_context.engine)
    try:
        groups = session.query(models.Channel.Channel).all()
        groups_count = {}
        result = "В очереди накопилось следующее количество постов:\n"
        for group in groups:
            messages = session.query(models.Message.Message).all()
            groups_count[group.channel_name] = len(list(filter(lambda x: x.message_channel == group.id
                                                                         and x.text != "advertisement", messages)))
            result += f"{group.channel_name}: {groups_count[group.channel_name]}\n"
        await bot.send_message(message.chat.id, result)
    except Exception as error:
        print(str(error))

@pyrogram_client.on_message(filters=filters.command(["leave_chat"]))
async def leave_chat(bot: Client, message: Message):
    session = Session(bind=models.posts_context.engine)
    try:
        if len(message.command) > 1:
            group = session.query(models.Channel.Channel).filter(models.Channel.Channel.channel_name==message.command[1]).all()
            group = next(iter(group), None)
            if group is None:
                await bot.send_message(message.chat.id, f"Ааа, эмм, такой группы нет прости:(")
                return
            await bot.leave_chat(group.telegram_id)
            session.delete(group)
            session.commit()
            await bot.send_message(message.chat.id, f"Успешно отписалась от канала: {message.command[1]}")
        else:
            await bot.send_message(message.chat.id, "Привет эту комманду надо использовать так:\n /leave_chat {Название канала}")
    except Exception as error:
        print(error)

@pyrogram_client.on_message(filters.command(["get_stop_words"]))
async def get_stop_words(bot: Client, message: Message):
    session = Session(bind=models.posts_context.engine)
    try:
        words = session.query(models.StopWords.stop_words).all()
        result_line = "Мои слова на которые я триггерюсь(0o0):\n"
        for word in words:
            result_line += f"{word.word};"
        await bot.send_message(message.chat.id, result_line)
    except Exception as error:
        print(error)

@pyrogram_client.on_message(filters.command(["add_stop_word"]))
async def add_stop_word(bot: Client, message: Message):
    session = Session(bind=models.posts_context.engine)
    try:
        if len(message.command) == 1:
            await bot.send_message(message.chat.id, "Ты неправильно используешь комманду, надо:\n add_stop_word {слова}")
        else:
            message_commands = message.command[1:]
            stop_words = [word.word for word in session.query(models.StopWords.stop_words).all()]
            increment = session.query(models.StopWords.stop_words).order_by(models.StopWords.stop_words.key.desc()).first().key + 1
            for word in message_commands:
                if word in stop_words:
                    continue
                word = models.StopWords.stop_words(key=increment, word=word)
                session.add(word)
                increment += 1
            session.commit()
    except Exception as error:
        print(error)