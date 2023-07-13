from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from dotenv import load_dotenv

import os

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pydantic import BaseModel

load_dotenv()

# Configuración de la base de datos
DATABASE_URL = f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class OdooOracleErrors(Base):
    __tablename__='odoo_oracle_errors'

    id = Column(Integer, primary_key=True, nullable=False)
    order = Column(String(50), unique=True, nullable=False)
    error_message = Column(String(255))

Base.metadata.create_all(bind=engine)

class OdooOracleError(BaseModel):
    order: str
    error_message: str

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def hello_world():
    return {"message": "Hello World"}

# Ruta para crear un nuevo registro
@app.post("/errors_odoo")
def create_error(error_object: OdooOracleError):
    # Crea una sesión para la operación
    db = SessionLocal()

    # Crea una instancia de OdooOracleErrors
    new_error = OdooOracleErrors(order=error_object.order, error_message=error_object.error_message)

    # Guarda el nuevo registro en la base de datos
    db.add(new_error)
    db.commit()
    db.refresh(new_error)

    return new_error

@app.get("/errors_odoo")
def get_all_errors():
    # Crea una sesión para la operación
    db = SessionLocal()

    # Busca el registro por su ID
    error = db.query(OdooOracleErrors).all()

    # Si no se encuentra el registro, devuelve un error 404
    if not error:
        raise HTTPException(status_code=404, detail="Error not found")

    return error

# Ruta para obtener un registro por su Pedido
@app.get("/errors_odoo/{order}")
def get_error(order: str):
    # Crea una sesión para la operación
    db = SessionLocal()

    # Busca el registro por su ID
    error = db.query(OdooOracleErrors).filter(OdooOracleErrors.order == order).first()

    # Si no se encuentra el registro, devuelve un error 404
    if not error:
        raise HTTPException(status_code=404, detail="Error not found")

    return error


# Ruta para actualizar un registro por su Pedido
@app.put("/errors_odoo/{order}")
def update_error(error_object: OdooOracleError):
    # Crea una sesión para la operación
    db = SessionLocal()

    # Busca el registro por su ID
    error = db.query(OdooOracleErrors).filter(OdooOracleErrors.order == error_object.order).first()

    # Si no se encuentra el registro, devuelve un error 404
    if not error:
        raise HTTPException(status_code=404, detail="Error not found")

    # Actualiza los campos del registro
    error.order = error_object.order
    error.error_message = error_object.error_message

    # Guarda los cambios en la base de datos
    db.commit()
    db.refresh(error)

    return error


# Ruta para eliminar un registro por su Pedido
@app.delete("/errors_odoo/{order}")
def delete_error(order: str):
    # Crea una sesión para la operación
    db = SessionLocal()

    # Busca el registro por su ID
    error = db.query(OdooOracleErrors).filter(OdooOracleErrors.order == order).first()

    # Si no se encuentra el registro, devuelve un error 404
    if not error:
        raise HTTPException(status_code=404, detail="Error not found")

    # Elimina el registro de la base de datos
    db.delete(error)
    db.commit()

    return {"message": "Error deleted"}