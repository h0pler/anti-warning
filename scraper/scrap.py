import asyncio
from bs4 import BeautifulSoup
import re
import httpx


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

class SpysMeScraper(Scraper):
    def __init__(self, method):
        super().__init__(method, "https://spys.me/{mode}.txt")

    def get_url(self, **kwargs):
        mode = "proxy" if self.method == "http" else "socks" if self.method == "socks" else "unknown"
        if mode == "unknown":
            raise NotImplementedError
        return super().get_url(mode=mode, **kwargs)

class ProxyScrapeScraper(Scraper):
    def __init__(self, method, timeout=1000, country="All"):
        self.timeout = timeout
        self.country = country
        super().__init__(method,
                         "https://api.proxyscrape.com/?request=getproxies"
                         "&proxytype={method}"
                         "&timeout={timeout}"
                         "&country={country}")

    def get_url(self, **kwargs):
        return super().get_url(timeout=self.timeout, country=self.country, **kwargs)

class GeoNodeScraper(Scraper):
    def __init__(self, method, limit="500", page="1", sort_by="lastChecked", sort_type="desc"):
        self.limit = limit
        self.page = page
        self.sort_by = sort_by
        self.sort_type = sort_type
        super().__init__(method,
                         "https://proxylist.geonode.com/api/proxy-list?"
                         "&limit={limit}"
                         "&page={page}"
                         "&sort_by={sort_by}"
                         "&sort_type={sort_type}")

    def get_url(self, **kwargs):
        return super().get_url(limit=self.limit, page=self.page, sort_by=self.sort_by, sort_type=self.sort_type, **kwargs)

class ProxyListDownloadScraper(Scraper):
    def __init__(self, method, anon):
        self.anon = anon
        super().__init__(method, "https://www.proxy-list.download/api/v1/get?type={method}&anon={anon}")

    def get_url(self, **kwargs):
        return super().get_url(anon=self.anon, **kwargs)

class GeneralTableScraper(Scraper):
    async def handle(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        proxies = set()
        table = soup.find("table", attrs={"class": "table table-striped table-bordered"})
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


async def scrape(method, output, verbose):
    loop = asyncio.get_event_loop()
    now = loop.time()
    methods = [method]
    if method == "socks":
        methods += ["socks4", "socks5"]
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
        ProxyListDownloadScraper("http", "anonymo"),
        GeneralTableScraper("https", "http://sslproxies.org"),
        GeneralTableScraper("http", "http://free-proxy-list.net"),
        GeneralTableScraper("http", "http://us-proxy.org"),
        GeneralTableScraper("socks", "http://socks-proxy.net"),
    ]
    proxy_scrapers = [s for s in scrapers if s.method in methods]
    if not proxy_scrapers:
        raise ValueError("Method not supported")
    
    def verbose_print(verbose, message):
        if verbose:
            print(message)

    verbose_print(verbose, "Scraping proxies...")
    proxies = []

    tasks = []
    client = httpx.AsyncClient(follow_redirects=True)

    async def scrape_scraper(scraper):
        try:
            verbose_print(verbose, f"Looking {scraper.get_url()}...")
            proxies.extend(await scraper.scrape(client))
        except Exception:
            pass

    for scraper in proxy_scrapers:
        tasks.append(asyncio.ensure_future(scrape_scraper(scraper)))

    await asyncio.gather(*tasks)
    await client.aclose()

    verbose_print(verbose, f"Writing {len(proxies)} proxies to file...")
    with open(output, "w") as f:
        f.write("\n".join(proxies))
    verbose_print(verbose, "Done!")
    loop = asyncio.get_event_loop()
    now = loop.time()
    verbose_print(verbose, f"Took {now} seconds")