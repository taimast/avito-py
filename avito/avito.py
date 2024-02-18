from pprint import pformat
from typing import TypeVar, Generic

import aiohttp
import orjson
from loguru import logger

from .base.methods import AvitoMethod, AvitoType
from .base.models import AvitoObject
from .methods import GetToken, GetRatingsInfo, GetUserInfoSelf, GetUserBalance
from .models import Token, UserInfoSelf, Balance, RatingInfo

T = TypeVar("T")


class AvitoError(AvitoObject):
    code: int
    message: str


class AvitoErrorResponse(AvitoObject):
    error: AvitoError


class AvitoResponse(AvitoObject, Generic[AvitoType]):
    result: AvitoType


class Avito:

    def __init__(
            self,
            token: str | None = None,
            session: aiohttp.ClientSession | None = None,
            base_url: str = "https://api.avito.ru",
    ):
        self._token = token
        if session is None:
            session = aiohttp.ClientSession()
        self.session = session
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self._token}",
            # "Content-Type": "application/json",
        }

        self._me: UserInfoSelf | None = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def make_url(self, method: str) -> str:
        return f"{self.base_url}/{method}"

    async def __call__(
            self,
            method: AvitoMethod[T]
    ) -> T:
        url = self.make_url(method.__api_method__)
        json = method.model_dump(mode="json")
        content_type = {method.__content_type__: json}
        logger.debug(f"Request: {url} {pformat(json)} | {method.__request_method__} | {method.__returning__} | {content_type=}")
        async with self.session.request(
                method.__request_method__,
                url,
                headers=self.headers,
                **content_type,
        ) as res:
            try:
                # text = await res.json(loads=orjson.loads)
                body = await res.read()
                # if not body and res.status == 200:
                #     data = {}
                # else:
                data = orjson.loads(body)
                logger.debug(f"Response: {res.status} {pformat(data)}")
            except orjson.JSONDecodeError as e:
                text = await res.text()
                raise ValueError(f"{e} {text=} {res.status}")

            except aiohttp.ContentTypeError as e:
                text = await res.text()
                raise ValueError(f"{e} {text=}")

            if res.status != 200:
                response = AvitoErrorResponse.model_validate(data)
                raise ValueError(f"{response.error.code} {response.error.message}")

            if "error" in data:
                response = AvitoErrorResponse.model_validate(data)
                raise ValueError(f"{response.error.code} {response.error.message}")

            # pprint(data)
            # response_type = AvitoResponse[method.__returning__]
            # response = response_type(result=data)
            # return response.result
            return method.__returning__.model_validate(data, context={"avito": self})

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value
        self.headers = {
            "Authorization": f"Bearer {self._token}",
        }

    async def init_token_if_needed(self, client_id: str, client_secret: str) -> Token | None:
        if self.token:
            return None
        get_token = GetToken(
            client_id=client_id,
            client_secret=client_secret,
        ).as_(self)
        token = await get_token
        self.token = token.access_token
        return token

    async def get_self_info(self) -> UserInfoSelf:
        if self._me:
            return self._me
        call = GetUserInfoSelf()
        self._me = await self(call)
        return self._me

    async def get_self_rating(self) -> RatingInfo:
        call = GetRatingsInfo()
        return await self(call)

    async def get_self_balance(self) -> Balance:
        return await self.get_balance(self._me.id)

    async def get_balance(self, user_id: int) -> Balance:
        call = GetUserBalance(user_id=user_id)
        return await self(call)
