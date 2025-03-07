import asyncio
import os
from pathlib import Path

from avito import Avito

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN = os.getenv("TOKEN", None)

image_path = Path(r"image.jpeg")


async def main():
    async with Avito(TOKEN, CLIENT_ID, CLIENT_SECRET) as avito:
        chat_id = "<chat_id>"
        image = await avito.send_image(chat_id, str(image_path.resolve().absolute()))
        print(image)


if __name__ == "__main__":
    asyncio.run(main())
