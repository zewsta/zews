#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the MIT License.
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import LOG, LOG_GROUP_ID
from YukkiMusic import app
from YukkiMusic.utils.database import (
    delete_served_chat,
    get_assistant,
    is_on_off,
)


@app.on_message(filters.new_chat_members)
async def on_bot_added(_, message):
    try:
        if not await is_on_off(LOG):
            return
        userbot = await get_assistant(message.chat.id)
        chat = message.chat
        for members in message.new_chat_members:
            if members.id == app.id:
                count = await app.get_chat_members_count(chat.id)
                username = (
                    message.chat.username if message.chat.username else "Özel Grup"
                )
                msg = (
                    f"**Müzik botu yeni gruba eklendi #Yeni_Grup**\n\n"
                    f"**Sohbet Adı:** {message.chat.title}\n"
                    f"**Sohbet ID:** {message.chat.id}\n"
                    f"**Sohbet Kullanıcı Adı:** @{username}\n"
                    f"**Sohbet Üye Sayısı:** {count}\n"
                    f"**Ekleyen:** {message.from_user.mention}"
                )
                await app.send_message(
                    LOG_GROUP_ID,
                    text=msg,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text=f"Ekleyen: {message.from_user.first_name}",
                                    user_id=message.from_user.id,
                                )
                            ]
                        ]
                    ),
                )
                if message.chat.username:
                    await userbot.join_chat(message.chat.username)
    except Exception:
        pass


@app.on_message(filters.left_chat_member)
async def on_bot_kicked(_, message: Message):
    try:
        if not await is_on_off(LOG):
            return
        userbot = await get_assistant(message.chat.id)

        left_chat_member = message.left_chat_member
        if left_chat_member and left_chat_member.id == app.id:
            remove_by = (
                message.from_user.mention if message.from_user else "Bilinmeyen Kullanıcı"
            )
            title = message.chat.title
            username = (
                f"@{message.chat.username}" if message.chat.username else "Özel Grup"
            )
            chat_id = message.chat.id
            left = (
                f"Bot gruptan çıkarıldı {title} #Gruptan_Çıkarıldı\n"
                f"**Sohbet Adı**: {title}\n"
                f"**Sohbet ID**: {chat_id}\n"
                f"**Sohbet Kullanıcı Adı**: {username}\n"
                f"**Çıkaran**: {remove_by}"
            )

            await app.send_message(
                LOG_GROUP_ID,
                text=left,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=f"Çıkaran: {message.from_user.first_name}",
                                user_id=message.from_user.id,
                            )
                        ]
                    ]
                ),
            )
            await delete_served_chat(chat_id)
            await userbot.leave_chat(chat_id)
    except Exception as e:
        pass
