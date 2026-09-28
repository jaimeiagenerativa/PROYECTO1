"""
Service Layer para Producto.
Contiene lógica de negocio, validaciones y orquestación.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from repositories.producto_repository import ProductoRepository
from schemas.producto import ProductoCreate, ProductoUpdate, ProductoResponse, ProductoListResponse
from models.producto import Producto
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProductoNotFoundException(Exception):
    """Excepción cuando un producto no es encontrado."""
    pass


class ProductoDuplicateException(Exception):
    """Excepción cuando hay un código duplicado."""
    pass


class ProductoValidationException(Exception):
    """Excepción para validaciones de negocio."""
    pass


class ProductoService:
    """Service para gestionar la lógica de Producto."""
    
    def __init__(self, db: AsyncSession):
        """
        Inicializar el servicio con una sesión de BD.
        
        Args:
            db: Sesión AsyncSession de SQLAlchemy
        """
        self.repository = ProductoRepository(db)
        self.db = db
    
    async def crear_producto(self, producto_data: ProductoCreate) -> ProductoResponse:
        """
        Crear un nuevo producto con validaciones de negocio.
        
        Args:
            producto_data: Datos del producto a crear
            
        Returns:
            Producto creado como ProductoResponse
            
        Raises:
            ProductoDuplicateException: Si el código ya existe
            ProductoValidationException: Si hay validaciones fallidas
        """
        try:
            # Validar que el código no exista
            existe = await self.repository.existe_codigo(producto_data.codigo)
            if existe:
                logger.warning(f"Intento de crear producto con código duplicado: {producto_data.codigo}")
                raise ProductoDuplicateException(
                    f"El código '{producto_data.codigo}' ya existe en el sistema"
                )
            
            # Validaciones de negocio
            if producto_data.precio <= 0:
                raise ProductoValidationException("El precio debe ser mayor a 0")
            
            if producto_data.stock < 0:
                raise ProductoValidationException("El stock no puede ser negativo")
            
            # Crear el producto
            producto = await self.repository.crear(producto_data)
            await self.db.commit()
            
            logger.info(f"Producto creado: ID={producto.id}, Código={producto.codigo}")
            return ProductoResponse.from_orm(producto)
        
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Error de integridad al crear producto: {str(e)}")
            if "codigo" in str(e).lower() or "unique" in str(e).lower():
                raise ProductoDuplicateException("El código del producto ya existe")
            raise ProductoValidationException("Error en la validación de datos")
        
        except (ProductoDuplicateException, ProductoValidationException):
            await self.db.rollback()
            raise
    
    async def obtener_producto(self, producto_id: int) -> ProductoResponse:
        """
        Obtener un producto por ID.
        
        Args:
            producto_id: ID del producto
            
        Returns:
            Producto como ProductoResponse
            
        Raises:
            ProductoNotFoundException: Si no existe
        """
        producto = await self.repository.obtener_por_id(producto_id)
        
        if not producto:
            logger.warning(f"Producto no encontrado: ID={producto_id}")
            raise ProductoNotFoundException(f"Producto con ID {producto_id} no encontrado")
        
        return ProductoResponse.from_orm(producto)
    
    async def obtener_todos_productos(
        self, skip: int = 0, limit: int = 10
    ) -> ProductoListResponse:
        """
        Obtener todos los productos con paginación.
        
        Args:
            skip: Número de registros a saltar
            limit: Límite de registros (máximo 100)
            
        Returns:
            Respuesta paginada con productos
            
        Raises:
            ProductoValidationException: Si los parámetros son inválidos
        """
        # Validar parámetros
        if skip < 0:
            raise ProductoValidationException("skip no puede ser negativo")
        
        if limit < 1 or limit > 100:
            raise ProductoValidationException("limit debe estar entre 1 y 100")
        
        productos, total = await self.repository.obtener_todos(skip, limit)
        
        items = [ProductoResponse.from_orm(p) for p in productos]
        
        return ProductoListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=items
        )
    
    async def obtener_por_categoria(
        self, categoria: str, skip: int = 0, limit: int = 10
    ) -> ProductoListResponse:
        """
        Obtener productos por categoría.
        
        Args:
            categoria: Categoría del producto
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Respuesta paginada con productos
        """
        if skip < 0:
            raise ProductoValidationException("skip no puede ser negativo")
        
        if limit < 1 or limit > 100:
            raise ProductoValidationException("limit debe estar entre 1 y 100")
        
        productos, total = await self.repository.obtener_por_categoria(
            categoria, skip, limit
        )
        
        items = [ProductoResponse.from_orm(p) for p in productos]
        
        return ProductoListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=items
        )
    
    async def obtener_activos(
        self, skip: int = 0, limit: int = 10
    ) -> ProductoListResponse:
        """
        Obtener solo productos activos.
        
        Args:
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Respuesta paginada con productos activos
        """
        if skip < 0:
            raise ProductoValidationException("skip no puede ser negativo")
        
        if limit < 1 or limit > 100:
            raise ProductoValidationException("limit debe estar entre 1 y 100")
        
        productos, total = await self.repository.obtener_activos(skip, limit)
        
        items = [ProductoResponse.from_orm(p) for p in productos]
        
        return ProductoListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=items
        )
    
    async def actualizar_producto(
        self, producto_id: int, producto_data: ProductoUpdate
    ) -> ProductoResponse:
        """
        Actualizar un producto existente.
        
        Args:
            producto_id: ID del producto a actualizar
            producto_data: Nuevos datos del producto
            
        Returns:
            Producto actualizado como ProductoResponse
            
        Raises:
            ProductoNotFoundException: Si no existe
            ProductoDuplicateException: Si el código ya existe en otra entidad
            ProductoValidationException: Si hay validaciones fallidas
        """
        try:
            # Verificar que el producto existe
            producto = await self.repository.obtener_por_id(producto_id)
            if not producto:
                logger.warning(f"Intento de actualizar producto inexistente: ID={producto_id}")
                raise ProductoNotFoundException(f"Producto con ID {producto_id} no encontrado")
            
            # Validaciones de negocio
            if producto_data.precio is not None and producto_data.precio <= 0:
                raise ProductoValidationException("El precio debe ser mayor a 0")
            
            if producto_data.stock is not None and producto_data.stock < 0:
                raise ProductoValidationException("El stock no puede ser negativo")
            
            # Validar código único si se intenta cambiar
            if producto_data.codigo and producto_data.codigo != producto.codigo:
                existe = await self.repository.existe_codigo(
                    producto_data.codigo,
                    excluir_id=producto_id
                )
                if existe:
                    logger.warning(
                        f"Intento de actualizar producto con código duplicado: {producto_data.codigo}"
                    )
                    raise ProductoDuplicateException(
                        f"El código '{producto_data.codigo}' ya existe en otro producto"
                    )
            
            # Actualizar el producto
            producto_actualizado = await self.repository.actualizar(
                producto_id, producto_data
            )
            await self.db.commit()
            
            logger.info(f"Producto actualizado: ID={producto_id}")
            return ProductoResponse.from_orm(producto_actualizado)
        
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Error de integridad al actualizar producto: {str(e)}")
            if "codigo" in str(e).lower() or "unique" in str(e).lower():
                raise ProductoDuplicateException("El código del producto ya existe")
            raise ProductoValidationException("Error en la validación de datos")
        
        except (ProductoNotFoundException, ProductoDuplicateException, ProductoValidationException):
            await self.db.rollback()
            raise
    
    async def eliminar_producto(self, producto_id: int) -> None:
        """
        Eliminar un producto.
        
        Args:
            producto_id: ID del producto a eliminar
            
        Raises:
            ProductoNotFoundException: Si no existe
        """
        try:
            # Verificar que existe
            producto = await self.repository.obtener_por_id(producto_id)
            if not producto:
                logger.warning(f"Intento de eliminar producto inexistente: ID={producto_id}")
                raise ProductoNotFoundException(f"Producto con ID {producto_id} no encontrado")
            
            # Eliminar
            await self.repository.eliminar(producto_id)
            await self.db.commit()
            
            logger.info(f"Producto eliminado: ID={producto_id}")
        
        except ProductoNotFoundException:
            await self.db.rollback()
            raise
    
    async def obtener_con_stock_bajo(
        self, limite_stock: int = 5, skip: int = 0, limit: int = 10
    ) -> ProductoListResponse:
        """
        Obtener productos con stock bajo.
        
        Args:
            limite_stock: Límite de stock considerado bajo
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Respuesta paginada con productos de stock bajo
        """
        if limite_stock < 0:
            raise ProductoValidationException("limite_stock no puede ser negativo")
        
        if skip < 0:
            raise ProductoValidationException("skip no puede ser negativo")
        
        if limit < 1 or limit > 100:
            raise ProductoValidationException("limit debe estar entre 1 y 100")
        
        productos, total = await self.repository.obtener_con_stock_bajo(
            limite_stock, skip, limit
        )
        
        items = [ProductoResponse.from_orm(p) for p in productos]
        
        return ProductoListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=items
        )
