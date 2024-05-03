from .. import models, schemas, oauth2
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List, Tuple
import pandas as pd

# Creamos instancia de router que importaremos en main.
router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

def get_num_likes_num_dislikes(series_posts, db):
    list_posts_likes = []
    def get_nums(p):
        num_likes = len(db.query(models.Votes).filter(models.Votes.post_id==p.id, models.Votes.liked_it==True).all())
        num_dislikes = len(db.query(models.Votes).filter(models.Votes.post_id==p.id, models.Votes.liked_it==False).all())
        list_posts_likes.append((p, {"num_likes": num_likes, "num_dislikes": num_dislikes}))
    series_posts.apply(get_nums)
    return list_posts_likes

@router.get("/", response_model=List[Tuple[schemas.PostResponse, dict]])  ##Le decimos que queremos una lista de Post en la respuesta
def get_posts(limit:int = 10, db:Session = Depends(get_db),
              search_title:str = ""):
    # Con query simplemente "escribimos" sql. Con all() obtenemos todo lo de la query
    posts = pd.Series(list(db.query(models.Posts).filter(models.Posts.title.contains(search_title)).limit(limit).all()))
    return get_num_likes_num_dislikes(posts, db)

@router.get("/{user_id}", response_model=List[Tuple[schemas.PostResponse, dict]])
def get_user_posts(user_id:int, db: Session=Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    user_posts = db.query(models.Posts).filter(models.Posts.user_id == user_id).all()
    if user_posts == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with (id = {user_id}) does not have posts")
    return user_posts



# Cambiamos a 201 porque estamos creando un post y es convención poner una response de 201
# Sigue siendo la ruta de "/posts" como arriba, pero esté método es POST, por tanto, es perfecto
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)  # Ponemos lo de response model para que la respuesta sea como queremos .
def create_post(new_post: schemas.PostCreate, db: Session=Depends(get_db),
                current_user:dict = Depends(oauth2.get_current_user)):
    # De esta forma vemos si el usuario está logeado o no y si puede acceder o no.
    print(current_user.email)
    # Creamos un nuevo post con la clase Posts de models. Convertimos a dict con model_dump()
    new_post = new_post.model_dump()
    new_post["user_id"] = current_user.id  # Añadimos el user_id correspondiente
    new_post = models.Posts(**new_post)
    # Añadimos el nuevo post a la database
    db.add(new_post)
    # Hacemos commit para que se guarde el cambio
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/one/{id}", response_model=Tuple[schemas.PostResponse, dict]) #response_model=schemas.PostResponse)
def get_post(id: int, db: Session=Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    # Es mejor poner first() para que sea eficiente
    post_to_get = db.query(models.Posts).filter(models.Posts.id == id).first()
    if post_to_get == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with (id = {id}) was not found")
    num_likes = len(db.query(models.Votes).filter(models.Votes.post_id==id, models.Votes.liked_it==True).all())
    num_dislikes = len(db.query(models.Votes).filter(models.Votes.post_id==id, models.Votes.liked_it==False).all())
    return post_to_get, {"num_likes": num_likes, "num_dislikes": num_dislikes}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session=Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    post_to_delete = db.query(models.Posts).filter(models.Posts.id == id)

    if post_to_delete.first().user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_UNAUTHORIZED, 
                            detail=f"You cannot delete a post that is not yours")
    if post_to_delete.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} does not exist")
    # Eliminamos el post y hacemos commit. Lo de synchr... es por eficiencia.
    post_to_delete.delete(synchronize_session=False)
    db.commit()

    # Tenemos que poner esto.
    ## Cuando es un 204 el sistema espera no devolver nada. Si ponemos algo dará error
    ## Ponemos esto simplemente por convención para que no aparezca nada.
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, db: Session=Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    # Recuerda que esto es simplemente una query
    post_to_update = db.query(models.Posts).filter(models.Posts.id == id)

    if post_to_update.first().user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_UNAUTHORIZED, 
                            detail=f"You cannot update a post that is not yours")
    
    if post_to_update.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} does not exist")
    # Hacemos el update con el método update de la query
    post_to_update.update(post.model_dump(), synchronize_session=False)
    # Hacemos commit
    db.commit()
    return post_to_update.first()

