
from telebot.types import (
    InlineKeyboardMarkup as IM, InlineKeyboardButton as IB,
    CallbackQuery as C, Message, Message as M,
    CopyTextButton
)

import requests

from cpytba import CustomAsyncTeleBot as Bot
from database import DB
from translator import get_text_translations, tr
from logging import Logger
from utils import paste

async def main(bot: Bot, db: DB, logger: Logger):

    
    bot.add_command(3, ['rules'], get_text_translations("rules_cmd_desc"))
    @bot.message_handler(['rules'])
    async def _rules(msg: Message):
        _ = await tr(msg)
        
        with open(_('rules_file', 'rules.en.md'), 'r', encoding='utf-8') as f:
            url = paste(f.read(), 'md')
        
        if not await db.is_rules_confirmed(msg.from_user.id):
            rm = IM()
            rm.add(IB(_('confirm_rules_btn'), callback_data='confirm_rules'))
            
            await bot.reply(msg, _('confirm_rules_text').format(rules_url=url), reply_markup=rm)
        else:
            await bot.reply(msg, _('rules_text').format(rules_url=url))


    @bot.callback_query_handler(cs='confirm_rules')
    async def _confirm_rules(c: C):
        await db.set_rules_confirmed(c.from_user.id)
        _ = await tr(c)
        
        
        rm = IM()
        rm.add(IB(_('get_started'), callback_data='get_started'))
        
        await bot.edit(c.message, _('rules_confirmed_text').format(rules_url=_('rules_url')), reply_markup=rm)