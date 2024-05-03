# Esto siempre lo vamos a copiar en cualquier proyecto de databases
# Lo único que vamos a tener que cambiar es la SQLALCHEMY_DATABASE_URL
# Piensa en este código como un copy paste siempre para poder acceder a la db con sqlalchemy.

from sqlalchemy import create_engine 
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker 

# El username es postgres porque es por defecto y no lo he cambiado
username = "postgres"
# La contraseña que puse es esta
contraseña = "contraseña123"
# Esto es el ip-addres que en este caso es simplemente hostname
ip_address_hostname = "localhost"
# NOmbre de la database
db_name = "fastapi_db"
import os
os.getenv("DATABASE_URL")
SQLALCHEMY_DATABASE_URL = f"postgresql://{username}:{contraseña}@{ip_address_hostname}/{db_name}"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
print(SQLALCHEMY_DATABASE_URL)
# Creamos conexión con la database y sqlalchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Esto simplemente abre una sesión con nuestra database
## Es mejor hacerlo así porque podemos usar python code en vez de sql
## Además es más eficiente.
## Piensa en este código como algo que no entiendes del todo, pero que es igual siempre.
def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()
