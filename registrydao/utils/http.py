import aiohttp


async def fetch(url: str):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        json_resp = await resp.json()
        return json_resp