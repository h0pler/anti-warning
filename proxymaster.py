import asyncio
import os
import random
import time
from scraper import check, dedupe, find
import logmaster


async def make():
    file = "proxies.txt"
    method = "http"
    timeout = 9
    site = "google.com"
    random_user_agent = True

    await logmaster.log_start()

    start_time = time.time()

    await find.scrape(method, file)
    await dedupe.dedupe(file)
    await check.check(file, timeout, method, site, random_user_agent)

    end_time = time.time()
    total_runtime = end_time - start_time
    await logmaster.log_print("[DONE]", f"Total runtime: {total_runtime} seconds")

    return


async def get():
    await make()
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    proxies_path = os.path.join(script_dir, "proxies.txt")

    proxies = []
    with open(proxies_path, "r") as f:
        for line in f:
            proxies.append(line.replace("\n", ""))

    proxy = []
    ip, port = random.choice(proxies).split(":")
    proxy.append(ip)
    proxy.append(port)

    return proxy


if __name__ == "__main__":
    asyncio.run(make())
    asyncio.run(get())
