from urllib.parse import urlparse

import aiohttp
from aiohttp import web, TCPConnector, ClientSession


async def proxy_handler(request: web.Request) -> web.Response:
    """
    Check request contains http url in query args:
        /fetch?url=http%3A%2F%2Fexample.com%2F
    and trying to fetch it and return body with http status.
    If url passed without scheme or is invalid raise 400 Bad request.
    On failure raise 502 Bad gateway.
    :param request: aiohttp.web.Request to handle
    :return: aiohttp.web.Response
    """
    url = request.query.get("url")
    if url:
        parsed_url = urlparse(url)
        if parsed_url.scheme:
            if parsed_url.scheme == 'ftp':
                return web.Response(text='Bad url scheme: ftp', status=400)
            if parsed_url.netloc:
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(url) as resp:
                            content = await resp.text()
                            return web.Response(text=content, status=resp.status)
                    except aiohttp.ClientError:
                        return web.Response(text='Error occurred during request', status=502)
            return web.Response(text='Internal server error', status=500)
        return web.Response(text='Empty url scheme', status=400)
    return web.Response(text='No url to fetch', status=400)


async def setup_application(app: web.Application) -> None:
    """
    Setup application routes and aiohttp session for fetching
    :param app: app to apply settings with
    """
    connector = TCPConnector(limit=0)
    session = ClientSession(connector=connector)
    app['session'] = session
    app.add_routes([web.get('/fetch', proxy_handler),
                    web.get('/ok', proxy_handler),
                    web.get('/fail', proxy_handler),
                    web.get('/sleep', proxy_handler)])


async def teardown_application(app: web.Application) -> None:
    """
    Application with aiohttp session for tearing down
    :param app: app for tearing down
    """
    session: ClientSession = app['session']
    await session.close()
    await app.cleanup()
