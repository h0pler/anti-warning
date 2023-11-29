import asyncio
import platform
import sys
import urllib.request
import os
import random
from time import time

def dedupe(file):
    proxies = []
    duplicates = 0
    with open(file, "r") as f:
        for line in f:
            proxy = line.replace("\n", "")
            if proxy not in proxies:
                proxies.append(proxy)
            else:
                duplicates += 1
    with open(file, "w") as f:
        for proxy in proxies:
            f.write(proxy + "\n")
    print(f"Removed {duplicates} duplicates")

def get():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    proxies_path = os.path.join(script_dir, "../proxies.txt")

    proxies = []
    with open(proxies_path, "r") as f:
        for line in f:
            proxies.append(line.replace("\n", ""))

    proxy = []
    ip, port = random.choice(proxies).split(':')
    proxy.append(ip)
    proxy.append(port)

    return proxy