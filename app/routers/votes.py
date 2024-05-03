from .. import database, schemas, models, utils, oauth2
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List

# Creamos instancia de router que importaremos en main.
router = APIRouter(
    prefix="/votes",
    tags=["Votes"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db:Session = Depends(database.get_db),
         current_user = Depends(oauth2.get_current_user)):

    post_exists = db.query(models.Posts).filter(models.Posts.id==vote.post_id).first() != None
    if not post_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with (id = {vote.post_id}) does not exists")

    voted = db.query(models.Votes).filter(models.Votes.user_id==current_user.id, models.Votes.post_id==vote.post_id)
    if voted.first()!=None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with (id = {current_user.id}) has alredy voted on post with (id = {vote.post_id})")
    
    new_vote = models.Votes(**vote.model_dump(), user_id=current_user.id)
    db.add(new_vote)
    db.commit()
    return {"Success": "Voted successfully "}
