from __future__ import annotations

import typing
from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl

from avito.base.models import AvitoObject

from .black_list import Reason

if typing.TYPE_CHECKING:
    from ...methods import (
        AddToBlacklist,
        ChatRead,
        DeleteMessage,
        GetMessages,
        PostWebhookUnsubscribe,
        SendImage,
        SendMessage,
    )


class ImageSizes(AvitoObject):
    size_1280x960: Optional[HttpUrl] = Field(None, alias="1280x960")
    size_140x105: Optional[HttpUrl] = Field(None, alias="140x105")
    size_32x32: Optional[HttpUrl] = Field(None, alias="32x32")
    size_640x480: Optional[HttpUrl] = Field(None, alias="640x480")


class ImageContent(AvitoObject):
    sizes: ImageSizes


class ItemContent(AvitoObject):
    image_url: HttpUrl
    item_url: HttpUrl
    price_string: Optional[str] = None
    title: str


class LinkPreview(AvitoObject):
    description: Optional[str] = None
    domain: Optional[str] = None
    images: Optional[ImageSizes] = None
    title: Optional[str] = None
    url: Optional[HttpUrl] = None


class LinkContent(AvitoObject):
    preview: Optional[LinkPreview] = None
    text: str
    url: HttpUrl


class LocationContent(AvitoObject):
    kind: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    text: Optional[str] = None
    title: Optional[str] = None


class CallContent(AvitoObject):
    status: Optional[str] = None
    target_user_id: Optional[int] = None


# Модель для содержимого сообщения
class MessageContent(AvitoObject):
    call: Optional[CallContent] = None
    image: Optional[ImageContent] = None
    item: Optional[ItemContent] = None
    link: Optional[LinkContent] = None
    location: Optional[LocationContent] = None
    text: Optional[str] = None


# Модель для цитаты сообщения
class MessageQuote(AvitoObject):
    author_id: int
    content: MessageContent
    created: int
    id: str
    type: MessageType


class Direction(StrEnum):
    INCOMING = "in"
    OUTGOING = "out"


class MessageType(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    LINK = "link"
    ITEM = "item"
    LOCATION = "location"
    CALL = "call"
    DELETED = "deleted"
    SYSTEM = "system"


# Сообщение для отправки
class MessageToSend(AvitoObject):
    text: str


# Модель для сообщения
class Message(AvitoObject):
    author_id: int
    content: MessageContent
    created: int
    direction: Direction
    id: str
    is_read: Optional[bool] = Field(None, alias="isRead")
    quote: Optional[MessageQuote] = None
    read: Optional[int] = None
    type: MessageType


class Meta(AvitoObject):
    has_more: bool


class Messages(AvitoObject):
    messages: List[Message]
    meta: Meta


class ImageDetails(AvitoObject):
    size_140x105: Optional[HttpUrl] = Field(None, alias="140x105")


class Images(AvitoObject):
    count: int
    main: ImageDetails


class ItemContextValue(AvitoObject):
    id: int
    images: Images
    price_string: str
    status_id: int
    title: str
    url: HttpUrl
    user_id: int


class ChatContext(AvitoObject):
    type: str
    value: ItemContextValue


class AvatarImages(AvitoObject):
    size_128x128: Optional[HttpUrl] = Field(None, alias="128x128")
    size_192x192: Optional[HttpUrl] = Field(None, alias="192x192")
    size_24x24: Optional[HttpUrl] = Field(None, alias="24x24")
    size_256x256: Optional[HttpUrl] = Field(None, alias="256x256")
    size_36x36: Optional[HttpUrl] = Field(None, alias="36x36")
    size_48x48: Optional[HttpUrl] = Field(None, alias="48x48")
    size_64x64: Optional[HttpUrl] = Field(None, alias="64x64")
    size_72x72: Optional[HttpUrl] = Field(None, alias="72x72")
    size_96x96: Optional[HttpUrl] = Field(None, alias="96x96")


class PublicUserProfile(AvitoObject):
    avatar: AvatarImages
    item_id: int
    url: HttpUrl
    user_id: int


class User(AvitoObject):
    id: int
    name: str
    public_user_profile: PublicUserProfile


# Модель для чата
class Chat(AvitoObject):
    context: ChatContext
    created: int
    id: str
    last_message: Message
    updated: int
    users: List[User]

    def get_messages(self) -> GetMessages:
        from avito.methods import GetMessages

        return GetMessages(user_id=self.me_id, chat_id=self.id).as_(self._avito)

    def read(self) -> ChatRead:
        from avito.methods import ChatRead

        return ChatRead(user_id=self.me_id, chat_id=self.id).as_(self._avito)


class Chats(BaseModel):
    chats: List[Chat]


# Модель для сообщения от вебхука
class WebhookMessage(AvitoObject):
    author_id: int
    chat_id: str
    chat_type: str
    content: MessageContent
    created: int
    id: str
    item_id: Optional[int] = None
    read: Optional[int] = None
    type: str
    user_id: int

    def answer(self, text: str) -> SendMessage:
        from avito.methods import SendMessage
        from avito.models import MessageToSend

        return SendMessage(
            user_id=self.me_id, chat_id=self.chat_id, message=MessageToSend(text=text)
        ).as_(self._avito)

    async def answer_image(self, file_path: str) -> SendImage:
        from avito.schema.messenger.methods import SendImage

        image_id = await self._avito.upload_image(file_path)
        return SendImage(
            user_id=self.me_id,
            chat_id=self.chat_id,
            image_id=image_id,
        ).as_(self._avito)

    def from_self(self) -> bool:
        return self.author_id == self.me_id

    def read_message_chat(self) -> ChatRead:
        from avito.methods import ChatRead

        return ChatRead(user_id=self.me_id, chat_id=self.chat_id).as_(self._avito)

    def delete_message(self) -> DeleteMessage:
        from avito.methods import DeleteMessage

        return DeleteMessage(
            user_id=self.me_id, chat_id=self.chat_id, message_id=self.id
        ).as_(self._avito)

    def add_to_blacklist(self, reason: Reason = Reason.OTHER) -> AddToBlacklist:
        from avito.methods import AddToBlacklist
        from avito.models import AddBlackListRequest, BlackListContext, BlackListUser

        return AddToBlacklist(
            users=[
                AddBlackListRequest(
                    users=[
                        BlackListUser(
                            context=BlackListContext(
                                item_id=self.item_id, reason_id=reason
                            ),
                            user_id=self.user_id,
                        )
                    ]
                )
            ]
        ).as_(self._avito)


class WebhookPayload(AvitoObject):
    type: str
    value: WebhookMessage


class WebhookUpdate(AvitoObject):
    """
    'id': 'e7fe3e32-7dcb-435b-92f9-db1f1f3c9a6f',
    'payload': {'type': 'message',
                'value': {'author_id': 237569507,
                          'chat_id': 'u2i-eaK3A2JW1iRBkCS~9UkP6Q',
                          'chat_type': 'u2i',
                          'content': {'text': 'Привет'},
                          'created': 1707486141,
                          'id': '707ed8b26213d69d8ea07fd0cc641b2c',
                          'item_id': 3749321767,
                          'type': 'text',
                          'user_id': 370440487}},
    'timestamp': 1707486141,
    'version': 'v3.0.0'}

    """

    id: str
    payload: WebhookPayload
    timestamp: int
    version: str

    @property
    def message(self) -> WebhookMessage:
        return self.payload.value


# set weebhook response
class OkResponse(AvitoObject):
    ok: bool = True


class WebhookSubscription(AvitoObject):
    url: str
    version: str

    def unsubscribe(self) -> PostWebhookUnsubscribe:
        from avito.methods import PostWebhookUnsubscribe

        return PostWebhookUnsubscribe(url=self.url).as_(self._avito)


class WebhookSubscriptions(AvitoObject):
    subscriptions: List[WebhookSubscription]
