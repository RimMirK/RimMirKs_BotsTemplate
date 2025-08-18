
from telebot.types import (
    InlineKeyboardMarkup as IM, InlineKeyboardButton as IB,
    CallbackQuery as C, Message, Message as M,
    CopyTextButton, ReplyKeyboardRemove as RKR
)

from cpytba import CustomAsyncTeleBot as Bot
from database import DB
from translator import get_text_translations, tr
from logging import Logger

from utils.utils import paste

async def main(bot: Bot, db: DB, logger: Logger):

    bot.add_command(2, ['menu', 'get_started'], get_text_translations("cmd_desc.menu"))
    @bot.callback_query_handler(cs='get_started')
    @bot.message_handler(['get_started', 'menu'])
    @bot.message_handler(func=lambda msg: msg.text in get_text_translations('back.back_to_menu_btn').values())
    async def _get_started(obj: C|M):
        c = obj if isinstance(obj, C) else None
        m = obj if isinstance(obj, M) else c.message
        
        if isinstance(obj, M):
            lm = await bot.reply(m, 'loading...', reply_markup=RKR())
            await bot.delete(lm)

        
        _ = await tr(obj)
        
        if not await db.is_rules_confirmed(obj.from_user.id):
            
            rm = IM()
            rm.add(IB(_('rules.confirm_rules_btn'), callback_data='confirm_rules'))
            
            with open("rules/"+_('rules_file', 'rules.en.md'), 'r', encoding='utf-8') as f:
                url = paste(f.read(), 'md')
        

            if c:
                await bot.edit(c.message, _('rules.confirm_rules_text').format(rules_url=url), reply_markup=rm)
            elif m:
                await bot.reply(m, _('rules.confirm_rules_text').format(rules_url=url), reply_markup=rm)
            else:
                raise ValueError("Neither CallbackQuery nor Message provided.")

            return
        
        
        text = _('menu.menu_text',
            user_id=obj.from_user.id,
        )  
        
        rm = IM()
        rm.add(IB(_('menu.copy_my_id_btn'), copy_text=CopyTextButton(obj.from_user.id)))
        
        if c:
            await bot.edit(m, text, reply_markup=rm)
        elif m:
            await bot.reply(m, text, reply_markup=rm)
            
        else:
            raise ValueError("Neither CallbackQuery nor Message provided.")