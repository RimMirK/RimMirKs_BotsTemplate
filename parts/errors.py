#  RimMirK's Telegram Bot Template - Template for building Telegram bots
#  Copyright (C) 2025-present RimMirK
#
#  This file is part of the RimMirK's Telegram Bot Template.
#
#  Telegram Bot Template is free software: you can use, modify, and redistribute
#  it under the terms of the Apache License 2.0.
#
#  Use responsibly and respect the author's work.
#
#  LICENSE: See LICENSE file for full terms.
#  NOTICE: Dear developer — this file is written especially for you.
#          Take a moment to read it: inside is a message, acknowledgements,
#          and guidance that matter.
#
#  Repository: https://github.com/RimMirK/RimMirKs_TelegramBotTemplate
#  Telegram: @RimMirK



from telebot.types import (
    InlineKeyboardMarkup as IM, InlineKeyboardButton as IB,
    CallbackQuery as C, Message, Message as M,
    CopyTextButton
)

from cpytba import CustomAsyncTeleBot as Bot
from database import DB
from translator import get_text_translations, tr
from logging import Logger

async def main(bot: Bot, db: DB, logger: Logger):


    bot.add_command(0, ['get_error'], get_text_translations('cmd_decs.get_error'))
    @bot.message_handler(['get_error'], is_admin=True)
    async def _get_error(msg: M):
        _ = await tr(msg)
        try:
            eid = int(msg.text.split()[1])
        except:
            return await bot.reply(msg, _('errors.enter_value'))
        error = await db.get_error(eid)
        if not error:
            return await bot.reply(msg, _('errors.error_not_found').format(eid=eid))
        traceback = error.get('error', 'no traceback O_o')
        await bot.reply(msg, _(
            'errors.error_msg_fmt',
            eid=eid,
            user_id=error.get('user_id'),
            time=error.get('time'),
            time_str=error.get('time_str'),
            traceback=traceback,
        ))