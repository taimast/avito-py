from pprint import pformat
from typing import Generic, TypeVar

import aiohttp
import orjson
from loguru import logger

from .base.methods import AvitoMethod, AvitoType
from .base.models import AvitoObject
from .methods import (
    GetRatingsInfo,
    GetSubscriptions,
    GetToken,
    GetUserBalance,
    GetUserInfoSelf,
)
from .models import Balance, RatingInfo, Token, UserInfoSelf
from .schema.messenger.methods import PostWebhook, SendImage, UploadImage
from .schema.messenger.models import WebhookSubscriptions

T = TypeVar("T")


class AvitoErrorResponse(AvitoObject):
    class AvitoError(AvitoObject):
        code: int | None = None
        message: str

    error: AvitoError


class AvitoExpiredTokenResponse(AvitoObject):
    class AvitoExpiredTokenError(AvitoObject):
        """# {'result': {'message': 'access token expired', 'status': False}}"""

        message: str
        status: bool

    result: AvitoExpiredTokenError


class AvitoResponse(AvitoObject, Generic[AvitoType]):
    result: AvitoType


class Avito:
    info_cache = {}

    def __init__(
        self,
        token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        session: aiohttp.ClientSession | None = None,
        base_url: str = "https://api.avito.ru",
    ):
        self._token = token
        self._client_id = client_id
        self._client_secret = client_secret
        if session is None:
            session = aiohttp.ClientSession()
        self.session = session
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self._token}",
            # "Content-Type": "application/json",
        }

        self._me: UserInfoSelf | None = None
        self.refreshed_token: Token | None = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def make_url(self, method: str) -> str:
        return f"{self.base_url}/{method}"

    async def _request(self, *args, **kwargs):
        async with self.session.request(*args, **kwargs) as res:
            try:
                body = await res.read()
                data = orjson.loads(body)
                logger.debug(
                    f"Response [{self._client_id}] : {res.status} {pformat(data)}"
                )
            except orjson.JSONDecodeError as e:
                text = await res.text()
                raise ValueError(f"{e} {text=} {res.status}")

            except aiohttp.ContentTypeError as e:
                text = await res.text()
                raise ValueError(f"{e} {text=}")

            if res.status != 200:
                if "error" in data:
                    response = AvitoErrorResponse.model_validate(data)
                    raise ValueError(f"{response.error.code} {response.error.message}")

                response = AvitoExpiredTokenResponse.model_validate(data)
                raise ValueError(f"{response.result.message}")

        return data

    async def _actual_call(self, method: AvitoMethod[T]) -> T:
        url = self.make_url(method.__api_method__)
        json = method.model_dump(mode="json")
        content_type = {method.__content_type__: json}
        logger.debug(
            f"Request [{self._client_id}]: {url} {pformat(json)} | {method.__request_method__} | {method.__returning__} | {content_type=}"
        )
        if isinstance(method, UploadImage):
            with aiohttp.MultipartWriter("form-data") as form:
                form.append(
                    open(method.file_path, "rb"),
                    {
                        "Content-Type": "application/octet-stream",
                        "Content-Disposition": f'form-data; name="uploadfile[]"; filename="{method.file_path}"',
                    },
                )
                data = await self._request(
                    method.__request_method__,
                    url,
                    headers=self.headers,
                    data=form,
                )
        else:
            data = await self._request(
                method.__request_method__,
                url,
                headers=self.headers,
                **content_type,
            )
        # response_type = AvitoResponse[method.__returning__]
        # response = response_type(result=data)
        # return response.result
        if method.__returning__ is dict:
            return data
        return method.__returning__.model_validate(data, context={"avito": self})

    async def __call__(self, method: AvitoMethod[T]) -> T:
        if not self._token:
            logger.info("Token is not set, trying to init token")
            await self.init_token_if_needed()
        try:
            return await self._actual_call(method)
        except ValueError as e:
            logger.warning(f"Error: {e}")
            if "access token expired" in str(e):
                self.refreshed_token = await self.refresh_token()
                return await self._actual_call(method)
            if str(e).startswith("unauthorized_"):
                self.refreshed_token = await self.refresh_token()
                return await self._actual_call(method)
            if "invalid access token" in str(e):
                self.refreshed_token = await self.refresh_token()
                return await self._actual_call(method)
            raise e

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value
        self.headers = {
            "Authorization": f"Bearer {self._token}",
        }

    async def refresh_token(self) -> Token:
        get_token = GetToken(
            client_id=self._client_id,
            client_secret=self._client_secret,
        ).as_(self)
        token = await get_token
        self.token = token.access_token
        return token

    async def init_token_if_needed(self) -> Token | None:
        if self.token:
            return None
        get_token = GetToken(
            client_id=self._client_id,
            client_secret=self._client_secret,
        ).as_(self)
        token = await self._actual_call(get_token)
        self.token = token.access_token
        return token

    async def get_self_info(self) -> UserInfoSelf:
        if self._me:
            logger.debug(f"Using cached self info _me: {self._me}")
            return self._me
        if info := self.info_cache.get(self._client_id):
            logger.debug(f"Using cached self info info_cache: {info}")
            self._me = info
        else:
            call = GetUserInfoSelf()
            self._me = await self(call)
            self.info_cache[self._client_id] = self._me
        return self._me

    async def get_self_rating(self) -> RatingInfo:
        call = GetRatingsInfo()
        return await self(call)

    async def get_self_balance(self) -> Balance:
        return await self.get_balance(self._me.id)

    async def get_balance(self, user_id: int) -> Balance:
        call = GetUserBalance(user_id=user_id)
        return await self(call)

    async def unsubscribe_all(self) -> WebhookSubscriptions:
        subscriptions = await self.get_subscriptions()
        for subscription in subscriptions.subscriptions:
            await subscription.unsubscribe()
        return subscriptions

    async def get_subscriptions(self) -> WebhookSubscriptions:
        call = GetSubscriptions()
        return await self(call)

    async def set_webhook(self, url: str, unsubscribe_all: bool = False):
        if unsubscribe_all:
            await self.unsubscribe_all()
        call = PostWebhook(url=url)
        return await self(call)

    async def upload_image(
        self,
        file_path: str,
    ) -> str:
        from .schema.messenger.methods import UploadImage

        me = await self.get_self_info()
        call = UploadImage(user_id=me.id, file_path=file_path)
        res = await self(call)
        if isinstance(res, dict):
            # first key is image_id
            image_id = list(res.keys())[0]
            return image_id
        raise ValueError("Failed to upload image")

    async def send_image(
        self,
        chat_id: str,
        file_path: str,
    ) -> dict:
        image_id = await self.upload_image(file_path=file_path)
        me = await self.get_self_info()
        call = SendImage(
            user_id=me.id,
            chat_id=chat_id,
            image_id=image_id,
        )
        return await self(call)
