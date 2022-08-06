import aiohttp


async def fetch(url: str):
    print("url: ", url);
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        json_resp = await resp.json(content_type=None)
        return json_resp