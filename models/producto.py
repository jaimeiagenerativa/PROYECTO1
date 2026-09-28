"""
Modelo SQLAlchemy para la entidad Producto.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
from database import Base
import enum


class CategoriaEnum(str, enum.Enum):
    """Enumeración de categorías válidas."""
    ELECTRONICA = "ELECTRONICA"
    ROPA = "ROPA"
    ALIMENTOS = "ALIMENTOS"
    LIBROS = "LIBROS"
    DEPORTES = "DEPORTES"
    HOGAR = "HOGAR"
    OTROS = "OTROS"


class Producto(Base):
    """
    Modelo de Producto para la base de datos.
    
    Atributos:
        id: Identificador único (PK, AutoIncrement)
        codigo: Código único del producto
        nombre: Nombre del producto
        precio: Precio del producto
        stock: Cantidad disponible
        categoria: Categoría del producto
        proveedor: Nombre del proveedor
        activo: Estado operativo del producto
        fecha_creacion: Timestamp de creación
        fecha_actualizacion: Timestamp de última actualización
    """
    
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    categoria = Column(SQLEnum(CategoriaEnum), nullable=False)
    proveedor = Column(String(100), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self):
        return f"<Producto(id={self.id}, codigo={self.codigo}, nombre={self.nombre})>"
