import traceback
from telebot.asyncio_handler_backends import BaseMiddleware
from telebot.asyncio_handler_backends import CancelUpdate, SkipHandler

from translator import tr

class MessageMiddleware(BaseMiddleware):
    def __init__(self, bot, db):
        self.update_types = ['message']
        self.bot = bot
        self.db = db
        
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
                await self.bot.reply(message, _('rules.rules_not_confirmed', html=True))
                return CancelUpdate()
        
        if await self.db.is_registered(message.from_user.id):
            if await self.db.is_banned(message.from_user.id):
                if message.text and message.text.lower() not in ['/rules']:
                    return CancelUpdate()
        
        
    async def post_process(self, message, data, exception: Exception = None):
        
        _ = await tr(message)
            
        if exception:
            id = await self.db.add_error(''.join(traceback.format_exception(exception)), message.from_user.id)
            await self.bot.reply(message, _('errors.error_occurred', html=True, id=id))



class CallbackMiddleware(BaseMiddleware):
    def __init__(self, bot, db):
        self.update_types = ['callback_query']
        self.bot = bot
        self.db = db
        
    async def pre_process(self, callback, data):
        from translator import tr
        if not await self.db.is_registered(callback.from_user.id):
            await self.bot.answer_callback_query(callback.id, 'You are not registered. Please register first. Use /start command.', show_alert=True)
            
        if callback.data and not (callback.data.startswith('set_lang:') or callback.data in ['get_started', 'confirm_rules']):
            if not await self.db.is_rules_confirmed(callback.from_user.id):
                _ = await tr(callback)
                await self.bot.answer_callback_query(callback.id, _('rules.rules_not_confirmed', html=False), show_alert=True)
                return SkipHandler()
        
        if await self.db.is_banned(callback.from_user.id):
            _ = await tr(callback)
            await self.bot.answer_callback_query(callback.id, _('you_are_banned_inline'), show_alert=True)
            return CancelUpdate()
        
    async def post_process(self, callback, data, exception: Exception =None):
        from translator import tr
        _ = await tr(callback)
            
        if exception:
            id = await self.db.add_error(''.join(traceback.format_exception(exception)), callback.from_user.id)
            await self.bot.answer_callback_query(callback.id, _('errors.error_occurred', html=False, id=id), show_alert=True)
        
        # await bot.answer_callback_query(callback.id)


def setup_middlewares(bot, db):
    bot.setup_middleware(MessageMiddleware(bot, db))
    bot.setup_middleware(CallbackMiddleware(bot, db))