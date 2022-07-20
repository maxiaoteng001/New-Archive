import aiohttp

default_headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}


async def crawl_articles(data: dict = {}):
    async with aiohttp.ClientSession(headers=data.get('headers', default_headers)) as session:
        async with session.get(data.get('url'), proxy=data.get('proxy')) as response:
            return response.status, await response.text()
