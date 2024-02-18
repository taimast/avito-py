from __future__ import annotations

from enum import StrEnum

from pydantic import Field


from avito.base.methods import AvitoMethod
from .models import OAuthToken, Token


class GrantType(StrEnum):
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"



class GetTokenOAuth(AvitoMethod[OAuthToken]):
    __returning__ = OAuthToken
    __api_method__ = "token"

    client_id: str
    client_secret: str
    code: str
    grant_type: GrantType = Field(default=GrantType.AUTHORIZATION_CODE)


class GetToken(AvitoMethod[Token]):
    __returning__ = Token
    __api_method__ = "token"

    client_id: str
    client_secret: str
    grant_type: GrantType = Field(default=GrantType.CLIENT_CREDENTIALS)


class RefreshOAuthToken(AvitoMethod[Token]):
    __returning__ = Token
    __api_method__ = "token"

    client_id: str
    client_secret: str
    grant_type: GrantType = Field(default=GrantType.REFRESH_TOKEN, description="Тип OAuth flow. Строка refresh_token")
    refresh_token: str
