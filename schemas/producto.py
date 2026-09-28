"""
Esquemas Pydantic para validación de Producto.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CategoriaEnum(str, Enum):
    """Enumeración de categorías válidas."""
    ELECTRONICA = "ELECTRONICA"
    ROPA = "ROPA"
    ALIMENTOS = "ALIMENTOS"
    LIBROS = "LIBROS"
    DEPORTES = "DEPORTES"
    HOGAR = "HOGAR"
    OTROS = "OTROS"


class ProductoBase(BaseModel):
    """Esquema base con campos comunes."""
    
    codigo: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Código único del producto"
    )
    nombre: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nombre del producto"
    )
    precio: float = Field(
        ...,
        gt=0,
        description="Precio del producto (debe ser mayor a 0)"
    )
    stock: int = Field(
        ...,
        ge=0,
        description="Cantidad disponible (debe ser >= 0)"
    )
    categoria: CategoriaEnum = Field(
        ...,
        description="Categoría del producto"
    )
    proveedor: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nombre del proveedor"
    )
    activo: bool = Field(
        default=True,
        description="Estado operativo del producto"
    )
    
    @validator('nombre')
    def nombre_no_vacio(cls, v):
        """Validar que el nombre no sea solo espacios."""
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()
    
    @validator('codigo')
    def codigo_no_vacio(cls, v):
        """Validar que el código no sea solo espacios."""
        if not v.strip():
            raise ValueError('El código no puede estar vacío')
        return v.strip().upper()
    
    @validator('proveedor')
    def proveedor_no_vacio(cls, v):
        """Validar que el proveedor no sea solo espacios."""
        if not v.strip():
            raise ValueError('El proveedor no puede estar vacío')
        return v.strip()


class ProductoCreate(ProductoBase):
    """Esquema para crear un producto (sin id ni timestamps)."""
    pass


class ProductoUpdate(BaseModel):
    """Esquema para actualizar un producto (todos los campos opcionales)."""
    
    codigo: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="Código único del producto"
    )
    nombre: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Nombre del producto"
    )
    precio: Optional[float] = Field(
        None,
        gt=0,
        description="Precio del producto"
    )
    stock: Optional[int] = Field(
        None,
        ge=0,
        description="Cantidad disponible"
    )
    categoria: Optional[CategoriaEnum] = Field(
        None,
        description="Categoría del producto"
    )
    proveedor: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Nombre del proveedor"
    )
    activo: Optional[bool] = Field(
        None,
        description="Estado operativo del producto"
    )
    
    @validator('nombre')
    def nombre_no_vacio(cls, v):
        """Validar que el nombre no sea solo espacios."""
        if v is not None and not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip() if v else v
    
    @validator('codigo')
    def codigo_no_vacio(cls, v):
        """Validar que el código no sea solo espacios."""
        if v is not None and not v.strip():
            raise ValueError('El código no puede estar vacío')
        return v.strip().upper() if v else v
    
    @validator('proveedor')
    def proveedor_no_vacio(cls, v):
        """Validar que el proveedor no sea solo espacios."""
        if v is not None and not v.strip():
            raise ValueError('El proveedor no puede estar vacío')
        return v.strip() if v else v


class ProductoResponse(ProductoBase):
    """Esquema de respuesta con id y timestamps."""
    
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True


class ProductoListResponse(BaseModel):
    """Esquema para respuesta de listado con paginación."""
    
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Registros saltados")
    limit: int = Field(..., description="Límite de registros")
    items: List[ProductoResponse] = Field(..., description="Lista de productos")


class ErrorDetail(BaseModel):
    """Esquema para detalles de error."""
    
    field: str = Field(..., description="Campo con error")
    error: str = Field(..., description="Mensaje de error")


class ErrorResponse(BaseModel):
    """Esquema de respuesta de error."""
    
    status: str = Field(default="error", description="Estado de la respuesta")
    code: str = Field(..., description="Código de error")
    message: str = Field(..., description="Mensaje de error")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detalles del error")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp del error")


class SuccessResponse(BaseModel):
    """Esquema de respuesta exitosa."""
    
    status: str = Field(default="success", description="Estado de la respuesta")
    data: ProductoResponse = Field(..., description="Datos del producto")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp")
