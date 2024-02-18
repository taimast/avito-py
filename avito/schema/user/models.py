# Модели данных пользователя и операций
from __future__ import annotations

import typing
from datetime import datetime
from typing import Optional, List

from pydantic import Field, HttpUrl

from avito.base.models import AvitoObject

if typing.TYPE_CHECKING:
    from avito.methods import GetChats


class UserInfoSelf(AvitoObject):
    email: Optional[str] = None
    id: int
    name: str
    phone: Optional[str] = None
    profile_url: Optional[HttpUrl] = None

    def get_chats(self) -> GetChats:
        from avito.methods import GetChats
        return GetChats(
            user_id=self.id
        ).as_(self._avito)


class Balance(AvitoObject):
    bonus: float
    real: float


class ResponseOperationsHistoryItem(AvitoObject):
    amount_bonus: Optional[float] = Field(None, alias="amountBonus")
    amount_rub: Optional[float] = Field(None, alias="amountRub")
    amount_total: float = Field(..., alias="amountTotal")
    item_id: Optional[int] = Field(None, alias="itemId")
    operation_name: str = Field(..., alias="operationName")
    operation_type: str = Field(..., alias="operationType")
    paid_at: Optional[datetime] = Field(None, alias="paidAt")
    service_id: Optional[int] = Field(None, alias="serviceId")
    service_name: Optional[str] = Field(None, alias="serviceName")
    service_type: Optional[str] = Field(None, alias="serviceType")
    updated_at: datetime = Field(..., alias="updatedAt")


class ResponseOperationsHistory(AvitoObject):
    operations: List[ResponseOperationsHistoryItem]


# Модели запросов
class RequestOperationsHistory(AvitoObject):
    date_time_from: datetime = Field(..., alias="dateTimeFrom")
    date_time_to: datetime = Field(..., alias="dateTimeTo")
