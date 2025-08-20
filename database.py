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


from typing import AsyncGenerator, List
from logging import Logger
import time

import aiosqlite

from utils import format_date
 
 
class DB:
    path: str
    con: aiosqlite.Connection
    logger: Logger

    def __init__(self, path) -> None:
        self.path = path
        self.con = None
    

    async def bootstrap(self) -> None:
        if not self.con:
            self.con = await aiosqlite.connect(self.path)
            
    async def force_bootstrap(self) -> None:
        if self.con:
            await self.con.close()
        self.con = await aiosqlite.connect(self.path)

    async def teardown(self) -> None:
        await self.con.close()
        
    async def sql(self, sql: str, asdict: bool = False, return_cursor=False, **params) -> list | dict:
        self.logger.debug(f"Executing sql {sql!r} with params {params}")
        cursor = await self.con.execute(sql, params)
        rows = await cursor.fetchall()
        
        if asdict and return_cursor:
            raise ValueError("Cannot return cursor and asdict at the same time.")
        
        if asdict:
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        
        await self.con.commit()
        self.logger.debug(f"Executed sql {sql!r} with params {params}. result: {rows}")
        
        if return_cursor:
            return cursor
        
 
        return rows
 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    async def create_tables(self):
        
        await self.sql("""
            CREATE TABLE IF NOT EXISTS users (
                id              INTEGER PRIMARY KEY
                                        NOT NULL,
                user_id         INTEGER UNIQUE
                                        NOT NULL,
                reg             NUMERIC,
                lang            TEXT    DEFAULT en,
                rules_confirmed INTEGER DEFAULT (0),
                banned          INTEGER DEFAULT (0),
                is_admin        INTEGER DEFAULT (0),
                newsletter      INTEGER DEFAULT (1) 
            );
        """)
        await self.sql("""
            CREATE TABLE IF NOT EXISTS errors (
                id      INTEGER PRIMARY KEY,
                error   TEXT    NOT NULL,
                time    INTEGER,
                user_id INTEGER REFERENCES users (user_id) 
            );
        """)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
 

    # USERS #
 
    async def register(self, user_id: int, reg: float = None) -> None:
        await self.sql("INSERT OR IGNORE INTO users (user_id, reg) VALUES (:user_id, :reg)", user_id=user_id, reg=reg or time.time())
    
    async def is_registered(self, user_id: int) -> bool:
        return not not (await self.sql("SELECT user_id FROM users WHERE user_id=:user_id", user_id=user_id))
    
    async def get_user(self, user_id: int) -> dict:
        user = await self.sql("SELECT * FROM users WHERE user_id=:user_id LIMIT 1", user_id=user_id, asdict=True)
        if not user:
            return {}
        user: dict = user[0]
        if user['reg']:
            user['reg_str'] = format_date(user['reg'])
        return user
    
    async def ban_user(self, user_id: int) -> None:
        await self.sql("UPDATE users SET banned = 1 WHERE user_id = :user_id", user_id=user_id)
    
    async def unban_user(self, user_id: int) -> None:
        await self.sql("UPDATE users SET banned = 0 WHERE user_id = :user_id", user_id=user_id)
    
    async def is_banned(self, user_id: int) -> bool:
        return not not (await self.sql("SELECT banned FROM users WHERE user_id=:user_id", user_id=user_id))[0][0]
    
    async def is_admin(self, user_id: int) -> bool:
        return not not (await self.sql("SELECT is_admin FROM users WHERE user_id=:user_id", user_id=user_id))[0][0]
    
    async def get_admins(self) -> List[int]:
        return [a[0] for a in ((await self.sql('SELECT user_id FROM users WHERE is_admin=1')) or [])]

    async def get_users(self, important=False) -> AsyncGenerator[dict, None]:
        query = "SELECT * from users" if important else "SELECT * from users where newsletter = true" 
        for row in await self.sql(query, asdict=True):
            yield row
            
            
    # LANGUAGES #
    
    async def get_lang(self, user_id: int) -> str:
        return (await self.sql("SELECT lang FROM users WHERE user_id=:user_id", user_id=user_id))[0][0]
    
    async def set_lang(self, user_id: int, lang: str) -> None:
        await self.sql("UPDATE users SET lang = :lang where user_id = :user_id", lang=lang, user_id=user_id)


    # RULES #

    async def is_rules_confirmed(self, user_id: int) -> bool:
        return not not (await self.sql("SELECT rules_confirmed FROM users WHERE user_id=:user_id", user_id=user_id))[0][0]
    
    async def set_rules_confirmed(self, user_id: int) -> None:
        await self.sql("UPDATE users SET rules_confirmed = 1 WHERE user_id = :user_id", user_id=user_id)


    # ERRORS # 
    
    async def add_error(self, error: str, user_id: int) -> int:
        cursor = await self.sql("INSERT INTO errors (error, time, user_id) VALUES (:error, :time, :user_id)", error=error, time=time.time(), user_id=user_id, return_cursor=True)
        return cursor.lastrowid
    
    async def get_error(self, eid: int) -> dict:
        error = await self.sql("SELECT * FROM errors WHERE id=:eid LIMIT 1", eid=eid, asdict=True)
        if not error:
            return {}
        error: dict = error[0]
        if error['time']:
            error['time_str'] = format_date(error['time'])
        return error

    


db = DB('database.db')