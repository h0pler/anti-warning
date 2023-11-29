import random
import re
import threading
import urllib.request
import os
from time import time
import asyncio
import aiofiles
import aiohttp
import old_scraper.agent

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
# user_agents_path = os.path.join(script_dir, "user_agents.txt")

# user_agents = []
# with open(user_agents_path, "r") as f:
#     for line in f:
#         user_agents.append(line.replace("\n", ""))


class Proxy:
    def __init__(self, method, proxy):
        if method.lower() not in ["http", "https"]:
            raise NotImplementedError("Only HTTP and HTTPS are supported")
        self.method = method.lower()
        self.proxy = proxy

    def is_valid(self):
        return re.match(r"\d{1,3}(?:\.\d{1,3}){3}(?::\d{1,5})?$", self.proxy)

    async def check(self, site, timeout, user_agent):
        url = self.method + "://" + self.proxy
        async with aiohttp.ClientSession() as session:
            try:
                start_time = time()
                async with session.get(self.method + "://" + site, headers={"User-Agent": user_agent}, proxy=url, timeout=timeout) as response:
                    end_time = time()
                    time_taken = end_time - start_time
                    return True, time_taken, None
            except Exception as e:
                return False, 0, e

    def __str__(self):
        return self.proxy


async def log_print(verbose, message, logfile):
    if verbose:
        async with aiofiles.open(logfile, "a") as file:
            await file.write("[CHECK]  " + message + "\n")


async def check_proxy(proxy, user_agent, site, timeout, random_user_agent, verbose, logfile, valid_proxies):
    new_user_agent = user_agent
    if random_user_agent:
        new_user_agent = old_scraper.agent.get()
    try:
        valid, time_taken, error = await proxy.check(site, timeout, new_user_agent)
    except AttributeError as e:
        valid, time_taken, error = await Proxy.proxy.check(site, timeout, new_user_agent)
    message = {
        True: f"{proxy} is valid, took {time_taken} seconds",
        False: f"{proxy} is invalid: {repr(error)}",
    }[valid]
    await log_print(verbose, message, logfile)
    if valid:
        valid_proxies.append(proxy)
    return valid_proxies


async def check(file, timeout, method, site, verbose, random_user_agent, logfile):
    proxies = []
    with open(file, "r") as f:
        for line in f:
            proxies.append(Proxy(method, line.replace("\n", "")))

    await log_print(verbose, f"Checking {len(proxies)} proxies", logfile)

    proxies = filter(lambda x: x.is_valid(), proxies)
    valid_proxies = []
    user_agent = old_scraper.agent.get()

    tasks = []
    for proxy in proxies:
        task = asyncio.create_task(check_proxy(proxy, user_agent, site, timeout, random_user_agent, verbose, logfile, valid_proxies))
        tasks.append(task)

    await asyncio.gather(*tasks)

    with open(file, "w") as f:
        for proxy in valid_proxies:
            f.write(str(proxy) + "\n")

    await log_print(verbose, f"Found {len(valid_proxies)} valid proxies", logfile)



# if __name__ == "__main__":
#     # python3 check.py -t 20 -s google.com -l output.txt -r -v -p http
#     timeout = 15
#     method = "http"
#     site = "google.com"
#     verbose = True
#     random_user_agent = True
#     file = "output.txt"
#     logfile = "log.txt"  # Define the logfile variable with the desired file path

#     asyncio.run(check(file, timeout, method, site, verbose, random_user_agent, logfile))