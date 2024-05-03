from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: int | None

while True:
    try:
        conn = psycopg2.connect(host="localhost", database="fastapi_db", user="postgres",
                                password="contraseña123", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Db connection ok")
        break 
    except Exception as error:
        # Esto lo ponemos porque quizás tenemos mal el internet y entonces necesita probar varias veces para conectar.
        print(f"Error: {error}")
        time.sleep(2)

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "favorite foods", "content": "pizza hamburguesa", "id": 2}]

def find_post(id: int):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_post(id: int):
    for index,p in enumerate(my_posts):
        if p["id"] == id:
            return index

@app.get("/")
def root():
    return {"message": "Hello world"}

@app.get("/posts")
def get_posts():
    # Con esto ejecutamos la query
    cursor.execute("""SELECT * FROM posts""")
    # Después hacemos el fetchall para obtener todas las filas de la query
    my_posts = cursor.fetchall()
    return {"data": my_posts}


# Cambiamos a 201 porque estamos creando un post y es convención poner una response de 201
# Sigue siendo la ruta de "/posts" como arriba, pero esté método es POST, por tanto, es perfecto
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(new_post: Post):

    # Hacemos esto así en vez de con f string para evitar que los usuarios puedan poner SQL querys y jodernos la database
    # Ponemos RETURNING * al final para que nos devuelva los valores que acabamos de subir
    cursor.execute("""INSERT INTO posts (title, content, published, rating) VALUES (%s, %s, %s, %s) RETURNING *""",
                   (new_post.title, new_post.content, new_post.published, new_post.rating))
    
    # Tenemos que hacer lo de fetchone() para efectivamente guardar los datos que metimos en la varible
    new_post = cursor.fetchone()

    # Con el commit conseguimos que se guarden de verdad los datos en la database (es como hacer el push final en github)
    conn.commit()

    return {"data": new_post}



@app.get("/posts/{id}")
def get_post(id: int):
    # Hay que convertirlo a string para meterlo en la query.
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id), ))
    post_to_get = cursor.fetchone()
    if post_to_get == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return {"data": post_to_get}

### Llevas 4 horas y 24 minutos, ni más ni menos.

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE from posts WHERE id = %s RETURNING *""",
                   (str(id), ))
    post_to_delete = cursor.fetchone()
    if post_to_delete == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} does not exist")
    
    # Ejecutamos el commit para que se borre en la base de datos
    conn.commit()

    # Tenemos que poner esto.
    ## Cuando es un 204 el sistema espera no devolver nada. Si ponemos algo dará error
    ## Ponemos esto simplemente por convención para que no aparezca nada.
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s, rating = %s WHERE id = %s RETURNING *""",
                   (post.title, post.content, post.published, post.rating, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} does not exist")

    return {"data": updated_post}


## 2 horas y 18 minutos.



