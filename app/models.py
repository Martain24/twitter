from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from .database import Base 

# Con esto de aquí creamos la tabla Posts en nuestra base de datos.
# Si en la base de datos ya está creada entonces no hace nada
# Si no está en la base de datos la crea de cero.
# Si hay una tabla con __tablename__ entonces no hace nada aunque tenga diferente estructura
class Posts(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    ### Esto no cambia la base de datos.
    ### Simplemente le pasamos el nombre de la clase que define la tabla "users"
    ### De esta forma obtenemos información relacionada con la otra tabla y el "user_id"
    user = relationship("Users")

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)

class Votes(Base):
    __tablename__ = "votes"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                     primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"),
                     primary_key=True)
    liked_it = Column(Boolean, nullable=False)




