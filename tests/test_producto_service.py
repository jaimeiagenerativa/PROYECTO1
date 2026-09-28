import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models.producto import Base
from services.producto_service import (
    ProductoService,
    ProductoDuplicateException,
    ProductoNotFoundException,
    ProductoValidationException,
)
from repositories.producto_repository import ProductoRepository
from schemas.producto import ProductoCreate, ProductoUpdate


@pytest.fixture
def test_db() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def service(test_db: Session) -> ProductoService:
    repository = ProductoRepository(test_db)
    return ProductoService(test_db)


class TestProductoServiceValidation:
    def test_validar_precio_valido(self, service: ProductoService):
        service.creation_service.validation_service.validar_precio(100.0)

    def test_validar_precio_invalido(self, service: ProductoService):
        with pytest.raises(ProductoValidationException):
            service.creation_service.validation_service.validar_precio(0)

    def test_validar_stock_valido(self, service: ProductoService):
        service.creation_service.validation_service.validar_stock(5)

    def test_validar_stock_invalido(self, service: ProductoService):
        with pytest.raises(ProductoValidationException):
            service.creation_service.validation_service.validar_stock(-1)

    def test_validar_paginacion_valida(self, service: ProductoService):
        service.creation_service.validation_service.validar_paginacion(0, 10)

    def test_validar_paginacion_invalida(self, service: ProductoService):
        with pytest.raises(ProductoValidationException):
            service.creation_service.validation_service.validar_paginacion(-1, 10)


class TestProductoServiceCreate:
    @pytest.mark.asyncio
    async def test_crear_producto_valido(self, service: ProductoService):
        data = ProductoCreate(
            codigo="P-001",
            nombre="Laptop",
            precio=1200.0,
            stock=10,
            categoria="ELECTRONICA",
            proveedor="Proveedor A",
            activo=True,
        )

        producto = await service.crear_producto(data)

        assert producto.id is not None
        assert producto.codigo == "P-001"
        assert producto.nombre == "Laptop"

    @pytest.mark.asyncio
    async def test_crear_producto_codigo_duplicado(self, service: ProductoService):
        data_1 = ProductoCreate(
            codigo="P-001",
            nombre="Laptop",
            precio=1200.0,
            stock=10,
            categoria="ELECTRONICA",
            proveedor="Proveedor A",
            activo=True,
        )
        await service.crear_producto(data_1)

        data_2 = ProductoCreate(
            codigo="P-001",
            nombre="Laptop 2",
            precio=900.0,
            stock=4,
            categoria="ROPA",
            proveedor="Proveedor B",
            activo=True,
        )

        with pytest.raises(ProductoDuplicateException):
            await service.crear_producto(data_2)

    @pytest.mark.asyncio
    async def test_crear_producto_precio_invalido(self, service: ProductoService):
        data = ProductoCreate(
            codigo="P-002",
            nombre="Producto",
            precio=0,
            stock=10,
            categoria="ELECTRONICA",
            proveedor="Proveedor A",
            activo=True,
        )

        with pytest.raises(ProductoValidationException):
            await service.crear_producto(data)


class TestProductoServiceRead:
    @pytest.mark.asyncio
    async def test_obtener_producto_existente(self, service: ProductoService):
        data = ProductoCreate(
            codigo="P-001",
            nombre="Laptop",
            precio=1200.0,
            stock=10,
            categoria="ELECTRONICA",
            proveedor="Proveedor A",
            activo=True,
        )
        producto_creado = await service.crear_producto(data)

        producto = await service.obtener_producto(producto_creado.id)

        assert producto.id == producto_creado.id
        assert producto.nombre == "Laptop"

    @pytest.mark.asyncio
    async def test_obtener_producto_inexistente(self, service: ProductoService):
        with pytest.raises(ProductoNotFoundException):
            await service.obtener_producto(9999)

    @pytest.mark.asyncio
    async def test_obtener_todos_productos(self, service: ProductoService):
        for i in range(1, 4):
            await service.crear_producto(
                ProductoCreate(
                    codigo=f"P-{i:03d}",
                    nombre=f"Producto {i}",
                    precio=100.0 + i,
                    stock=i,
                    categoria="ELECTRONICA",
                    proveedor="Proveedor A",
                    activo=True,
                )
            )

        resultado = await service.obtener_todos_productos(skip=0, limit=10)

        assert resultado.total == 3
        assert len(resultado.items) == 3


class TestProductoServiceUpdate:
    @pytest.mark.asyncio
    async def test_actualizar_producto_valido(self, service: ProductoService):
        creado = await service.crear_producto(
            ProductoCreate(
                codigo="P-001",
                nombre="Laptop",
                precio=1200.0,
                stock=10,
                categoria="ELECTRONICA",
                proveedor="Proveedor A",
                activo=True,
            )
        )

        actualizado = await service.actualizar_producto(
            creado.id,
            ProductoUpdate(
                nombre="Laptop Pro",
                precio=1500.0,
                stock=20,
                categoria="ELECTRONICA",
                proveedor="Proveedor B",
                activo=False,
            ),
        )

        assert actualizado.nombre == "Laptop Pro"
        assert actualizado.precio == 1500.0
        assert actualizado.stock == 20
        assert actualizado.activo is False

    @pytest.mark.asyncio
    async def test_actualizar_producto_inexistente(self, service: ProductoService):
        with pytest.raises(ProductoNotFoundException):
            await service.actualizar_producto(
                9999,
                ProductoUpdate(nombre="No existe"),
            )


class TestProductoServiceDelete:
    @pytest.mark.asyncio
    async def test_eliminar_producto_existente(self, service: ProductoService):
        creado = await service.crear_producto(
            ProductoCreate(
                codigo="P-001",
                nombre="Laptop",
                precio=1200.0,
                stock=10,
                categoria="ELECTRONICA",
                proveedor="Proveedor A",
                activo=True,
            )
        )

        await service.eliminar_producto(creado.id)

        with pytest.raises(ProductoNotFoundException):
            await service.obtener_producto(creado.id)

    @pytest.mark.asyncio
    async def test_eliminar_producto_inexistente(self, service: ProductoService):
        with pytest.raises(ProductoNotFoundException):
            await service.eliminar_producto(9999)
