import importlib
import logging
import asyncio
import pkgutil
import os


from middlewares import setup_middlewares
from translator import get_langs
from filters import set_filters
from config import BOT_TOKEN
from database import db


from cpytba import CustomAsyncTeleBot
from telebot.types import (
    BotCommand,
    BotCommandScopeChat,
    BotCommandScopeChatMember,
    BotCommandScopeDefault
)




async def load_bot_parts(bot, db, logger):

    parts_path = os.path.join(os.path.dirname(__file__), "parts")
    loaded = []
    failed = []

    for finder, name, _ in pkgutil.iter_modules([parts_path]):
        part_logger = logger.getChild(name)
        try:
            module = importlib.import_module(f"parts.{name}")
            if hasattr(module, "main"):
                await module.main(bot, db, part_logger)
                loaded.append(name)
                part_logger.info(f"Loaded successfully.")
            else:
                failed.append(name)
                part_logger.warning(f"No main() found.")
        except Exception as e:
            failed.append(name)
            part_logger.error(f"Failed to load: {e}", exc_info=True)

    logger.info(f"Loaded bot parts: {', '.join(loaded)}")
    logger.info(f"Failed to load bot parts: {', '.join(failed)}")


async def set_commands(bot, db):
    # Set commands for each language
    for lang in get_langs():
        # Prepare user commands
        cmds = []
        for cmd in bot.commands.get(lang, []):
            if cmd['description']:
                cmds.append(cmd)
        bot.commands[lang] = sorted(cmds, key=lambda d: d['index'])
        
        cmds = []
        for cmd in bot.admin_commands.get(lang, []):
            if cmd['description']:
                cmds.append(cmd)
        bot.admin_commands[lang] = sorted(cmds, key=lambda d: d['index'])
        
        
        commands = [
            BotCommand(
                cmd['commands'][0],
                cmd['description']
            )
            for cmd in bot.commands[lang]
            if cmd['to_menu']
        ]
        await bot.set_my_commands(commands, BotCommandScopeDefault(), language_code=lang)
        await asyncio.sleep(.1)        
        
        admin_commands = commands + [
            BotCommand(
                cmd['commands'][0],
                cmd['description']
            )
            for cmd in bot.admin_commands[lang]
            if cmd['to_menu']
        ]
        for admin_id in await db.get_admins():
            await bot.set_my_commands(
                admin_commands,
                BotCommandScopeChat(admin_id),
                language_code=lang
            )
            await asyncio.sleep(.1)
            # await bot.set_my_commands(
            #     admin_commands,
            #     BotCommandScopeChatMember(-1002808566375, admin_id),
            #     language_code=lang
            # )
            # asyncio.sleep(.1)


async def start_bot():
    
    try:
        logger = logging.getLogger('BOT')
        db.logger = logger.getChild('database')
        
        await db.force_bootstrap()
        await db.create_tables()

        bot = CustomAsyncTeleBot(BOT_TOKEN, logger=logger, db=db)
        
        await bot._set_me()
        
        set_filters(bot, db)
        setup_middlewares(bot, db)

        await load_bot_parts(bot, db, logger)
        await set_commands(bot, db)
        
        await bot.polling(non_stop=True)
    except (KeyboardInterrupt, SystemExit):
        print('Stopping the bot...')
    finally:
        await db.teardown()
    logger.info('Goodbye!')
    

if __name__ == "__main__":
    raise RuntimeError("Run `main.py` instead of `bot.py`")