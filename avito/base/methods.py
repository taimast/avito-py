from __future__ import annotations

import abc
import typing
from typing import Generic, TypeVar

from pydantic import BaseModel

from avito.base.context_controller import BotContextController

if typing.TYPE_CHECKING:
    from avito.avito import Avito
    from avito.base.models import AvitoObject

AvitoType = TypeVar("AvitoType")


class AvitoMethod(BotContextController, BaseModel, Generic[AvitoType], abc.ABC):
    __request_method__ = "POST"
    __content_type__ = "data"

    @property
    @abc.abstractmethod
    def __returning__(self) -> AvitoObject:
        pass

    @property
    @abc.abstractmethod
    def __api_method__(self) -> str:
        pass

    async def emit(self, avito: Avito) -> AvitoType:
        return await avito(self)

    # async def __call__(self) -> AvitoType:
    #     if self._avito is None:
    #         raise ValueError("Avito is not set")
    #     return await self.emit(self._avito)

    def __await__(self) -> typing.Generator[typing.Any, None, AvitoType]:
        avito = self._avito
        if not avito:
            raise RuntimeError(
                "This method is not mounted to a any avito instance, please call it explicilty "
                "with avito instance `await avito(method)`\n"
                "or mount method to a avito instance `method.as_(avito)` "
                "and then call it `await method()`"
            )
        return self.emit(avito).__await__()
