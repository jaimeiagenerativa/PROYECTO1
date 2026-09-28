"""
Service Layer para Producto.
Contiene lógica de negocio, validaciones y orquestación.
Aplicando SRP (Single Responsibility Principle) con métodos pequeños y específicos.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from repositories.producto_repository import ProductoRepository
from schemas.producto import ProductoCreate, ProductoUpdate, ProductoResponse, ProductoListResponse
from models.producto import Producto
from typing import Optional
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


class ProductoValidationService:
    """Servicio especializado en validaciones de Producto."""
    
    @staticmethod
    def validar_precio(precio: float) -> None:
        """
        Validar que el precio sea válido.
        
        Args:
            precio: Precio del producto
            
        Raises:
            ProductoValidationException: Si el precio es inválido
        """
        if precio is None:
            return  # Opcional en actualización
        
        if precio <= 0:
            raise ProductoValidationException("El precio debe ser mayor a 0")
    
    @staticmethod
    def validar_stock(stock: int) -> None:
        """
        Validar que el stock sea válido.
        
        Args:
            stock: Stock del producto
            
        Raises:
            ProductoValidationException: Si el stock es inválido
        """
        if stock is None:
            return  # Opcional en actualización
        
        if stock < 0:
            raise ProductoValidationException("El stock no puede ser negativo")
    
    @staticmethod
    def validar_paginacion(skip: int, limit: int) -> None:
        """
        Validar parámetros de paginación.
        
        Args:
            skip: Registros a saltar
            limit: Límite de registros
            
        Raises:
            ProductoValidationException: Si los parámetros son inválidos
        """
        if skip < 0:
            raise ProductoValidationException("skip no puede ser negativo")
        
        if limit < 1 or limit > 100:
            raise ProductoValidationException("limit debe estar entre 1 y 100")
    
    @staticmethod
    def validar_limite_stock(limite_stock: int) -> None:
        """
        Validar que el límite de stock sea válido.
        
        Args:
            limite_stock: Límite de stock
            
        Raises:
            ProductoValidationException: Si el límite es inválido
        """
        if limite_stock < 0:
            raise ProductoValidationException("limite_stock no puede ser negativo")


class ProductoExistenceService:
    """Servicio especializado en verificaciones de existencia."""
    
    def __init__(self, repository: ProductoRepository):
        """Inicializar con el repository."""
        self.repository = repository
    
    async def verificar_producto_existe(self, producto_id: int) -> Producto:
        """
        Verificar que un producto existe por ID.
        
        Args:
            producto_id: ID del producto
            
        Returns:
            Producto si existe
            
        Raises:
            ProductoNotFoundException: Si no existe
        """
        producto = await self.repository.obtener_por_id(producto_id)
        
        if not producto:
            logger.warning(f"Producto no encontrado: ID={producto_id}")
            raise ProductoNotFoundException(
                f"Producto con ID {producto_id} no encontrado"
            )
        
        return producto
    
    async def verificar_codigo_unico(
        self, codigo: str, excluir_id: Optional[int] = None
    ) -> None:
        """
        Verificar que el código sea único.
        
        Args:
            codigo: Código a verificar
            excluir_id: ID a excluir de la búsqueda (para actualizaciones)
            
        Raises:
            ProductoDuplicateException: Si el código ya existe
        """
        existe = await self.repository.existe_codigo(codigo, excluir_id)
        
        if existe:
            logger.warning(
                f"Intento de usar código duplicado: {codigo} (excluir_id={excluir_id})"
            )
            raise ProductoDuplicateException(
                f"El código '{codigo}' ya existe en el sistema"
            )


class ProductoCreationService:
    """Servicio especializado en creación de productos."""
    
    def __init__(self, repository: ProductoRepository, db: AsyncSession):
        """Inicializar servicios."""
        self.repository = repository
        self.db = db
        self.validation_service = ProductoValidationService()
        self.existence_service = ProductoExistenceService(repository)
    
    async def crear_producto(self, producto_data: ProductoCreate) -> ProductoResponse:
        """
        Crear un nuevo producto con validaciones completas.
        
        Args:
            producto_data: Datos del producto a crear
            
        Returns:
            Producto creado como ProductoResponse
            
        Raises:
            ProductoDuplicateException: Si el código ya existe
            ProductoValidationException: Si hay validaciones fallidas
        """
        try:
            # Validar campos individuales
            await self._validar_datos_creacion(producto_data)
            
            # Verificar código único
            await self.existence_service.verificar_codigo_unico(producto_data.codigo)
            
            # Crear producto
            producto = await self._insertar_producto(producto_data)
            
            logger.info(f"Producto creado: ID={producto.id}, Código={producto.codigo}")
            return ProductoResponse.from_orm(producto)
        
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Error de integridad al crear producto: {str(e)}")
            raise ProductoDuplicateException("El código del producto ya existe")
        
        except (ProductoDuplicateException, ProductoValidationException):
            await self.db.rollback()
            raise
    
    async def _validar_datos_creacion(self, producto_data: ProductoCreate) -> None:
        """
        Validar todos los campos al crear.
        
        Args:
            producto_data: Datos a validar
            
        Raises:
            ProductoValidationException: Si hay validaciones fallidas
        """
        self.validation_service.validar_precio(producto_data.precio)
        self.validation_service.validar_stock(producto_data.stock)
    
    async def _insertar_producto(self, producto_data: ProductoCreate) -> Producto:
        """
        Insertar el producto en la base de datos.
        
        Args:
            producto_data: Datos del producto
            
        Returns:
            Producto insertado
        """
        producto = await self.repository.crear(producto_data)
        await self.db.flush()
        return producto


class ProductoRetrievalService:
    """Servicio especializado en obtención de productos."""
    
    def __init__(self, repository: ProductoRepository):
        """Inicializar con el repository."""
        self.repository = repository
        self.validation_service = ProductoValidationService()
        self.existence_service = ProductoExistenceService(repository)
    
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
        producto = await self.existence_service.verificar_producto_existe(producto_id)
        return ProductoResponse.from_orm(producto)
    
    async def obtener_todos_productos(
        self, skip: int = 0, limit: int = 10
    ) -> ProductoListResponse:
        """
        Obtener todos los productos con paginación.
        
        Args:
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Respuesta paginada con productos
        """
        self.validation_service.validar_paginacion(skip, limit)
        
        productos, total = await self.repository.obtener_todos(skip, limit)
        
        return self._construir_respuesta_listado(
            productos=productos, total=total, skip=skip, limit=limit
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
        self.validation_service.validar_paginacion(skip, limit)
        
        productos, total = await self.repository.obtener_por_categoria(
            categoria, skip, limit
        )
        
        return self._construir_respuesta_listado(
            productos=productos, total=total, skip=skip, limit=limit
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
        self.validation_service.validar_paginacion(skip, limit)
        
        productos, total = await self.repository.obtener_activos(skip, limit)
        
        return self._construir_respuesta_listado(
            productos=productos, total=total, skip=skip, limit=limit
        )
    
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
        self.validation_service.validar_limite_stock(limite_stock)
        self.validation_service.validar_paginacion(skip, limit)
        
        productos, total = await self.repository.obtener_con_stock_bajo(
            limite_stock, skip, limit
        )
        
        return self._construir_respuesta_listado(
            productos=productos, total=total, skip=skip, limit=limit
        )
    
    @staticmethod
    def _construir_respuesta_listado(
        productos: list, total: int, skip: int, limit: int
    ) -> ProductoListResponse:
        """
        Construir respuesta de listado.
        
        Args:
            productos: Lista de productos
            total: Total de registros
            skip: Registros saltados
            limit: Límite de registros
            
        Returns:
            Respuesta formateada
        """
        items = [ProductoResponse.from_orm(p) for p in productos]
        
        return ProductoListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=items
        )


class ProductoUpdateService:
    """Servicio especializado en actualización de productos."""
    
    def __init__(self, repository: ProductoRepository, db: AsyncSession):
        """Inicializar servicios."""
        self.repository = repository
        self.db = db
        self.validation_service = ProductoValidationService()
        self.existence_service = ProductoExistenceService(repository)
    
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
            ProductoDuplicateException: Si el código ya existe
            ProductoValidationException: Si hay validaciones fallidas
        """
        try:
            # Verificar que el producto existe
            await self.existence_service.verificar_producto_existe(producto_id)
            
            # Validar datos
            await self._validar_datos_actualizacion(producto_id, producto_data)
            
            # Actualizar
            producto_actualizado = await self._actualizar_en_bd(
                producto_id, producto_data
            )
            
            logger.info(f"Producto actualizado: ID={producto_id}")
            return ProductoResponse.from_orm(producto_actualizado)
        
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Error de integridad al actualizar: {str(e)}")
            raise ProductoDuplicateException("El código del producto ya existe")
        
        except (ProductoNotFoundException, ProductoDuplicateException, ProductoValidationException):
            await self.db.rollback()
            raise
    
    async def _validar_datos_actualizacion(
        self, producto_id: int, producto_data: ProductoUpdate
    ) -> None:
        """
        Validar datos antes de actualizar.
        
        Args:
            producto_id: ID del producto
            producto_data: Datos a validar
            
        Raises:
            ProductoValidationException o ProductoDuplicateException
        """
        # Validar campos individuales
        self.validation_service.validar_precio(producto_data.precio)
        self.validation_service.validar_stock(producto_data.stock)
        
        # Validar código único si se intenta cambiar
        if producto_data.codigo:
            producto_actual = await self.repository.obtener_por_id(producto_id)
            if producto_data.codigo != producto_actual.codigo:
                await self.existence_service.verificar_codigo_unico(
                    producto_data.codigo,
                    excluir_id=producto_id
                )
    
    async def _actualizar_en_bd(
        self, producto_id: int, producto_data: ProductoUpdate
    ) -> Producto:
        """
        Realizar la actualización en la base de datos.
        
        Args:
            producto_id: ID del producto
            producto_data: Datos a actualizar
            
        Returns:
            Producto actualizado
        """
        producto_actualizado = await self.repository.actualizar(
            producto_id, producto_data
        )
        await self.db.flush()
        return producto_actualizado


class ProductoDeletionService:
    """Servicio especializado en eliminación de productos."""
    
    def __init__(self, repository: ProductoRepository, db: AsyncSession):
        """Inicializar servicios."""
        self.repository = repository
        self.db = db
        self.existence_service = ProductoExistenceService(repository)
    
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
            await self.existence_service.verificar_producto_existe(producto_id)
            
            # Eliminar
            await self._eliminar_de_bd(producto_id)
            
            logger.info(f"Producto eliminado: ID={producto_id}")
        
        except ProductoNotFoundException:
            await self.db.rollback()
            raise
    
    async def _eliminar_de_bd(self, producto_id: int) -> None:
        """
        Realizar la eliminación en la base de datos.
        
        Args:
            producto_id: ID del producto a eliminar
        """
        await self.repository.eliminar(producto_id)
        await self.db.flush()


class ProductoService:
    """
    Servicio principal que orquesta todos los servicios especializados.
    Implementa el patrón Facade para simplificar el acceso.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Inicializar el servicio principal.
        
        Args:
            db: Sesión AsyncSession de SQLAlchemy
        """
        self.repository = ProductoRepository(db)
        self.db = db
        
        # Inicializar servicios especializados
        self.creation_service = ProductoCreationService(self.repository, db)
        self.retrieval_service = ProductoRetrievalService(self.repository)
        self.update_service = ProductoUpdateService(self.repository, db)
        self.deletion_service = ProductoDeletionService(self.repository, db)
    
    # Delegación de métodos al servicio de creación
    async def crear_producto(self, producto_data: ProductoCreate) -> ProductoResponse:
        """Crear nuevo producto."""
        return await self.creation_service.crear_producto(producto_data)
    
    # Delegación de métodos al servicio de obtención
    async def obtener_producto(self, producto_id: int) -> ProductoResponse:
        """Obtener producto por ID."""
        return await self.retrieval_service.obtener_producto(producto_id)
    
    async def obtener_todos_productos(
        self, skip: int = 0, limit: int = 10
    ) -> ProductoListResponse:
        """Obtener todos los productos con paginación."""
        return await self.retrieval_service.obtener_todos_productos(skip, limit)
    
    async def obtener_por_categoria(
        self, categoria: str, skip: int = 0, limit: int = 10
    ) -> ProductoListResponse:
        """Obtener productos por categoría."""
        return await self.retrieval_service.obtener_por_categoria(
            categoria, skip, limit
        )
    
    async def obtener_activos(
        self, skip: int = 0, limit: int = 10
    ) -> ProductoListResponse:
        """Obtener productos activos."""
        return await self.retrieval_service.obtener_activos(skip, limit)
    
    async def obtener_con_stock_bajo(
        self, limite_stock: int = 5, skip: int = 0, limit: int = 10
    ) -> ProductoListResponse:
        """Obtener productos con stock bajo."""
        return await self.retrieval_service.obtener_con_stock_bajo(
            limite_stock, skip, limit
        )
    
    # Delegación de métodos al servicio de actualización
    async def actualizar_producto(
        self, producto_id: int, producto_data: ProductoUpdate
    ) -> ProductoResponse:
        """Actualizar producto."""
        return await self.update_service.actualizar_producto(producto_id, producto_data)
    
    # Delegación de métodos al servicio de eliminación
    async def eliminar_producto(self, producto_id: int) -> None:
        """Eliminar producto."""
        return await self.deletion_service.eliminar_producto(producto_id)
