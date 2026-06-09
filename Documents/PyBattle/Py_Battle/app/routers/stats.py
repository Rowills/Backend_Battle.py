from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.battle import Battle
from app.models.user import User

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(User).all()
    result = []
    for user in users:
        wins = db.query(Battle).filter(
            Battle.winner_id == user.id,
            Battle.status == "completed"
        ).count()
        total = db.query(Battle).filter(
            (Battle.player1_id == user.id) | (Battle.player2_id == user.id),
            Battle.status == "completed"
        ).count()
        losses = total - wins
        if total > 0:
            result.append({
                "user_id": user.id,
                "username": user.username,
                "wins": wins,
                "losses": losses,
                "total": total,
                "win_rate": round((wins / total) * 100) if total > 0 else 0,
            })
    result.sort(key=lambda x: (x["wins"], x["win_rate"]), reverse=True)
    return result


@router.get("/profile/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    wins = db.query(Battle).filter(
        Battle.winner_id == user_id,
        Battle.status == "completed"
    ).count()
    total = db.query(Battle).filter(
        (Battle.player1_id == user_id) | (Battle.player2_id == user_id),
        Battle.status == "completed"
    ).count()
    losses = total - wins

    recent = db.query(Battle).filter(
        (Battle.player1_id == user_id) | (Battle.player2_id == user_id),
        Battle.status == "completed"
    ).order_by(Battle.created_at.desc()).limit(5).all()

    recent_list = []
    for b in recent:
        recent_list.append({
            "battle_id": b.id,
            "problem_id": b.problem_id,
            "result": "win" if b.winner_id == user_id else "loss",
        })

    return {
        "user_id": user.id,
        "username": user.username,
        "wins": wins,
        "losses": losses,
        "total": total,
        "win_rate": round((wins / total) * 100) if total > 0 else 0,
        "recent_battles": recent_list,
    }


@router.post("/battle/{battle_id}/result")
def record_result(battle_id: int, winner_id: int, db: Session = Depends(get_db)):
    battle = db.query(Battle).filter(Battle.id == battle_id).first()
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    battle.winner_id = winner_id
    battle.status = "completed"
    db.commit()
    return {"message": "Result recorded"}
