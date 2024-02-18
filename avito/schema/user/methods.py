from .models import UserInfoSelf, Balance
from avito.base.methods import AvitoMethod


class GetUserInfoSelf(AvitoMethod[UserInfoSelf]):
    __request_method__ = "GET"
    __returning__ = UserInfoSelf
    __api_method__ = "core/v1/accounts/self"


class GetUserBalance(AvitoMethod[Balance]):
    __request_method__ = "GET"
    __returning__ = Balance

    user_id: int

    @property
    def __api_method__(self) -> str:
        # https://api.avito.ru/core/v1/accounts/{user_id}/balance/
        return f"core/v1/accounts/{self.user_id}/balance"
