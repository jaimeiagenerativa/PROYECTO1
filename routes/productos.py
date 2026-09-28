"""
Rutas (Endpoints) para gestionar Productos.
Define todos los endpoints REST de la API.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from database import get_db
from services.producto_service import (
    ProductoService,
    ProductoNotFoundException,
    ProductoDuplicateException,
    ProductoValidationException,
)
from schemas.producto import (
    ProductoCreate,
    ProductoUpdate,
    ProductoResponse,
    ProductoListResponse,
    SuccessResponse,
    ErrorResponse,
    ErrorDetail,
    CategoriaEnum,
)
from typing import List

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get(
    "",
    response_model=ProductoListResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener todos los productos",
    description="Retorna un listado paginado de todos los productos",
)
async def obtener_todos(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Límite de registros"),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener todos los productos con paginación.
    
    - **skip**: Número de registros a saltar (default: 0)
    - **limit**: Límite de registros a retornar (default: 10, máximo: 100)
    """
    try:
        service = ProductoService(db)
        return await service.obtener_todos_productos(skip=skip, limit=limit)
    except ProductoValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/activos",
    response_model=ProductoListResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener productos activos",
    description="Retorna un listado paginado de productos activos",
)
async def obtener_activos(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Límite de registros"),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener solo productos activos.
    
    - **skip**: Número de registros a saltar (default: 0)
    - **limit**: Límite de registros a retornar (default: 10, máximo: 100)
    """
    try:
        service = ProductoService(db)
        return await service.obtener_activos(skip=skip, limit=limit)
    except ProductoValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/categoria/{categoria}",
    response_model=ProductoListResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener productos por categoría",
    description="Retorna un listado paginado de productos por categoría",
)
async def obtener_por_categoria(
    categoria: str,
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Límite de registros"),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener productos por categoría específica.
    
    - **categoria**: Categoría del producto (ELECTRONICA, ROPA, ALIMENTOS, LIBROS, DEPORTES, HOGAR, OTROS)
    - **skip**: Número de registros a saltar (default: 0)
    - **limit**: Límite de registros a retornar (default: 10, máximo: 100)
    """
    try:
        service = ProductoService(db)
        return await service.obtener_por_categoria(categoria=categoria, skip=skip, limit=limit)
    except ProductoValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/stock-bajo",
    response_model=ProductoListResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener productos con stock bajo",
    description="Retorna un listado paginado de productos con stock bajo",
)
async def obtener_stock_bajo(
    limite_stock: int = Query(5, ge=0, description="Límite de stock considerado bajo"),
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Límite de registros"),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener productos con stock bajo.
    
    - **limite_stock**: Límite de stock considerado como bajo (default: 5)
    - **skip**: Número de registros a saltar (default: 0)
    - **limit**: Límite de registros a retornar (default: 10, máximo: 100)
    """
    try:
        service = ProductoService(db)
        return await service.obtener_con_stock_bajo(
            limite_stock=limite_stock, skip=skip, limit=limit
        )
    except ProductoValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{producto_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener producto por ID",
    description="Retorna los detalles de un producto específico",
)
async def obtener_por_id(
    producto_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener un producto específico por su ID.
    
    - **producto_id**: ID único del producto (requerido)
    """
    try:
        service = ProductoService(db)
        producto = await service.obtener_producto(producto_id)
        return SuccessResponse(
            status="success",
            data=producto,
            timestamp=datetime.utcnow(),
        )
    except ProductoNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo producto",
    description="Crea un nuevo producto en el sistema",
)
async def crear_producto(
    producto_data: ProductoCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Crear un nuevo producto.
    
    Validaciones:
    - El código debe ser único
    - El precio debe ser mayor a 0
    - El stock debe ser >= 0
    - Todos los campos son requeridos
    """
    try:
        service = ProductoService(db)
        producto = await service.crear_producto(producto_data)
        return SuccessResponse(
            status="success",
            data=producto,
            timestamp=datetime.utcnow(),
        )
    except ProductoDuplicateException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except ProductoValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/{producto_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar producto",
    description="Actualiza los datos de un producto existente",
)
async def actualizar_producto(
    producto_id: int,
    producto_data: ProductoUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Actualizar un producto existente.
    
    - **producto_id**: ID del producto a actualizar (requerido)
    - **producto_data**: Datos a actualizar (todos los campos son opcionales)
    
    Validaciones:
    - Si se actualiza el código, debe ser único
    - Si se actualiza el precio, debe ser > 0
    - Si se actualiza el stock, debe ser >= 0
    """
    try:
        service = ProductoService(db)
        producto = await service.actualizar_producto(producto_id, producto_data)
        return SuccessResponse(
            status="success",
            data=producto,
            timestamp=datetime.utcnow(),
        )
    except ProductoNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ProductoDuplicateException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except ProductoValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar producto",
    description="Elimina un producto del sistema",
)
async def eliminar_producto(
    producto_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Eliminar un producto.
    
    - **producto_id**: ID del producto a eliminar (requerido)
    """
    try:
        service = ProductoService(db)
        await service.eliminar_producto(producto_id)
        return None
    except ProductoNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
