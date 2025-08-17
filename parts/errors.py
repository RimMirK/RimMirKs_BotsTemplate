
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


    bot.add_command(0, ['get_error'], get_text_translations('get_error_cmd_decs'))
    @bot.message_handler(['get_error'], is_admin=True)
    async def _get_error(msg: M):
        _ = await tr(msg)
        try:
            eid = int(msg.text.split()[1])
        except:
            return await bot.reply(msg, _('enter_value'))
        error = await db.get_error(eid)
        if not error:
            return await bot.reply(msg, _('error_not_found').format(eid=eid))
        traceback = error.get('error', 'no traceback O_o')
        await bot.reply(msg, _(
            'error_msg_fmt',
            eid=eid,
            user_id=error.get('user_id'),
            time=error.get('time'),
            time_str=error.get('time_str'),
            traceback=traceback,
        ))