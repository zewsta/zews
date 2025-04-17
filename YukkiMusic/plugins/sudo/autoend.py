#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the MIT License.
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#

from strings import command
from YukkiMusic import app
from YukkiMusic.misc import SUDOERS
from YukkiMusic.utils.database import autoend_off, autoend_on


@app.on_message(command("AUTOEND_COMMAND") & SUDOERS)
async def auto_end_stream(client, message):
    usage = "**Kullanım:**\n\n/autoend [enable|disable]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "enable":
        await autoend_on()
        await message.reply_text(
            "Otomatik sonlandırma etkin.\n\nBot, bir uyarı mesajı ile şarkı dinlenmiyorsa 30 saniye sonra otomatik olarak sesli sohbetten ayrılacak."
        )
    elif state == "disable":
        await autoend_off()
        await message.reply_text("Otomatik sonlandırma kapalı.")
    else:
        await message.reply_text(usage)
