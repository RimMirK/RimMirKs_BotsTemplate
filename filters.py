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