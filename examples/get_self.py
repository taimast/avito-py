import asyncio
import os

from avito import Avito

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN = os.getenv("TOKEN", None)


async def main():
    async with Avito(TOKEN) as avito:
        token = await avito.init_token(CLIENT_ID, CLIENT_SECRET)
        # save token to db
        me = await avito.get_self_info()
        print(me)


if __name__ == '__main__':
    asyncio.run(main())
