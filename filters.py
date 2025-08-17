
from telebot.asyncio_filters import StateFilter, AdvancedCustomFilter
from telebot.types import Message, CallbackQuery

from translator import tr



class CallbackDataFilter(AdvancedCustomFilter):
    key = 'c'
    
    async def check(self, callback_query, cdata) -> bool:
        return callback_query.data == cdata

class CallbackDataStartsWithFilter(AdvancedCustomFilter):
    key = 'cs'
    
    async def check(self, callback_query, cdata) -> bool:
        return callback_query.data.startswith(cdata)
    
class IsAdminFilter(AdvancedCustomFilter):
    key = 'is_admin'
    
    def __init__(self, bot, db, *args, **kwargs) -> None:
        self.db = db
        self.bot = bot
        super().__init__(*args, **kwargs)


    async def check(self, obj, *_) -> bool:
        if not await self.db.is_admin(obj.from_user.id):
            _ = await tr(obj)
            if isinstance(obj, Message):
                await self.bot.reply(obj, _('you_are_not_admin'), quote=True)
            elif isinstance(obj, CallbackQuery):
                await self.bot.answer_callback_query(obj.id, _('you_are_not_admin'), True)
            return False
        return True


def set_filters(bot, db):
    bot.add_custom_filter(CallbackDataFilter())
    bot.add_custom_filter(StateFilter(bot=bot))
    bot.add_custom_filter(CallbackDataStartsWithFilter())
    bot.add_custom_filter(IsAdminFilter(bot=bot, db=db))