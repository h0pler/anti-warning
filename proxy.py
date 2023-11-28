import asyncio
import platform
import sys
import datetime
import time

from proxy import check, dedupe, find


def get():
    file = "proxies.txt"
    logfile = "logs.txt"
    method = "http"
    verbose = True
    timeout = 15
    site = "google.com"
    random_user_agent = True

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(logfile, "a") as f:
        f.write(f"\n\n================= [LOG: {current_time}] =================\n")

    start_time = time.time()

    if sys.version_info >= (3, 7) and platform.system() == "Windows":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(find.scrape(method, file, verbose, logfile))
        loop.close()
    elif sys.version_info >= (3, 7):
        asyncio.run(find.scrape(method, file, verbose, logfile))
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(scrape(method, output, verbose, logfile))
        loop.close()

    asyncio.run(dedupe.dedupe(file, logfile))
    asyncio.run(check.check(file, timeout, method, site, verbose, random_user_agent, logfile))

    end_time = time.time()
    total_runtime = end_time - start_time
    # print(f"Total runtime: {total_runtime} seconds")
    with open(logfile, "a") as f:
        f.write("[DONE]  " + f"Total runtime: {total_runtime} seconds\n")

    return


if __name__ == "__main__":
    get()
