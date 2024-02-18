from enum import IntEnum

from pydantic import Field

from avito.base.models import AvitoObject


#

class Reason(IntEnum):
    """
    Причина блокировки:
      * `spam` - Спам
      * `fraud` - Мошенничество
      * `abuse` - Оскорбление
      * `other` - Другое
    """
    SPAM = 1
    FRAUD = 2
    ABUSE = 3
    OTHER = 4


class Context(AvitoObject):
    item_id: int
    reason_id: Reason


class User(AvitoObject):
    context: Context
    user_id: int = Field(
        description='id пользователя которого хотим заблокировать',
        example=94235311,
    )


class AddBlackListRequest(AvitoObject):
    users: list[User] | None = None
