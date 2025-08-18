from typing import Any, List, Optional, Union
from asyncio import sleep
import logging
import time

from telebot.asyncio_helper import ApiTelegramException
from telebot.asyncio_storage import StatePickleStorage
from telebot.async_telebot import AsyncTeleBot
from telebot import types

from database import DB



class CustomAsyncTeleBot(AsyncTeleBot):
    logger: logging.Logger
    chats_last_send: dict
    me: types.User
    db: DB
    
    def __init__(self, *args, logger, db, **kwargs):
        self.logger = logger
        self.db = db
        self.chats_last_send = {}
        self.commands: dict[str, List[dict[str, str]]] = {}
        self.admin_commands: dict[str, List[dict[str, str]]] = {}
        
        def install_log():

            tb_logger = logging.getLogger('TeleBot')
            tb_logger.setLevel(logging.INFO)
            tb_logger.setLevel(logging.DEBUG)
            

            my_logger = logger
            my_logger.setLevel(logging.INFO)
            my_logger.setLevel(logging.DEBUG)
            
            import coloredlogs
            coloredlogs.install(logger=my_logger, level=my_logger.level, fmt='%(asctime)s %(name)s %(levelname)s: %(message)s')
            coloredlogs.install(logger=tb_logger, level=my_logger.level, fmt='%(asctime)s %(name)s %(levelname)s: %(message)s')

            fh = logging.FileHandler('main.log', encoding='utf-8')
            fh.setLevel(logging.INFO)
            fh.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
            
            my_logger.addHandler(fh)
            tb_logger.addHandler(fh)

        install_log()
        
        super().__init__(*args, **kwargs, colorful_logs=True, state_storage=StatePickleStorage(), parse_mode='HTML')

        
            

    def add_command(self,index: int, commands: List[str], description: dict[str, str], admin: bool = False, to_menu=True):
        return
        """
        Add command to menu in tg
        
        Args:
            index (int): index of command
            commands (List[str]): list of commands. First command will be shown in menu
            description (Dict[str, str]): dict {lang_code: description}
            admin (bool): pass True if command only for admins
            to_menu (bool): pass False to avoid adding command to menu
            
        """
        if admin:
            for lang, desc in description.items():
                if not self.admin_commands.get(lang):
                    self.admin_commands[lang] = []
                self.admin_commands[lang].append(dict(
                    index=index, commands=commands, description=desc, to_menu=to_menu
                ))
        else:
            for lang, desc in description.items():
                if not self.commands.get(lang):
                    self.commands[lang] = []
                self.commands[lang].append(dict(
                    index=index, commands=commands, description=desc, to_menu=to_menu
                ))

    async def _set_me(self):
        self.me = await self.get_me()
     
     

    async def reply(
        self,
        message:                     types.Message,
        text:                        str,
        parse_mode:                  Optional[str]=None, 
        entities:                    Optional[List[types.MessageEntity]]=None,
        disable_web_page_preview:    Optional[bool]=None, 
        disable_notification:        Optional[bool]=None, 
        protect_content:             Optional[bool]=None,
        allow_sending_without_reply: Optional[bool]=None,
        reply_markup:                Optional[Union[
                                        types.InlineKeyboardMarkup, types.ReplyKeyboardMarkup, 
                                        types.ReplyKeyboardRemove, types.ForceReply
                                     ]]=None,
        reply_to_message_id:         Optional[int]=None,
        reply_parameters:            Optional[types.ReplyParameters]=None,
        timeout:                     Optional[int]=None,
        quote:                       Optional[bool]=False,
        send_limited:                Optional[bool]=False,
        antiflood:                   Optional[bool]=True,
    ) -> types.Message:
        """
        Reply to message
        
        - pass `quote=True` to reply as reply
        - pass `send_limited=True` to send messages with interval to avoid flood wait
        - pass `antiflood=False` to disable auto resend message after getting flood wait
        """
        args = dict(
            chat_id=message.chat.id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_parameters=(
                reply_parameters if reply_parameters else (
                    types.ReplyParameters(
                        message_id=reply_to_message_id,
                        chat_id=message.chat.id,
                        allow_sending_without_reply=allow_sending_without_reply
                    ) if reply_to_message_id else (
                        types.ReplyParameters(message_id=message.id, chat_id=message.chat.id, allow_sending_without_reply=False)
                        if quote else None
                    )
                )
            ),
            reply_markup=reply_markup,
            timeout=timeout,
            message_thread_id=message.message_thread_id if not quote and message.is_topic_message else None
        )
        if send_limited:
            for i in range(30):
                try:
                    return await self.send_limited(args['chat_id'], self.send_message, **args)
                except ApiTelegramException as ex:
                    if ex.error_code == 429:
                        self.logger.warning(f"FLOOD_WAIT in reply {i+1} try {ex.result_json['parameters']['retry_after']} sec")
                        await sleep(ex.result_json['parameters']['retry_after'])
                    else:
                        raise
            else:
                return await self.send_limited(self.send_message, **args) # type: ignore
        else:
            if antiflood:
                for i in range(4):
                    try:
                        return await self.send_message(**args, )
                    except ApiTelegramException as ex:
                        if ex.error_code == 429:
                            self.logger.warning(f"FLOOD_WAIT in reply {i+1} try {ex.result_json['parameters']['retry_after']} sec")
                            await sleep(ex.result_json['parameters']['retry_after'])
                        else:
                            raise
            else:
                return await self.send_message(**args)
        
    async def edit(
        self,
        message: types.Message,
        text: str,
        reply_markup: types.InlineKeyboardMarkup=None,
        inline_message_id: str=None, 
        parse_mode: str=None,
        entities: List[types.MessageEntity]=None,
        disable_web_page_preview: bool=None,
        link_preview_options: types.LinkPreviewOptions=None,
        **_
    ) -> Union[types.Message, bool]:
        """
        Edit message or caption
        """
        params = dict(
            chat_id = message.chat.id,
            message_id=message.id,
            inline_message_id = inline_message_id,
            parse_mode = parse_mode,
            reply_markup = reply_markup,
        )
        if message.text:
            return await self.edit_message_text(**params, text=text, entities=entities,
            disable_web_page_preview = disable_web_page_preview, 
            link_preview_options = link_preview_options,)
        else:
            return await self.edit_message_caption(**params, caption=text, caption_entities=entities)
        
    async def delete(self, message: types.Message, /, timeout: int = None):
        """
        delete message
        """
        return await self.delete_message(message.chat.id, message.id, timeout=timeout)

    async def answer(
            self,
            obj: types.CallbackQuery | types.Message,
            text: str,
            reply_markup: types.InlineKeyboardMarkup | types.ReplyKeyboardMarkup |
                          types.ReplyKeyboardRemove  | types.ForceReply = None,
            **kwargs
        ):
        """
        Reply or edit message
        """
        return await (self.reply if isinstance(obj, types.Message) else self.edit)(
               obj if isinstance(obj, types.Message) else obj.message,
               text, reply_markup=reply_markup, **kwargs
        )

    async def send_limited(self, _chat_id, func, /, *args, **kwargs):
        # @seeklay thanks a lot for this feature
        self.logger.debug(f'send_limited, {_chat_id!r}, {func!r}')
        cur, last = (time.time(), self.chats_last_send.get(_chat_id, 3))
        if cur - last >= 3:
            self.chats_last_send[_chat_id] = cur 
            self.logger.debug(f'{self.chats_last_send = !r}')
            r = await func(*args, **kwargs)
            return r
        else:
            s = 3 - (cur - last)
            self.logger.debug(f'sleep {s}s')
            await sleep(s)
            return await self.send_limited(_chat_id, func, *args, **kwargs)
    
    async def state(self, obj: types.Message | types.CallbackQuery, state: str, **_params):
        """
        set state by Message or CallbackQuery
        """
        message = obj.message if hasattr(obj, 'message') else obj
        params = dict(
            user_id=obj.from_user.id,
            state=state,
            chat_id=message.chat.id if message.chat else None,
            business_connection_id=message.business_connection_id or None,
            message_thread_id=message.message_thread_id or None,
            bot_id=self.user.id,
        )
        params.update(**_params)
        await self.set_state(**params)
    
    async def set_data(self, obj, _params=None, **data):
        """
        set state data by Message or CallbackQuery
        """
        message = obj.message if hasattr(obj, 'message') else obj
        params = dict(
            user_id=obj.from_user.id,
            chat_id=message.chat.id if message.chat else None,
            business_connection_id=message.business_connection_id or None,
            message_thread_id=message.message_thread_id or None,
            bot_id=self.user.id,
        )
        if _params:
            params.update(**_params)
        async with self.retrieve_data(**params) as d: # type: ignore
            d.update(**data)

    async def unstate(self, obj, **_params):
        """
        set delete state by Message or CallbackQuery
        """
        message = obj.message if hasattr(obj, 'message') else obj
        params = dict(
            user_id=obj.from_user.id,
            chat_id=message.chat.id if message.chat else None,
            business_connection_id=message.business_connection_id or None,
            message_thread_id=message.message_thread_id or None,
            bot_id=self.user.id,
        )
        params.update(**_params)
        await self.delete_state(**params)
    
    async def get_data(self, obj, **_params):
        """
        get state data by Message or CallbackQuery
        """
        message = obj.message if hasattr(obj, 'message') else obj
        params = dict(
            user_id=obj.from_user.id,
            chat_id=message.chat.id if message.chat else None,
            business_connection_id=message.business_connection_id or None,
            message_thread_id=message.message_thread_id or None,
            bot_id=self.user.id,
        )
        params.update(**_params)
        async with self.retrieve_data(**params) as data: # type: ignore
            return data
    