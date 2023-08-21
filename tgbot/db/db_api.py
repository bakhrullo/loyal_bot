from typing import List, Union
import aiohttp


async def get(url: str, params: dict = None) -> Union[List, dict]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            return await response.json()


async def post(url: str, data: dict = None) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, data=data):
            return


async def patch(url: str, data: dict = None) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.patch(url=url, data=data):
            return
