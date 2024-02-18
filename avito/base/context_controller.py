from __future__ import annotations

import typing
from typing import Any, Optional

from pydantic import BaseModel, PrivateAttr
from typing_extensions import Self

if typing.TYPE_CHECKING:
    from avito.avito import Avito


class BotContextController(BaseModel):
    _avito: Optional[Avito] = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        # print(self.__class__.__name__, __context)
        self._avito = __context.get("avito") if __context else None

        # print(__context)
    def as_(self, avito: Optional[Avito]) -> Self:
        """
        Bind object to a bot instance.

        :param avito: Bot instance
        :return: self
        """
        self._avito = avito
        return self

    @property
    def avito(self) -> Optional[Avito]:
        """
        Get bot instance.

        :return: Bot instance
        """
        return self._avito

    @property
    def me_id(self)-> Optional[int]:
        return self._avito._me.id if self._avito else None
