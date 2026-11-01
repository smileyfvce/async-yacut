import asyncio
import urllib.parse

import aiohttp

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'


async def upload_file(session, file, token):
    headers = {'Authorization': f'OAuth {token}'}

    async with session.get(
        UPLOAD_URL,
        headers=headers,
        params={'path': f'app:/{file.filename}', 'overwrite': 'true'},
    ) as response:
        data = await response.json()
        upload_href = data['href']

    async with session.put(upload_href, data=file.read()) as response:
        location = response.headers['Location']
        path = urllib.parse.unquote(location).replace('/disk', '')

    async with session.get(
        DOWNLOAD_URL,
        headers=headers,
        params={'path': path},
    ) as response:
        data = await response.json()
        download_href = data['href']

    return download_href


async def upload_files(files, token):
    async with aiohttp.ClientSession() as session:
        tasks = [upload_file(session, file, token) for file in files]
        return await asyncio.gather(*tasks)