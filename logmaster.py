import aiofiles
import datetime

logfile = datetime.datetime.now().strftime("logs/%y%m%d-%H:%M:%S.log")


async def log_start():
    async with aiofiles.open(logfile, "a") as file:
        await file.write(f"\n\n================= [LOG] =================\n")


async def log_print(prefix, message):
    async with aiofiles.open(logfile, "a") as file:
        await file.write(prefix + "  " + message + "\n")
