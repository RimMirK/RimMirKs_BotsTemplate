import sys
sys.dont_write_bytecode = True


if __name__ == '__main__':
    import asyncio
    
    from bot import start_bot
    
    asyncio.run(start_bot())