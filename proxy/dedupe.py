import asyncio
import aiofiles

async def log_print(verbose, message, logfile):
    if verbose:
        async with aiofiles.open(logfile, "a") as file:
            await file.write("[DEDUPE]  " + message + "\n")

async def dedupe(file, logfile):
    proxies = []
    duplicates = 0
    async with aiofiles.open(file, "r") as f:
        async for line in f:
            proxy = line.replace("\n", "")
            if proxy not in proxies:
                proxies.append(proxy)
            else:
                duplicates += 1
    async with aiofiles.open(file, "w") as f:  
        for proxy in proxies:
            await f.write(proxy + "\n")
    await log_print(True, f"Removed {duplicates} duplicates", logfile)

if __name__ == "__main__":
    asyncio.run(dedupe("output.txt", "logfile.txt"))