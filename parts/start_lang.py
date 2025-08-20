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



import time
from telebot.types import (
    InlineKeyboardMarkup as IM, InlineKeyboardButton as IB,
    CallbackQuery as C, Message, Message as M,
    CopyTextButton
)

from cpytba import CustomAsyncTeleBot as Bot
from database import DB
from translator import get_text_translations, tr, get_langs, get_lang_title, get_translator
from logging import Logger
from utils import format_date



async def main(bot: Bot, db: DB, logger: Logger):

    # bot.add_command(1, ['start'], get_text_translations("cmd_desc.start"))
    @bot.message_handler(['start'])
    async def _start(msg: Message):
        await db.bootstrap()
        await db.register(msg.from_user.id)
        _ = await tr(msg)
        if len(msg.text.split()) == 1:
            rm = IM()
            btns = []
            for lang in get_langs():
                if len(lang) <= 3:
                    btns.append(IB(get_lang_title(lang), callback_data=f'set_lang:start:{lang}'))
            rm.add(*btns, row_width=3)

            rm.add(IB(await _('start_lang.get_started'), callback_data='get_started'))

            await bot.reply(msg, await _('start_lang.start_text'), reply_markup=rm)
        else:
            args = msg.text.split()[1].split('_')
            match args:
                case __:
                    return await bot.reply(msg, await _('start_lang.error_start_text'))


    @bot.callback_query_handler(cs='set_lang')
    async def _set_lang(c: C):
        lang = c.data.split(':')[-1]
        additional = c.data.split(':')[-2]
        await db.set_lang(c.from_user.id, lang)
        _ = get_translator(lang)
        if additional == 'start':
            await bot.answer_callback_query(c.id, await _('start_lang.lang_set_to'))
            rm = IM()
            btns = []
            for lang in get_langs():
                if len(lang) <= 3:
                    btns.append(IB(get_lang_title(lang), callback_data=f'set_lang:start:{lang}'))
            rm.add(*btns, row_width=3)
            
            rm.add(IB(await _('start_lang.get_started'), callback_data='get_started'))

            await bot.edit(c.message, await _('start_lang.start_text'), reply_markup=rm)
        elif additional == 'set_lang':
            await bot.answer_callback_query(c.id, await _('start_lang.lang_set_to'), True)

    bot.add_command(4, ['lang', 'language'], get_text_translations("cmd_desc.lang"))
    @bot.message_handler(['lang', 'language'])
    async def _lang(msg):
        _ = await tr(msg)

        rm = IM()
        btns = []
        langs = []
        for lang in get_langs():
            if len(lang) <= 3:
                btns.append(IB(get_lang_title(lang), callback_data=f'set_lang:{lang}'))
                langs.append(get_translator(lang)('start_lang.choose_lang'))
        rm.add(*btns, row_width=3)


        await bot.reply(msg, " · ".join(langs), reply_markup=rm)