from enum import StrEnum

from pydantic import Field

from avito.base.models import AvitoObject


class Stage(StrEnum):
    """
    Стадия сделки:
      * `done` - Сделка состоялась
      * `fell_through` - Сделка сорвалсь
      * `not_agree` - Не договорились
      * `not_communicate` - Не общались

    """

    DONE = 'done'
    FELL_THROUGH = 'fell_through'
    NOT_AGREE = 'not_agree'
    NOT_COMMUNICATE = 'not_communicate'


class Status(StrEnum):
    """
    Статус ответа:
      * `moderation` - на модерации
      * `published` - опубликован
      * `rejected` - отклонен

    """

    MODERATION = 'moderation'
    PUBLISHED = 'published'
    REJECTED = 'rejected'


# {
# "isEnabled": true,
# "rating": {
# "reviewsCount": 21,
# "reviewsWithScoreCount": 12,
# "score": 4.3
# }
# }
class Rating(AvitoObject):
    reviews_count: int = Field(
        alias='reviewsCount',
        description='Общее количество активных отзывов',
        example=21
    )
    reviews_with_score_count: int = Field(
        alias='reviewsWithScoreCount',
        description='Количество активных отзывов, влияющих на формирование рейтинга',
        example=12,
    )
    score: float = Field(description='Оценка рейтинга', example=4.3)


class RatingInfo(AvitoObject):
    """
    Рейтинг
    """
    is_enabled: bool = Field(
        alias='isEnabled',
        description='Включен ли рейтинг',
        example=True
    )
    rating: Rating | None = None
