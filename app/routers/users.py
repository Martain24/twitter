from .. import models, schemas, utils
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db

# Creamos instancia de router que importaremos en main.
router = APIRouter(
    prefix="/users",
    tags=["Users"] # Con esto la swagger gui se mejora y se distribuyen en Posts y Users.
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session=Depends(get_db)):
    # Hash password 
    hashed_pass = utils.hash(user.password)
    user.password = hashed_pass

    new_user = models.Users(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user 

@router.get("/{id}", response_model=schemas.UserResponse)  ##UserResponse para no mandar contraseña
def get_user(id: int, db: Session = Depends(get_db)):
    user_to_get = db.query(models.Users).filter(models.Users.id == id).first()

    if user_to_get == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with (id = {id}) does not exist")
    
    return user_to_get