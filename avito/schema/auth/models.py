from __future__ import annotations

import abc
import typing
from datetime import datetime

from pydantic import model_validator

if typing.TYPE_CHECKING:
    from ...methods import RefreshOAuthToken, GetToken

from avito.base.models import AvitoObject


class BaseToken(AvitoObject, abc.ABC):
    access_token: str
    expires_in: int
    token_type: str

    expires_at: float = .0

    @model_validator(mode="after")
    def set_expires_at(self):
        self.expires_at = self.expires_in + datetime.now().timestamp()
        return self

    def is_expired(self) -> bool:
        return self.expires_at < datetime.now().timestamp()



class OAuthToken(BaseToken):
    refresh_token: str
    scope: str

    def refresh(self, client_id: str, client_secret: str) -> RefreshOAuthToken:
        from ...methods import RefreshOAuthToken
        return RefreshOAuthToken(
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=self.refresh_token
        ).as_(self._avito)




class Token(BaseToken):

    def refresh(self, client_id: str, client_secret: str) -> GetToken:
        from ...methods import GetToken
        return GetToken(
            client_id=client_id,
            client_secret=client_secret,
        ).as_(self._avito)
