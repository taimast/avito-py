import asyncio
import os
from pprint import pformat

from aiohttp import web
from loguru import logger

from avito import Avito
from avito.models import WebhookUpdate

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN = os.getenv("TOKEN", None)

routes = web.RouteTableDef()


@routes.post("/api/webhook/{client_id}")
async def webhook(request: web.Request):
    """Handle request"""
    data = await request.json()
    logger.info(f"Webhook Request: {pformat(data)}")
    avito: Avito = request.app["avito"]

    update = WebhookUpdate.model_validate(data, context={"avito": avito})
    message = update.message
    message_text = message.content.text
    if message.from_self():
        logger.info(f"Message from self: {message_text}")
        return web.Response(text="OK")

    if message.type == "system":
        logger.info(f"System message: {message_text}")
        return web.Response(text="OK")

    logger.info(f"Message from user: {message_text}")
    await message.read_message_chat()
    await message.answer("Hello, I'm a bot")

    return web.Response(text="OK")


async def start_server():
    app = web.Application()

    avito = Avito(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token=TOKEN,
    )

    webhook_url = f"{WEBHOOK_URL}/api/webhook/{CLIENT_ID}"
    await avito.set_webhook(webhook_url, unsubscribe_all=True)
    logger.info(f"Webhook set: {webhook_url}")
    app["avito"] = avito
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        "0.0.0.0",
        81,
    )
    await site.start()


async def main():
    await start_server()
    await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
