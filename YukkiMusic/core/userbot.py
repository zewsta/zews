#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the MIT License.
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#
import asyncio
import sys
import traceback
from datetime import datetime
from functools import wraps

from pyrogram import Client, StopPropagation
from pyrogram.errors import (
    ChatSendMediaForbidden,
    ChatSendPhotosForbidden,
    ChatWriteForbidden,
    FloodWait,
    MessageIdInvalid,
    MessageNotModified,
)
from pyrogram.handlers import MessageHandler

import config

from ..logging import LOGGER

assistants = []
assistantids = []


class Userbot:
    def __init__(self):
        self.clients = [
            Client(
                f"YukkiString_{i}",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=session.strip(),
            )
            for i, session in enumerate(config.STRING_SESSIONS, start=1)
        ]
        self.handlers = []

    async def _start(self, client, index):
        LOGGER(__name__).info(f"Asistanlar Başlatılıyor {index}")
        try:
            await client.start()
            assistants.append(index)
            try:
                await client.send_message(config.LOG_GROUP_ID, "Asistan Başladı")
            except ChatWriteForbidden:
                try:
                    await client.join_chat(config.LOG_GROUP_ID)
                    await client.send_message(config.LOG_GROUP_ID, "Asistan Başladı")
                except Exception:
                    LOGGER(__name__).error(
                        f"Asistan {index} log grubuna mesaj gönderemedi."
                        f"Asistanın log grubuna eklendiğinden emin olun."
                    )
                    sys.exit(1)

            get_me = await client.get_me()
            client.username = get_me.username
            client.id = get_me.id
            client.mention = get_me.mention
            assistantids.append(get_me.id)
            client.name = f"{get_me.first_name} {get_me.last_name or ''}".strip()

            # Add stored handlers to the client
            for handler, group in self.handlers:
                client.add_handler(handler, group)

        except Exception as e:
            LOGGER(__name__).error(
                f"Asistan hesabı {index} hata ile başarısız oldu: {str(e)}. çıkılıyor..."
            )
            sys.exit(1)

    async def start(self):
        """Tüm asistanları başlatın"""
        tasks = [
            self._start(client, i) for i, client in enumerate(self.clients, start=1)
        ]
        await asyncio.gather(*tasks)

    async def stop(self):
        """Tüm asistanları durdurun"""
        tasks = [client.stop() for client in self.clients]
        await asyncio.gather(*tasks)

    def on_message(self, filters=None, group=0):
        """Hata işleme ile mesajları işlemek için dekoratör."""

        def decorator(func):
            @wraps(func)
            async def wrapper(client, message):
                try:
                    await func(client, message)
                except FloodWait as e:
                    LOGGER(__name__).warning(
                        f"FloodWait: {e.value} saniye boyunca duruyor."
                    )
                    await asyncio.sleep(e.value)
                except (
                    ChatWriteForbidden,
                    ChatSendMediaForbidden,
                    ChatSendPhotosForbidden,
                    MessageNotModified,
                    MessageIdInvalid,
                ):
                    pass
                except StopPropagation:
                    raise
                except Exception as e:
                    # Detailed error logging
                    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    user_id = message.from_user.id if message.from_user else "Unknown"
                    chat_id = message.chat.id if message.chat else "Unknown"
                    chat_username = (
                        f"@{message.chat.username}"
                        if message.chat.username
                        else "Özel Grup"
                    )
                    command = (
                        " ".join(message.command)
                        if hasattr(message, "command")
                        else message.text
                    )
                    error_trace = traceback.format_exc()
                    error_message = (
                        f"**Hata:** {type(e).__name__}\n"
                        f"**Tarih:** {date_time}\n"
                        f"**Sohbet ID:** {chat_id}\n"
                        f"**Sohbet Kullanıcı Adı:** {chat_username}\n"
                        f"**Kullanıcı ID:** {user_id}\n"
                        f"**Komut/Metin:** {command}\n"
                        f"**Geri izleme:**\n{error_trace}"
                    )
                    await client.send_message(config.LOG_GROUP_ID, error_message)
                    try:
                        await client.send_message(config.OWNER_ID[0], error_message)
                    except Exception:
                        pass

            handler = MessageHandler(wrapper, filters)
            self.handlers.append((handler, group))
            return func

        return decorator
