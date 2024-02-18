from avito.base.methods import AvitoMethod
from.models import RatingInfo


class GetRatingsInfo(AvitoMethod[RatingInfo]):
    __returning__ = RatingInfo
    __api_method__ = "ratings/v1/info"
