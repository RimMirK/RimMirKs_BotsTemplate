
import asyncio
from telebot.types import (
    InlineKeyboardMarkup as IM, InlineKeyboardButton as IB,
    ReplyKeyboardMarkup as RM, KeyboardButton as KB,
    CallbackQuery as C, Message, Message as M,
    CopyTextButton, ReplyKeyboardRemove as RKR
)

from cpytba import CustomAsyncTeleBot as Bot
from database import DB
from translator import get_text_translations, tr
from logging import Logger


async def main(bot: Bot, db: DB, logger: Logger):

    
    bot.add_command(-1, ['newsletter'], get_text_translations('cmd_desc.newsletter'), True)
    @bot.callback_query_handler(None, cdata='newsletter', is_admin=True)
    @bot.message_handler(['newsletter'], is_admin=True)
    async def _newsletter(obj: M | C):
        
        _ = await tr(obj)
        
        msg = obj if isinstance(obj, M) else obj.message
        await bot.state(obj, 'newsletter:message')
        if arg := (msg.text.split(maxsplit=1)[1] if len(msg.text.split()) >= 2 else ''):
            if '-important' in arg or '-i' in arg:
                imp = True
                await bot.reply(msg, _('newsletter.important_mode_enabled'))
                await bot.set_data(obj, important=True)
        else:
            imp = False
        
            await bot.set_data(obj, important=False)
    
        rm = IM()
        rm.add(IB(
            _('newsletter.switch_important_mode', on=not imp),
            callback_data='newsletter:toggle_important_mode')
        )
    
        await bot.reply(msg, _('newsletter.write_msg'), reply_markup=rm)
        
    
    @bot.callback_query_handler(None, c='newsletter:toggle_important_mode')
    async def _newsletter_toggle_important_mode(c: C):
        await bot.answer_callback_query(c.id)
        
        data = await bot.get_data(c)
        important = data['important']
        
        _ = await tr(c)
        
        if important:
            await bot.set_data(c, important=False)
            await bot.edit_message_reply_markup(
                c.message.chat.id, c.message.id,
                reply_markup=IM().add(IB(_("newsletter.switch_important_mode", on=True),
                callback_data='newsletter:toggle_important_mode'))
            )
        else:
            await bot.set_data(c, important=True)
            await bot.edit_message_reply_markup(
                c.message.chat.id, c.message.id,
                reply_markup=IM().add(IB(_("newsletter.switch_important_mode", on=False),
                callback_data='newsletter:toggle_important_mode'))
            )
        
    

        
    @bot.message_handler(state='newsletter:message')
    async def _newsletter_message(msg: M):
        _ = await tr(msg)
        
        await bot.set_data(msg, text=msg.html_text)
        await bot.reply(msg, 
            _("newsletter.send_one_media"),
            reply_markup=RM(True).add(KB(_("newsletter.skip"))), quote=True
        )
        await bot.state(msg, 'newsletter:media')
    
    
    @bot.message_handler(state='newsletter:media', content_types=['text', 'photo', 'video', 'animation'])
    async def _newsletter_media(msg: M):
        _ = await tr(msg)
        
        if msg.text and msg.text == _("newsletter.skip"):
            await bot.set_data(msg, file_type='nomedia', file_id=None)
        else:
            await bot.set_data(msg,
                file_type=(
                    'video' if msg.video
                    else (
                        'gif' if msg.animation
                        else 'photo'
                    )
                ),
                file_id=(msg.animation or msg.video or msg.photo[-1]).file_id
            )
        
        
        await bot.reply(msg, _('newsletter.add_links'))
        await bot.state(msg, 'newsletter:kb')
    
    @bot.message_handler(state='newsletter:kb')
    async def _newsletter_kb(msg: M):
        _ = await tr(msg)
        if msg.text and msg.text == _('newsletter.skip'):
            rm = None
        else:
            str_rows = msg.text.split('\n\n\n')
            rm = IM()
            for row in str_rows:
                btns = row.split('\n\n')
                buttuns = []
                for btn in btns:
                    buttuns.append(IB(*btn.split('\n')))   
                rm.add(*buttuns)
        
        await bot.set_data(msg, rm=rm)
        data = await bot.get_data(msg)
        text = data['text']
        file_id = data['file_id']
        file_type = data['file_type']
            
        params = dict(
            chat_id = msg.chat.id,
            caption = text,
            reply_markup = rm,
        )
        
        await bot.set_state(msg.from_user.id, "newsletter:confirm", msg.chat.id)
        
        await bot.reply(msg, _("newsletter.everything_ok"), reply_markup=RM(True).add(
            KB(f"✅"), KB(f"❌")
        ))
        
        match file_type:
            case 'gif':
                await bot.send_animation(**params, animation=file_id)
            case 'photo':
                await bot.send_photo(**params, photo=file_id)
            case 'video':
                await bot.send_video(**params, video=file_id)
            case 'nomedia':
                await bot.reply(msg, params['caption'], reply_markup=rm)

            
    @bot.message_handler(state='newsletter:confirm')
    async def _newsletter_confirm(msg: M):
        _ = await tr(msg)
        
        if msg.text == f'✅':
            await bot.reply(msg, _('newsletter.started'), reply_markup=RKR())
            data = await bot.get_data(msg)
            rm = data['rm']
            text = data['text']
            file_id = data['file_id']
            file_type = data['file_type']
            important = data['important']
                
            await bot.unstate(msg)
            
            errors = []
            c = 0
            s = 0
            
            async for user in db.get_users(important=important):
                c += 1
                params = dict(
                    chat_id = user['user_id'],
                    caption = text,
                    reply_markup = rm
                )
                
                try:
                    match file_type:
                        case 'gif':
                            await bot.send_animation(**params, animation=file_id)
                        case 'photo':
                            await bot.send_photo(**params, photo=file_id)
                        case 'video':
                            await bot.send_video(**params, video=file_id)
                        case 'nomedia':
                            await bot.send_message(user['user_id'], params['caption'], reply_markup=rm)
                    s += 1
                except Exception as ex:
                    errors.append((user['user_id'], ex))
                await asyncio.sleep(.025)
            
            await bot.reply(msg, _('newsletter.end', c=c, s=s, errors=errors))
            
        else:
            await bot.reply(msg, _('newsletter.cancelled'), reply_markup=RKR())
            await bot.unstate(msg)
            