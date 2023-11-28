import asyncio
import platform
import re
import sys
import time

import httpx
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, method, _url):
        self.method = method
        self._url = _url

    def get_url(self, **kwargs):
        return self._url.format(**kwargs, method=self.method)

    async def get_response(self, client):
        return await client.get(self.get_url())

    async def handle(self, response):
        return response.text

    async def scrape(self, client):
        response = await self.get_response(client)
        proxies = await self.handle(response)
        pattern = re.compile(r"\d{1,3}(?:\.\d{1,3}){3}(?::\d{1,5})?")
        return re.findall(pattern, proxies)


# From spys.me
class SpysMeScraper(Scraper):
    def __init__(self, method):
        super().__init__(method, "https://spys.me/{mode}.txt")

    def get_url(self, **kwargs):
        mode = (
            "proxy"
            if self.method == "http"
            else "socks"
            if self.method == "socks"
            else "unknown"
        )
        if mode == "unknown":
            raise NotImplementedError
        return super().get_url(mode=mode, **kwargs)


# From proxyscrape.com
class ProxyScrapeScraper(Scraper):
    def __init__(self, method, timeout=1000, country="All"):
        self.timout = timeout
        self.country = country
        super().__init__(
            method,
            "https://api.proxyscrape.com/?request=getproxies"
            "&proxytype={method}"
            "&timeout={timout}"
            "&country={country}",
        )

    def get_url(self, **kwargs):
        return super().get_url(timout=self.timout, country=self.country, **kwargs)


# From geonode.com - A little dirty, grab http(s) and socks but use just for socks
class GeoNodeScraper(Scraper):
    def __init__(
        self, method, limit="500", page="1", sort_by="lastChecked", sort_type="desc"
    ):
        self.limit = limit
        self.page = page
        self.sort_by = sort_by
        self.sort_type = sort_type
        super().__init__(
            method,
            "https://proxylist.geonode.com/api/proxy-list?"
            "&limit={limit}"
            "&page={page}"
            "&sort_by={sort_by}"
            "&sort_type={sort_type}",
        )

    def get_url(self, **kwargs):
        return super().get_url(
            limit=self.limit,
            page=self.page,
            sort_by=self.sort_by,
            sort_type=self.sort_type,
            **kwargs,
        )


# From proxy-list.download
class ProxyListDownloadScraper(Scraper):
    def __init__(self, method, anon):
        self.anon = anon
        super().__init__(
            method,
            "https://www.proxy-list.download/api/v1/get?type={method}&anon={anon}",
        )

    def get_url(self, **kwargs):
        return super().get_url(anon=self.anon, **kwargs)


# For websites using table in html
class GeneralTableScraper(Scraper):
    async def handle(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        proxies = set()
        table = soup.find(
            "table", attrs={"class": "table table-striped table-bordered"}
        )
        for row in table.findAll("tr"):
            count = 0
            proxy = ""
            for cell in row.findAll("td"):
                if count == 1:
                    proxy += ":" + cell.text.replace("&nbsp;", "")
                    proxies.add(proxy)
                    break
                proxy += cell.text.replace("&nbsp;", "")
                count += 1
        return "\n".join(proxies)


scrapers = [
    SpysMeScraper("http"),
    SpysMeScraper("socks"),
    ProxyScrapeScraper("http"),
    ProxyScrapeScraper("socks4"),
    ProxyScrapeScraper("socks5"),
    GeoNodeScraper("socks"),
    ProxyListDownloadScraper("https", "elite"),
    ProxyListDownloadScraper("http", "elite"),
    ProxyListDownloadScraper("http", "transparent"),
    ProxyListDownloadScraper("http", "anonymous"),
    GeneralTableScraper("https", "http://sslproxies.org"),
    GeneralTableScraper("http", "http://free-proxy-list.net"),
    GeneralTableScraper("http", "http://us-proxy.org"),
    GeneralTableScraper("socks", "http://socks-proxy.net"),
]


def log_print(verbose, message, logfile):
    if verbose:
        # print(message)
        with open(logfile, "a") as file:
            file.write("[FIND]  " + message + "\n")
        


async def scrape(method, output, verbose, logfile):
    now = time.time()
    methods = [method]
    if method == "socks":
        methods += ["socks4", "socks5"]
    proxy_scrapers = [s for s in scrapers if s.method in methods]
    if not proxy_scrapers:
        raise ValueError("Method not supported")
    log_print(verbose, "Scraping proxies...", logfile)
    proxies = []

    tasks = []
    client = httpx.AsyncClient(follow_redirects=True)

    async def scrape_scraper(scraper):
        try:
            log_print(verbose, f"Looking {scraper.get_url()}...", logfile)
            proxies.extend(await scraper.scrape(client))
        except Exception:
            pass

    for scraper in proxy_scrapers:
        tasks.append(asyncio.ensure_future(scrape_scraper(scraper)))

    await asyncio.gather(*tasks)
    await client.aclose()

    log_print(verbose, f"Writing {len(proxies)} proxies to file...", logfile)
    with open(output, "w") as f:
        f.write("\n".join(proxies))
    log_print(verbose, "Done!", logfile)
    log_print(verbose, f"Took {time.time() - now} seconds", logfile)


if __name__ == "__main__":
    method = "http"
    output = "output.txt"
    verbose = True

    if sys.version_info >= (3, 7) and platform.system() == "Windows":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(scrape(method, output, verbose))
        loop.close()
    elif sys.version_info >= (3, 7):
        asyncio.run(scrape(method, output, verbose))
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(scrape(method, output, verbose))
        loop.close()
