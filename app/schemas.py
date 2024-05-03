from pydantic import BaseModel, EmailStr
from datetime import datetime



# Definir el modelo de datos para un post
class PostBase(BaseModel):
    title: str  # Título del post (str)
    content: str  # Contenido del post (str)
## Esto es PostBase tal cual. 
## A veces es bueno crear clases nuevas para cada acción que queramos hacer.
class PostCreate(PostBase):
    pass

class UserResponse(BaseModel):
    id: int
    email: EmailStr  #No nos interesa mandarle la contraseña al usuario, solo el email
    created_at: datetime
    class Config:
        from_attributes = True

class PostResponse(PostBase):
    # Estos son los campos que voy a recibir en mi respuesta.
    ## Solo ponemos id y created_at porque los otros vienen inheritados de PostBase
    id: int
    created_at: datetime
    user_id: int

    
    ## Esto es jodido.
    ## Esto de user viene de lo de relationship en el model de posts
    user: UserResponse


    # De esta forma la respuesta puede ser un objeto de Sqlalchemy
    ## Es decir lo va a convertir en un diccionario válido en la respuesta.
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int | None = None

class Vote(BaseModel):
    post_id: int
    liked_it: bool