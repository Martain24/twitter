from fastapi import APIRouter, Depends, status, HTTPException, Response 
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2

router = APIRouter(tags=["Autentificación"])

@router.post("/login", response_model=schemas.Token)
def login(user_credentials:OAuth2PasswordRequestForm=Depends(), db: Session=Depends(database.get_db)):
    ## OAuth2PasswordRequestFormStrict va a devolver un diccionario con username y con password
    user = db.query(models.Users).filter(models.Users.email == user_credentials.username).first()

    if user == None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid email or password")  #No queremos que sepan en que falló exactamente
    
    if utils.verify(plain_password=user_credentials.password, hashed_password=user.password) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid email or password")  #No queremos que sepan en que falló exactamente
    
    # Create token. En este caso solo pasamos el "id" del usuario para crear el token.
    ## Podiamos haberle pasado más información como email y tal (pero nunca contraseña)
    ## Nunca contraseña porque sino el token se puede sacar la información.
    ## Incluso mejor ni pasar el email la verdad....
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    # return token
    return {"access_token": access_token, "token_type": "bearer"}
