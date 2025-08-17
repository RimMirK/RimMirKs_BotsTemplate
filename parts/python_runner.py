
import time
from telebot.types import (
    Message as M
)

from cpytba import CustomAsyncTeleBot as Bot
from database import DB
from logging import Logger
from telebot.types import Message as M
from telebot.util import extract_arguments
from database import DB
import asyncio, time, sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from traceback import format_exc, print_exc
from utils import b, pre, code as code_html, escape
from utils import paste
from translator import get_text_translations


async def main(bot: Bot, db: DB, logger: Logger):
    async def aexec(code, *args, timeout=None):
        exec(
            f"async def __todo(bot, message, msg, m, u, p, db, database, logger, *args):\n"
            + "".join(f"\n {_l}" for _l in code.split("\n"))
        )
        
        f = StringIO()
        with redirect_stdout(f):
            await asyncio.wait_for(locals()["__todo"](*args), timeout=timeout)

        return f.getvalue()

    

    bot.add_command(2, ['py'], get_text_translations("py_cmd_desc"), True)
    @bot.message_handler(['py'])
    async def _py(msg: M):
        if not await db.is_admin(msg.from_user.id):
            return
        if arg := extract_arguments(msg.text):
            await bot.set_state(msg.from_user.id, 'bot:py:run_code', msg.chat.id)
            async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
                data['code'] = arg
            await bot.reply(msg, "use /run for run code or /cancel to cancel")
            return 
        await bot.set_state(msg.from_user.id, 'bot:py:get_code', msg.chat.id)
        await bot.reply(msg, 'send code or /cancel')
        
    
    @bot.message_handler(state='bot:py:get_code')
    async def _get_code(msg: M):
        if arg := msg.text:
            await bot.set_state(msg.from_user.id, 'bot:py:run_code', msg.chat.id)
            async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
                data['code'] = arg
            await bot.reply(msg, "use /run for run code or /cancel to cancel")
    
    @bot.message_handler(['run'], state='bot:py:run_code')
    async def _run_code(msg: M):
        if not await db.is_admin(msg.from_user.id):
            return
        
        async with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
            code = data['code']
            
        await bot.delete_state(msg.from_user.id, msg.chat.id)
        
        try:
            start_time = time.perf_counter()
            result = await aexec(
                code, bot, msg, msg, msg, msg.from_user, print, db, db, logger, timeout=3000
            )
            stop_time = time.perf_counter()
            
            return await bot.reply(msg,
                b("🐍 Python " + sys.version.split()[0], False) + "\n\n" +
                pre(code, 'python') + "\n\n" + (
                    b("✨ Вывод:\n", False) + (
                        result if result.startswith('nekobin.com/')
                        else code_html(result)
                    ) + '\n' if result.strip() != ''
                        else b("❌ Вывода нет\n", False)
                ) + "\n" +
                b(f"⏱ Выполнено за {round(stop_time - start_time, 5)}s.", False),

                disable_web_page_preview=True,
            )
        except TimeoutError:
            return await bot.reply(msg,
                b("🐍 Python " + sys.version.split()[0], False) + "\n\n" +
                pre(code, 'python') + "\n\n" +
                b("❌ Время на исполнение кода исчерапно! TimeoutError", False),

                disable_web_page_preview=True,
            )
        except Exception as e:
            bot.logger.exception('', exc_info=e)
            err = StringIO()
            with redirect_stderr(err):
                print_exc()

            return await bot.reply(msg,
                b("🐍 Python " + sys.version.split()[0], False) + "\n\n" +
                pre(code, 'python') + "\n\n" +
                f"❌ {b(e.__class__.__name__)}: {b(e)}\n"
                f"Traceback: {escape(paste(format_exc(), 'py'))}",

                disable_web_page_preview=True,
        )
            
    @bot.message_handler(['run'], state=False)
    async def _nothing_to_run(msg: M):
        if not await db.is_admin(msg.from_user.id):
            return
        await bot.reply(msg, 'nothing to run', quote=True)
    
    @bot.message_handler(['cancel'], state='bot:py:get_code')
    @bot.message_handler(['cancel'], state='bot:py:run_code')
    async def _nothing_to_run(msg: M):
        if not await db.is_admin(msg.from_user.id):
            return
        await bot.reply(msg, 'ok', quote=True)