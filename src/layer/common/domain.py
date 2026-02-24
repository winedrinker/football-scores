from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class SportEvent(BaseModel):
    model_config = ConfigDict(frozen=True, alias_generator=to_camel)

    match_id: int = Field(gt=0)
    team_home: str = Field(min_length=1)
    team_away: str = Field(min_length=1)
    score: str = Field(pattern=r"^(\d+):(\d+)$")
    timestamp: datetime