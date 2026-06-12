from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.comment import Comment
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/comments", tags=["comments"])

class CommentCreate(BaseModel):
    user_id: int
    username: str
    content: str

class CommentResponse(BaseModel):
    id: int
    user_id: int
    username: str
    content: str
    created_at: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[dict])
def get_comments(db: Session = Depends(get_db)):
    comments = db.query(Comment).order_by(Comment.created_at.desc()).limit(50).all()
    return [
        {
            "id": c.id,
            "user_id": c.user_id,
            "username": c.username,
            "content": c.content,
            "created_at": str(c.created_at),
        }
        for c in comments
    ]

@router.post("/")
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    if not comment.content.strip():
        raise HTTPException(status_code=400, detail="Comment cannot be empty")
    if len(comment.content) > 300:
        raise HTTPException(status_code=400, detail="Comment too long (max 300 chars)")
    new_comment = Comment(
        user_id=comment.user_id,
        username=comment.username,
        content=comment.content.strip(),
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return {"id": new_comment.id, "message": "Comment posted!"}

@router.delete("/{comment_id}")
def delete_comment(comment_id: int, user_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own comments")
    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted"}
