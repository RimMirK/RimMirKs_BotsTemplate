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


import traceback
from telebot.asyncio_handler_backends import BaseMiddleware
from telebot.asyncio_handler_backends import CancelUpdate, SkipHandler
from telebot.util import user_link

from translator import tr, jinja_env
from config import LOG_CHAT_ID, LOG_ERRORS, LOG_ERRORS_TEMPLATE

class MessageMiddleware(BaseMiddleware):
    def __init__(self, bot, db, logger):
        self.update_types = ['message']
        self.bot = bot
        self.db = db
        self.logger = logger
        
    async def pre_process(self, message, data):
        
        
        if message.text and not message.text.startswith('/start'):
            if not await self.db.is_registered(message.from_user.id):
                return await self.bot.reply(message, 'You are not registered. Please register first. Use /start command.')
                
        
        if not (
            message.text and 
            (
                (
                    message.text.lower() in ['/rules', '/get_started', '/menu']
                ) or (
                    message.text.startswith('/start')
                )
            )
        ):
            if not await self.db.is_rules_confirmed(message.from_user.id):
                _ = await tr(message)
                await self.bot.reply(message, await _('rules.rules_not_confirmed', html=True))
                return CancelUpdate()
        
        if await self.db.is_registered(message.from_user.id):
            if await self.db.is_banned(message.from_user.id):
                if message.text and message.text.lower() not in ['/rules']:
                    return CancelUpdate()
        
        
    async def post_process(self, message, data, exception: Exception = None):
        
        _ = await tr(message)
            
        if exception:
            tb = ''.join(traceback.format_exception(exception))
            id = await self.db.add_error(tb, message.from_user.id)
            await self.bot.reply(message, await _('errors.error_occurred', html=True, id=id))
            if LOG_ERRORS:
                error = await self.db.get_error(id)
                template = jinja_env.from_string(LOG_ERRORS_TEMPLATE)
                text = await template.render_async(
                    eid=id,
                    user_id=error.get('user_id'),
                    user_link=user_link(message.from_user),
                    time=error.get('time'),
                    time_str=error.get('time_str'),
                    traceback=tb,
                    is_callback=False
                )
                try:
                    await self.bot.send_message(LOG_CHAT_ID, text)
                except:
                    self.logger.error("Can't send error to log chat", exc_info=True)



class CallbackMiddleware(BaseMiddleware):
    def __init__(self, bot, db, logger):
        self.update_types = ['callback_query']
        self.bot = bot
        self.db = db
        self.logger = logger
        
    async def pre_process(self, callback, data):
        from translator import tr
        if not await self.db.is_registered(callback.from_user.id):
            await self.bot.answer_callback_query(callback.id, 'You are not registered. Please register first. Use /start command.', show_alert=True)
            
        if callback.data and not (callback.data.startswith('set_lang:') or callback.data in ['get_started', 'confirm_rules']):
            if not await self.db.is_rules_confirmed(callback.from_user.id):
                _ = await tr(callback)
                await self.bot.answer_callback_query(callback.id, await _('rules.rules_not_confirmed', html=False), show_alert=True)
                return SkipHandler()
        
        if await self.db.is_banned(callback.from_user.id):
            _ = await tr(callback)
            await self.bot.answer_callback_query(callback.id, await _('you_are_banned_inline'), show_alert=True)
            return CancelUpdate()
        
    async def post_process(self, callback, data, exception: Exception =None):
        from translator import tr
        _ = await tr(callback)
            
        if exception:
            tb = ''.join(traceback.format_exception(exception))
            id = await self.db.add_error(tb, callback.from_user.id)
            await self.bot.answer_callback_query(callback.id, await _('errors.error_occurred', html=False, id=id), show_alert=True)
            if LOG_ERRORS:
                error = await self.db.get_error(id)
                template = jinja_env.from_string(LOG_ERRORS_TEMPLATE)
                text = await template.render_async(
                    eid=id,
                    user_id=error.get('user_id'),
                    user_link=user_link(callback.from_user),
                    time=error.get('time'),
                    time_str=error.get('time_str'),
                    traceback=tb,
                    is_callback=True
                )
                try:
                    await self.bot.send_message(LOG_CHAT_ID, text)
                except:
                    self.logger.error("Can't send error to log chat", exc_info=True)
        
        # await bot.answer_callback_query(callback.id)


def setup_middlewares(bot, db, logger):
    bot.setup_middleware(MessageMiddleware (bot, db, logger.getChild( 'MessageMiddleware')))
    bot.setup_middleware(CallbackMiddleware(bot, db, logger.getChild('CallbackMiddleware')))