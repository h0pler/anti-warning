import asyncio
import platform
import sys

from proxy import check, dedupe, find

def get():
  file="proxies.txt"
  method = "http"
  verbose = True
  timeout=15
  site="google.com"
  random_user_agent=True

  if sys.version_info >= (3, 7) and platform.system() == 'Windows':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(find.scrape(method, file, verbose))
    loop.close()
  elif sys.version_info >= (3, 7):
    asyncio.run(find.scrape(method, file, verbose))
  else:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrape(method, output, verbose))
    loop.close()
  
  dedupe.dedupe(file)
  check.check(file, timeout, method, site, verbose, random_user_agent)


if __name__ == "__main__":
  get()
