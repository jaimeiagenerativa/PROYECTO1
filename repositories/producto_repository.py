"""
Repository Pattern para acceso a datos de Producto.
Contiene operaciones CRUD diretas con la base de datos.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from models.producto import Producto
from schemas.producto import ProductoCreate, ProductoUpdate
from typing import Optional, List, Tuple


class ProductoRepository:
    """Repository para operaciones de base de datos con Producto."""
    
    def __init__(self, db: AsyncSession):
        """
        Inicializar el repository con una sesión de BD.
        
        Args:
            db: Sesión AsyncSession de SQLAlchemy
        """
        self.db = db
    
    async def crear(self, producto_data: ProductoCreate) -> Producto:
        """
        Crear un nuevo producto en la base de datos.
        
        Args:
            producto_data: Datos del producto a crear
            
        Returns:
            Producto creado
            
        Raises:
            IntegrityError: Si el código ya existe
        """
        try:
            nuevo_producto = Producto(
                codigo=producto_data.codigo,
                nombre=producto_data.nombre,
                precio=producto_data.precio,
                stock=producto_data.stock,
                categoria=producto_data.categoria,
                proveedor=producto_data.proveedor,
                activo=producto_data.activo,
            )
            self.db.add(nuevo_producto)
            await self.db.flush()  # Genera el ID sin hacer commit
            return nuevo_producto
        except IntegrityError as e:
            await self.db.rollback()
            raise e
    
    async def obtener_por_id(self, producto_id: int) -> Optional[Producto]:
        """
        Obtener un producto por su ID.
        
        Args:
            producto_id: ID del producto
            
        Returns:
            Producto encontrado o None
        """
        stmt = select(Producto).where(Producto.id == producto_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def obtener_por_codigo(self, codigo: str) -> Optional[Producto]:
        """
        Obtener un producto por su código.
        
        Args:
            codigo: Código único del producto
            
        Returns:
            Producto encontrado o None
        """
        stmt = select(Producto).where(Producto.codigo == codigo.upper())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def obtener_todos(self, skip: int = 0, limit: int = 10) -> Tuple[List[Producto], int]:
        """
        Obtener todos los productos con paginación.
        
        Args:
            skip: Número de registros a saltar
            limit: Límite de registros a retornar
            
        Returns:
            Tupla con lista de productos y total de registros
        """
        # Obtener el total de registros
        count_stmt = select(func.count()).select_from(Producto)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # Obtener los registros con paginación
        stmt = select(Producto).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        productos = result.scalars().all()
        
        return productos, total
    
    async def obtener_por_categoria(
        self, categoria: str, skip: int = 0, limit: int = 10
    ) -> Tuple[List[Producto], int]:
        """
        Obtener productos por categoría.
        
        Args:
            categoria: Categoría del producto
            skip: Número de registros a saltar
            limit: Límite de registros a retornar
            
        Returns:
            Tupla con lista de productos y total de registros
        """
        count_stmt = select(func.count()).select_from(Producto).where(
            Producto.categoria == categoria
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        stmt = select(Producto).where(
            Producto.categoria == categoria
        ).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        productos = result.scalars().all()
        
        return productos, total
    
    async def obtener_activos(self, skip: int = 0, limit: int = 10) -> Tuple[List[Producto], int]:
        """
        Obtener solo productos activos.
        
        Args:
            skip: Número de registros a saltar
            limit: Límite de registros a retornar
            
        Returns:
            Tupla con lista de productos y total de registros
        """
        count_stmt = select(func.count()).select_from(Producto).where(
            Producto.activo == True
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        stmt = select(Producto).where(
            Producto.activo == True
        ).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        productos = result.scalars().all()
        
        return productos, total
    
    async def actualizar(
        self, producto_id: int, producto_data: ProductoUpdate
    ) -> Optional[Producto]:
        """
        Actualizar un producto existente.
        
        Args:
            producto_id: ID del producto a actualizar
            producto_data: Nuevos datos del producto
            
        Returns:
            Producto actualizado o None si no existe
            
        Raises:
            IntegrityError: Si hay violación de constraints
        """
        try:
            producto = await self.obtener_por_id(producto_id)
            if not producto:
                return None
            
            # Actualizar solo los campos que no son None
            update_data = producto_data.dict(exclude_unset=True)
            for campo, valor in update_data.items():
                if valor is not None:
                    setattr(producto, campo, valor)
            
            await self.db.flush()
            return producto
        except IntegrityError as e:
            await self.db.rollback()
            raise e
    
    async def eliminar(self, producto_id: int) -> bool:
        """
        Eliminar un producto por su ID.
        
        Args:
            producto_id: ID del producto a eliminar
            
        Returns:
            True si se eliminó, False si no existe
        """
        producto = await self.obtener_por_id(producto_id)
        if not producto:
            return False
        
        await self.db.delete(producto)
        await self.db.flush()
        return True
    
    async def existe_codigo(self, codigo: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verificar si un código ya existe en la BD.
        
        Args:
            codigo: Código a verificar
            excluir_id: ID a excluir de la búsqueda (para actualizaciones)
            
        Returns:
            True si existe, False si no
        """
        stmt = select(func.count()).select_from(Producto).where(
            Producto.codigo == codigo.upper()
        )
        
        if excluir_id is not None:
            stmt = stmt.where(Producto.id != excluir_id)
        
        result = await self.db.execute(stmt)
        return result.scalar() > 0
    
    async def obtener_con_stock_bajo(
        self, limite_stock: int = 5, skip: int = 0, limit: int = 10
    ) -> Tuple[List[Producto], int]:
        """
        Obtener productos con stock bajo.
        
        Args:
            limite_stock: Límite de stock considerado como bajo
            skip: Número de registros a saltar
            limit: Límite de registros a retornar
            
        Returns:
            Tupla con lista de productos y total de registros
        """
        count_stmt = select(func.count()).select_from(Producto).where(
            (Producto.stock <= limite_stock) & (Producto.activo == True)
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        stmt = select(Producto).where(
            (Producto.stock <= limite_stock) & (Producto.activo == True)
        ).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        productos = result.scalars().all()
        
        return productos, total
