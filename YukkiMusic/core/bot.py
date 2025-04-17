#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the MIT License.
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#
import uvloop

uvloop.install()

import asyncio
import importlib.util
import os
import traceback
from datetime import datetime
from functools import wraps

#import pyromod.listen #noqa
from pyrogram import Client, StopPropagation, errors
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatSendMediaForbidden,
    ChatSendPhotosForbidden,
    ChatWriteForbidden,
    FloodWait,
    MessageIdInvalid,
    MessageNotModified,
)
from pyrogram.handlers import MessageHandler
from pyrogram.types import (
    BotCommand,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
    BotCommandScopeChatMember,
)

import config

from ..logging import LOGGER


class YukkiBot(Client):
    def __init__(self, *args, **kwargs):
        LOGGER(__name__).info("Bot Başlatılıyor...")

        super().__init__(*args, **kwargs)
        self.loaded_plug_counts = 0

    def on_message(self, filters=None, group=0):
        def decorator(func):
            @wraps(func)
            async def wrapper(client, message):
                try:
                    await func(client, message)
                except FloodWait as e:
                    LOGGER(__name__).warning(
                        f"FloodWait: {e.value} Saniye Boyunca Bekle."
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
                    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    user_id = message.from_user.id if message.from_user else "Unknown"
                    chat_id = message.chat.id if message.chat else "Unknown"
                    chat_username = (
                        f"@{message.chat.username}"
                        if message.chat.username
                        else "Özel Grup"
                    )
                    command = message.text
                    error_trace = traceback.format_exc()
                    error_message = (
                        f"<b>Hata:</b> {type(e).__name__}\n"
                        f"<b>Tarih:</b> {date_time}\n"
                        f"<b>Sohbet ID:</b> {chat_id}\n"
                        f"<b>Sohbet Kullanıcı Adı:</b> {chat_username}\n"
                        f"<b>Kullanıcı ID:</b> {user_id}\n"
                        f"<b>Komut/Metin:</b>\n<pre language='python'><code>{command}</code></pre>\n\n"
                        f"<b>Geri İzleme:</b>\n<pre language='python'><code>{error_trace}</code></pre>"
                    )
                    await self.send_message(config.LOG_GROUP_ID, error_message)
                    try:
                        await self.send_message(config.OWNER_ID[0], error_message)
                    except Exception:
                        pass

            handler = MessageHandler(wrapper, filters)
            self.add_handler(handler, group)
            return func

        return decorator

    async def start(self):
        await super().start()
        get_me = await self.get_me()
        self.username = get_me.username
        self.id = get_me.id
        self.name = get_me.full_name
        self.mention = get_me.mention

        try:
            await self.send_message(
                config.LOG_GROUP_ID,
                text=(
                    f"<u><b>{self.mention} Bot Başlatıldı :</b></u>\n\n"
                    f"ID : <code>{self.id}</code>\n"
                    f"İsim : {self.name}\n"
                    f"Kullanıcı Adı : @{self.username}"
                ),
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "Bot günlük grubuna erişemedi. Botun eklendiğinden ve yönetici olarak yükseltildiğinden emin olun."
            )
            LOGGER(__name__).error("Hata ayrıntıları:", exc_info=True)
            exit()
        if config.SET_CMDS:
            try:
                await self._set_default_commands()
            except Exception as e:
                LOGGER(__name__).warning("Komutlar ayarlanamadı:", exc_info=True)

        try:
            a = await self.get_chat_member(config.LOG_GROUP_ID, "me")
            if a.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error("Lütfen botu logger grubunda yönetici olarak tanıtın")
                exit()
        except Exception:
            pass
        LOGGER(__name__).info(f"Müzik Botu {self.name} Olarak Başlatıldı.")

    async def _set_default_commands(self):
        private_commands = [
            BotCommand("start", "🎧 Botu Başlatın"),
            BotCommand("yardim", "📖 Yardım Menüsünü Açın"),
        ]
        group_commands = [
            BotCommand("oynat", "▶️ İstediğiniz Müziği Oynatın"),
            BotCommand("voynat", "🎦 İstediğiniz Videoyu Oynatın"), 
            BotCommand("atla", "⏯️ Çalan Müziği Atlayın"),
            BotCommand("duraklat", "⏸️ Çalan Müziği Duraklatın"),
            BotCommand("devam", "⏺️ Duraklatılan Müziği Devam Ettirin"),
            BotCommand("son", "⏹️ Çalan Müziği Sonlandırın"),
            BotCommand("karistir", "🔀 Sıradaki Müzikleri Karıştırın"),
            BotCommand("playmode", "⏏️ Oynatma Modunu Ayarlayın"),
            BotCommand("reload", "❤️‍🔥 Yönetici Listesini Güncelleyin"),
            BotCommand("indir", "⬇️ Belirtilen Müziği/Videoyu İndirin"),
            BotCommand("restart", "🚀 Botu Yeniden Başlatın"),
            BotCommand("ayarlar", "⚙️ Bot Ayarlarını Açın"),
        ]
        admin_commands = [
            BotCommand("oynat", "▶️ İstediğiniz Müziği Oynatın"),
            BotCommand("voynat", "🎦 İstediğiniz Videoyu Oynatın"), 
            BotCommand("atla", "⏯️ Çalan Müziği Atlayın"),
            BotCommand("duraklat", "⏸️ Çalan Müziği Duraklatın"),
            BotCommand("devam", "⏺️ Duraklatılan Müziği Devam Ettirin"),
            BotCommand("son", "⏹️ Çalan Müziği Sonlandırın"),
            BotCommand("karistir", "🔀 Sıradaki Müzikleri Karıştırın"),
            BotCommand("playmode", "⏏️ Oynatma Modunu Ayarlayın"),
            BotCommand("reload", "❤️‍🔥 Yönetici Listesini Güncelleyin"),
            BotCommand("indir", "⬇️ Belirtilen Müziği/Videoyu İndirin"),
            BotCommand("restart", "🚀 Botu Yeniden Başlatın"),
            BotCommand("ayarlar", "⚙️ Bot Ayarlarını Açın"),
        ]

        owner_commands = [
            BotCommand("update", "🔃 Botu Güncelle"),
            BotCommand("restart", "🔄 Botu Yeniden Başlat"),
            BotCommand("logs", "📳 Logları Al"),
            BotCommand("export", "📤 Tüm MongoDB Verilerini Dışa Aktar"),
            BotCommand("import", "📥 Tüm Verileri MongoDB'ye Aktar"),
            BotCommand("addsudo", "✅ Bir Kullanıcıyı Sudo Listesine Ekle"),
            BotCommand("delsudo", "❎ Bir Kullanıcıyı Sudo Listesinden Çıkar"),
            BotCommand("sudolist", "📄 Tüm Sudo Kullanıcılarını Listele"),
            BotCommand("log", "📋 Bot Loglarını Al"),
            BotCommand("getvar", "📚 Belirli Bir Var Al"),
            BotCommand("delvar", "🗳️ Belirli Bir Var Sil"),
            BotCommand("setvar", "✏️ Belirli Bir Var Ayarla"),
            BotCommand("usage", "💡 Dyno'yu Kullanma Hakkında Bilgi Edin"),
            BotCommand("maintenance", "🛠️ Bakım Modunu Aç Veya Kapat"),
            BotCommand("logger", "🚪 Logu Aç Veya Kapat"),
            BotCommand("block", "🚫 Bir Kullanıcıyı Engelle"),
            BotCommand("unblock", "✔️ Bir Kullanıcının Engelini Kaldır"),
            BotCommand("blacklist", "➕ Kara Listeye Sohbet Ekle"),
            BotCommand("whitelist", "➖ Beyaz Listeye Sohbet Ekle"),
            BotCommand("blacklisted", "📳 Kara Listeye Alınmış Tüm Sohbetleri Listele"),
            BotCommand("autoend", "🔇 Sesli Sohbet İçin Otomatik Sonlandırmayı Aç Veya Kapat"),
            BotCommand("reboot", "✨ Bota Reboot At"),
            BotCommand("restart", "🕹️ Botu Yeniden Başlatın"),
        ]

        await self.set_bot_commands(
            private_commands, scope=BotCommandScopeAllPrivateChats()
        )
        await self.set_bot_commands(
            group_commands, scope=BotCommandScopeAllGroupChats()
        )
        await self.set_bot_commands(
            admin_commands, scope=BotCommandScopeAllChatAdministrators()
        )

        LOG_GROUP_ID = (
            f"@{config.LOG_GROUP_ID}"
            if isinstance(config.LOG_GROUP_ID, str)
            and not config.LOG_GROUP_ID.startswith("@")
            else config.LOG_GROUP_ID
        )

        for owner_id in config.OWNER_ID:
            try:
                await self.set_bot_commands(
                    owner_commands,
                    scope=BotCommandScopeChatMember(
                        chat_id=LOG_GROUP_ID, user_id=owner_id
                    ),
                )
                await self.set_bot_commands(
                    private_commands + owner_commands,
                    scope=BotCommandScopeChat(chat_id=owner_id),
                )
            except Exception:
                pass

    def load_plugin(self, file_path: str, base_dir: str, utils=None):
        file_name = os.path.basename(file_path)
        module_name, ext = os.path.splitext(file_name)
        if module_name.startswith("__") or ext != ".py":
            return None

        relative_path = os.path.relpath(file_path, base_dir).replace(os.sep, ".")
        module_path = f"{os.path.basename(base_dir)}.{relative_path[:-3]}"

        spec = importlib.util.spec_from_file_location(module_path, file_path)
        module = importlib.util.module_from_spec(spec)
        module.logger = LOGGER(module_path)
        module.app = self
        module.Config = config

        if utils:
            module.utils = utils

        try:
            spec.loader.exec_module(module)
            self.loaded_plug_counts += 1
        except Exception as e:
            LOGGER(__name__).error(
                f"{module_path} Yüklenemedi: {e}\n\n", exc_info=True
            )
            exit()

        return module

    def load_plugins_from(self, base_folder: str):
        base_dir = os.path.abspath(base_folder)
        utils_path = os.path.join(base_dir, "utils.py")
        utils = None

        if os.path.exists(utils_path) and os.path.isfile(utils_path):
            try:
                spec = importlib.util.spec_from_file_location("utils", utils_path)
                utils = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(utils)
            except Exception as e:
                LOGGER(__name__).error(
                    f"'utils' Modülü Yüklenemedi: {e}", exc_info=True
                )

        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".py") and not file == "utils.py":
                    file_path = os.path.join(root, file)
                    mod = self.load_plugin(file_path, base_dir, utils)
                    yield mod

    async def run_shell_command(self, command: list):
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        return {
            "returncode": process.returncode,
            "stdout": stdout.decode().strip() if stdout else None,
            "stderr": stderr.decode().strip() if stderr else None,
        }
