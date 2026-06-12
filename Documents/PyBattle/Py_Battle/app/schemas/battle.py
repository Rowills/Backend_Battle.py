from pydantic import BaseModel
from typing import Optional

class BattleCreate(BaseModel):
    problem_id: int

class BattleResponse(BaseModel):
    id: int
    player1_id: Optional[int]
    player2_id: Optional[int]
    problem_id: int
    status: str
    winner_id: Optional[int]

    class Config:
        from_attributes = True
