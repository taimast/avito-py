from typing import Optional

from avito.base.methods import AvitoMethod
from .black_list import AddBlackListRequest
from .models import Chat, Chats, Messages, OkResponse, MessageType, Message, MessageToSend, WebhookSubscriptions


class GetMessages(AvitoMethod[Messages]):
    __request_method__ = "GET"
    __returning__ = Messages

    user_id: int
    chat_id: str

    limit: Optional[int] = None
    offset: Optional[int] = None

    @property
    def __api_method__(self) -> str:
        method = f"messenger/v3/accounts/{self.user_id}/chats/{self.chat_id}/messages/"
        if self.limit:
            method += f"?limit={self.limit}"
        if self.offset:
            method += f"&offset={self.offset}"
        return method


class GetChats(AvitoMethod[Chats]):
    __request_method__ = "GET"
    __returning__ = Chats

    user_id: int

    item_ids: Optional[list[int]] = None
    unread_only: Optional[bool] = None
    chat_types: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

    @property
    def __api_method__(self) -> str:
        # https://api.avito.ru/messenger/v2/accounts/{user_id}/chats
        method = f"messenger/v2/accounts/{self.user_id}/chats"
        if self.item_ids:
            method += f"?item_ids={','.join(map(str, self.item_ids))}"
        if self.unread_only:
            method += f"&unread_only={self.unread_only}"
        if self.chat_types:
            method += f"&chat_types={self.chat_types}"
        if self.limit:
            method += f"&limit={self.limit}"
        if self.offset:
            method += f"&offset={self.offset}"
        return method


class GetChat(AvitoMethod[Chat]):
    __returning__ = Chat

    user_id: int
    chat_id: str

    @property
    def __api_method__(self) -> str:
        return f"messenger/v2/accounts/{self.user_id}/chats/{self.chat_id}"


class ChatRead(AvitoMethod[OkResponse]):
    __returning__ = OkResponse

    user_id: int
    chat_id: str

    @property
    def __api_method__(self) -> str:
        # https://api.avito.ru/messenger/v1/accounts/{user_id}/chats/{chat_id}/read
        return f"messenger/v1/accounts/{self.user_id}/chats/{self.chat_id}/read"


class DeleteMessage(AvitoMethod[OkResponse]):
    __returning__ = OkResponse

    user_id: int
    chat_id: str
    message_id: str

    @property
    def __api_method__(self) -> str:
        # https://api.avito.ru/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages/{message_id}
        return f"messenger/v1/accounts/{self.user_id}/chats/{self.chat_id}/messages/{self.message_id}"


class AddToBlacklist(AvitoMethod[OkResponse]):
    __returning__ = OkResponse

    users: list[AddBlackListRequest]

    @property
    def __api_method__(self) -> str:
        # https://api.avito.ru/messenger/v2/accounts/{user_id}/blacklist
        return f"messenger/v2/accounts/{self.user_id}/blacklist"


class SendMessage(AvitoMethod[Message]):
    __content_type__ = "json"
    __returning__ = Message

    # path
    user_id: int
    chat_id: str

    # body
    message: MessageToSend
    type: MessageType = MessageType.TEXT

    @property
    def __api_method__(self) -> str:
        # https://api.avito.ru/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages
        return f"messenger/v1/accounts/{self.user_id}/chats/{self.chat_id}/messages"


class GetSubscriptions(AvitoMethod[WebhookSubscriptions]):
    __returning__ = WebhookSubscriptions
    __api_method__ = "messenger/v1/subscriptions"


class PostWebhook(AvitoMethod[OkResponse]):
    __content_type__ = "json"
    __returning__ = OkResponse
    __api_method__ = "messenger/v3/webhook"

    url: str


class PostWebhookUnsubscribe(AvitoMethod[OkResponse]):
    __content_type__ = "json"
    __returning__ = OkResponse
    __api_method__ = "messenger/v1/webhook/unsubscribe"

    url: str
