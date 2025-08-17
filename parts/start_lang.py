
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

    bot.add_command(1, ['start'], get_text_translations("start_cmd_desc"))
    @bot.message_handler(['start'])
    async def _start(msg: Message):
        logger.info('start command received')
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

            rm.add(IB(_('get_started'), callback_data='get_started'))

            await bot.reply(msg, _('start_text'), reply_markup=rm)
        else:
            args = msg.text.split()[1].split('_')
            match args:
                case 'check', token:
                    check = await db.get_check(token)
                    if not check:
                        return await bot.reply(msg, _("check_not_found"))
                    if check['type'] == 'topup':
                        if user_id := check['user_id']:
                            if user_id != msg.from_user.id:
                                return await bot.reply(msg, _('not_your_check'))
                        if check['used']:
                            return await bot.reply(msg, _("check_used"))
                        await db.add_balance(msg.from_user.id, check['amount'])
                        used_time = await db.set_check_used(token)
                        await bot.reply(
                            msg, _("check_added_balance").format(
                                amount=f"{check['amount']:,.2f}",
                                time=format_date(used_time)+f" [{used_time}]",
                                token=repr(token)
                            )
                        )
                    else:
                        raise ValueError(f'unknown check type: {check["type"]!r}')
                case __:
                    return await bot.reply(msg, _('error_start_text'))


    @bot.callback_query_handler(cs='set_lang')
    async def _set_lang(c: C):
        lang = c.data.split(':')[-1]
        additional = c.data.split(':')[-2]
        await db.set_lang(c.from_user.id, lang)
        _ = get_translator(lang)
        if additional == 'start':
            await bot.answer_callback_query(c.id, _('lang_set_to'))
            rm = IM()
            btns = []
            for lang in get_langs():
                if len(lang) <= 3:
                    btns.append(IB(get_lang_title(lang), callback_data=f'set_lang:start:{lang}'))
            rm.add(*btns, row_width=3)
            
            rm.add(IB(_('get_started'), callback_data='get_started'))

            await bot.edit(c.message, _('start_text'), reply_markup=rm)
        elif additional == 'set_lang':
            await bot.answer_callback_query(c.id, _('lang_set_to'), True)

    bot.add_command(4, ['lang', 'language'], get_text_translations("lang_cmd_desc"))
    @bot.message_handler(['lang', 'language'])
    async def _lang(msg):
        _ = await tr(msg)

        rm = IM()
        btns = []
        langs = []
        for lang in get_langs():
            if len(lang) <= 3:
                btns.append(IB(get_lang_title(lang), callback_data=f'set_lang:{lang}'))
                langs.append(get_translator(lang)('choose_lang'))
        rm.add(*btns, row_width=3)


        await bot.reply(msg, " · ".join(langs), reply_markup=rm)