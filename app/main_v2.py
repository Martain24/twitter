from fastapi import FastAPI
from . import models
from .database import engine
from .routers import posts, users, auth, votes

# Esto es lo que crea las databases que tengamos en models.py
models.Base.metadata.create_all(bind=engine)

# Inicializar la aplicación FastAPI
app = FastAPI()

# Incluimos las rutas de los diferentes routers.
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(votes.router)

@app.get("/")
def root():
    return {"message": "Hello world"}

