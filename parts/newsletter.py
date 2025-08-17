
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

from utils.utils import paste

async def main(bot: Bot, db: DB, logger: Logger):

    
    @bot.callback_query_handler(None, cdata='newsletter', is_admin=True)
    @bot.message_handler(['newsletter'], is_admin=True)
    async def _newsletter(obj: M | C):
        
        _ = await tr(obj)
        
        msg = obj if isinstance(obj, M) else obj.message
        await bot.set_state(obj.from_user.id, 'newsletter:message', msg.chat.id)
        if arg := (msg.text.split(maxsplit=1)[1] if len(msg.text.split()) >= 2 else ''):
            if '-important' in arg or '-i' in arg:
                imp = True
                await bot.reply(msg, _('important_mode_enabled'))
                await bot.set_data(obj, important=True)
        else:
            imp = False
        
            await bot.set_data(obj, important=False)
    
        rm = IM()
        rm.add(IB(
            _('switch_important_mode', on=imp),
            callback_data='newsletter:toggle_important_mode')
        )
    
        await bot.reply(msg, _('write_msg'), reply_markup=rm)
        
    
    @bot.callback_query_handler(None, c='newsletter:toggle_important_mode')
    async def _newsletter_toggle_important_mode(c: C):
        await bot.answer_callback_query(c.id)
        
        data = await bot.get_data(c)
        important = data['important']
        
        _ = await tr(c)
        
        if important:
            await bot.set_data(c, important=True)
            await bot.edit_message_reply_markup(
                c.message.chat.id, c.message.id,
                reply_markup=IM().add(IB(_("switch_important_mode", on=False),
                callback_data='newsletter:toggle_important_mode'))
            )
        else:
            await bot.set_data(c, important=False)
            await bot.edit_message_reply_markup(
                c.message.chat.id, c.message.id,
                reply_markup=IM().add(IB(_("switch_important_mode", on=False),
                callback_data='newsletter:toggle_important_mode'))
            )
        
    

        
    @bot.message_handler(state='newsletter:message')
    async def _newsletter_message(msg: M):
        async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
            data['text'] = msg.html_text
        await bot.reply(msg, 
            'Отлично! Теперь отправь <u>одну</u> картинку, видео или гифку',
            reply_markup=RM(True).add(KB("Пропустить")), quote=True
        )
        await bot.set_state(msg.from_user.id, 'newsletter:media', msg.chat.id)
    
    
    @bot.message_handler(state='newsletter:media', content_types=['text', 'photo', 'video', 'animation'])
    async def _newsletter_media(msg: M):
        if msg.text and msg.text == 'Пропустить':
            async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
                data['file_type'] = 'nomedia'
                data['file_id'] = None
        else:
            async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
                data['file_type'] = (
                    'video' if msg.video
                    else (
                        'gif' if msg.animation
                        else 'photo'
                    )
                )
                data['file_id'] = (msg.animation or msg.video or msg.photo[-1]).file_id
        
        
        await bot.reply(msg, 'добавьте ссылку(и)')
        await bot.set_state(msg.from_user.id, 'newsletter:kb', msg.chat.id)
    
    @bot.message_handler(state='newsletter:kb')
    async def _newsletter_kb(msg: M):
        if msg.text and msg.text == 'Пропустить':
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
        
        async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
            data['rm'] = rm
            text = data['text']
            file_id = data['file_id']
            file_type = data['file_type']
            
        user = await db.get_user(msg.from_user.id)
            
        params = dict(
            chat_id = msg.chat.id,
            caption = text,
            reply_markup = rm,
        )
        
        await bot.set_state(msg.from_user.id, "newsletter:confirm", msg.chat.id)
        
        await bot.reply(msg, "Все так, как ты хотел?", reply_markup=RM(True).add(
            KB(f"✅ Да"), KB(f"Нет ❌")
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
        if msg.text == f'✅ Да':
            await bot.reply(msg, "Пошла жара", reply_markup=RKR())
            async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
                rm = data['rm']
                text = data['text']
                file_id = data['file_id']
                file_type = data['file_type']
                important = data['important']
                
            await bot.delete_state(msg.from_user.id, msg.chat.id)
            
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
            
            await bot.reply(msg, f"Рассылка завершена!\nотправлено {c} юзерам\nуспешно дошло до {s} юзеров\n\nОшибок: {len(errors)}\n" + '\n'.join(f"<code>{user}</code>: {ex.description or str(ex)}" for user, ex in errors))
            
        else:
            await bot.reply(msg, "Рассылка отменена", reply_markup=RKR())
            await bot.delete_state(msg.from_user.id, msg.chat.id)
            