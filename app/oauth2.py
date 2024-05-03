from jose import JWTError, jwt 
from datetime import datetime, timedelta, timezone
from . import schemas, database, models
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os

# Ponemos login porque es la ruta donde se encuentra el endpoint para hacer login.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Secret key (es la que está en nuestro servidor)

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
SECRET_KEY = os.getenv("SECRET_KEY")
# Algoritmo para crear el token 
ALGORITHM = "HS256"
ALGORITHM = os.getenv("ALGORITHM")
# Expiration time (cuanto tiempo dura el token) (cuanto tiempo esta logeado el usuario)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

def create_access_token(data: dict):
    to_encode = data.copy()
    # Cuando va a terminar la sesión del usuario
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Añadimos la información de expiración del usuario al diccionario.
    to_encode.update({"exp": expire})
    # Creamos el token con toda la información que requermos
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")

        if id == None:
            raise credentials_exception 
        
        # Guardamos la data del token con la clase de TokenData
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    
    # Devolvemos el token que es un diccionario con el id
    return token_data
    

# Con esta función podemos acceder a la información del usuario que está loggeado en el momento.
def get_current_user(token:str = Depends(oauth2_scheme), db: Session=Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"No se pudieron validar las credenciales",
                                          headers={"WWW-Authenticate": "Bearer"})
    
    token = verify_access_token(token, credentials_exception)
    user = db.query(models.Users).filter(models.Users.id == token.id).first()

    return user

