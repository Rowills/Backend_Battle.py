from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.battle import Battle
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/battles", tags=["battles"])

# Battles older than this with no second player are considered abandoned
BATTLE_EXPIRY_MINUTES = 10

def cleanup_stale_battles(db: Session):
    """Delete waiting battles older than BATTLE_EXPIRY_MINUTES."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=BATTLE_EXPIRY_MINUTES)
    db.query(Battle).filter(
        Battle.status == "waiting",
        Battle.created_at < cutoff
    ).delete(synchronize_session=False)
    db.commit()

class CreateBattleRequest(BaseModel):
    problem_id: int

@router.post("/create")
def create_battle(player1_id: int, body: CreateBattleRequest, db: Session = Depends(get_db)):
    # Clean up stale battles on every create
    cleanup_stale_battles(db)
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
    # Clean up stale battles on every list fetch too
    cleanup_stale_battles(db)
    # Return most recent 10 waiting battles only
    return (
        db.query(Battle)
        .filter(Battle.status == "waiting")
        .order_by(Battle.created_at.desc())
        .limit(10)
        .all()
    )

@router.delete("/cleanup")
def manual_cleanup(db: Session = Depends(get_db)):
    """Manual trigger to wipe all stale waiting battles."""
    cleanup_stale_battles(db)
    return {"message": "Stale battles cleaned up"}
