
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

    bot.add_command(0, ['ban'], get_text_translations("cmd_desc.ban"), admin=True)
    @bot.message_handler(['ban'], is_admin=True)
    async def _ban(msg: M):
        _ = await tr(msg)
        try:
            user_id = int(msg.text.split()[1])
            assert await db.get_user(user_id)
        except IndexError:

            r = msg.reply_to_message

            if not r or not await db.get_user(r.from_user.id):
                return await bot.reply(msg, _('ban.input_value'))
            
            user_id = r.from_user.id
        
        except (ValueError, AssertionError):
            return await bot.reply(msg, _('ban.input_value'))


        await db.ban_user(user_id)

        await bot.reply(msg, _('ban.user_banned').format(user_id=user_id))
        

    bot.add_command(0, ['unban'], get_text_translations("cmd_desc.unban"), admin=True)
    @bot.message_handler(['unban'], is_admin=True)
    async def _unban(msg: M):
        _ = await tr(msg)
        try:
            user_id = int(msg.text.split()[1])
            assert await db.get_user(user_id)
        except IndexError:

            r = msg.reply_to_message

            if not r or not await db.get_user(r.from_user.id):
                return await bot.reply(msg, _('ban.input_value'))
            
            user_id = r.from_user.id
        
        except ValueError | AssertionError:
            return await bot.reply(msg, _('ban.input_value'))


        await db.unban_user(user_id)

        await bot.reply(msg, _('bane.user_unbanned').format(user_id=user_id))
        
