from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.battle import Battle
from pydantic import BaseModel

router = APIRouter(prefix="/battles", tags=["battles"])

class CreateBattleRequest(BaseModel):
    problem_id: int

@router.post("/create")
def create_battle(player1_id: int, body: CreateBattleRequest, db: Session = Depends(get_db)):
    battle = Battle(player1_id=player1_id, problem_id=body.problem_id, status="waiting")
    db.add(battle)
    db.commit()
    db.refresh(battle)
    return battle

@router.post("/join/{battle_id}")
def join_battle(battle_id: int, player2_id: int, db: Session = Depends(get_db)):
    battle = db.query(Battle).filter(Battle.id == battle_id).first()
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    if battle.status != "waiting":
        raise HTTPException(status_code=400, detail="Battle already started")
    battle.player2_id = player2_id
    battle.status = "active"
    db.commit()
    db.refresh(battle)
    return battle

@router.get("/list")
def list_battles(db: Session = Depends(get_db)):
    return db.query(Battle).filter(Battle.status == "waiting").all()
