from pydantic import BaseModel

from avito.base.context_controller import BotContextController


class AvitoObject(BotContextController, BaseModel):
    pass