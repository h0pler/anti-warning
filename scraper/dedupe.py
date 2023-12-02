import asyncio
import aiofiles
import logmaster


async def dedupe(file):
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
    await logmaster.log_print("[DEDUPE]", f"Removed {duplicates} duplicates")


if __name__ == "__main__":
    asyncio.run(dedupe("output.txt"))
