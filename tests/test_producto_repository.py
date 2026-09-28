import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import declarative_base

from models.producto import Base, Producto
from repositories.producto_repository import ProductoRepository


@pytest.fixture
def test_db() -> Session:
    """Crear una base de datos SQLite en memoria para cada test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def repository(test_db: Session) -> ProductoRepository:
    """Crear un repository con la DB de prueba."""
    return ProductoRepository(test_db)


class TestProductoRepositoryCreate:
    def test_crear_producto_exitosa(self, repository: ProductoRepository):
        producto = repository.crear(
            type("Payload", (), {
                "codigo": "P-001",
                "nombre": "Laptop",
                "precio": 1200.0,
                "stock": 10,
                "categoria": "ELECTRONICA",
                "proveedor": "Proveedor A",
                "activo": True,
            })()
        )

        assert producto is not None
        assert producto.id is not None
        assert producto.codigo == "P-001"
        assert producto.nombre == "Laptop"
        assert producto.precio == 1200.0
        assert producto.stock == 10
        assert producto.categoria.value == "ELECTRONICA"
        assert producto.activo is True

    def test_crear_producto_con_distintas_categorias(self, repository: ProductoRepository):
        categorias = ["ELECTRONICA", "ROPA", "ALIMENTOS", "LIBROS"]

        for categoria in categorias:
            producto = repository.crear(
                type("Payload", (), {
                    "codigo": f"P-{categoria[:2]}",
                    "nombre": f"Producto {categoria}",
                    "precio": 100.0,
                    "stock": 5,
                    "categoria": categoria,
                    "proveedor": "Proveedor X",
                    "activo": True,
                })()
            )
            assert producto.categoria.value == categoria

    def test_crear_producto_asigna_id_incrementado(self, repository: ProductoRepository):
        producto_1 = repository.crear(
            type("Payload", (), {
                "codigo": "P-001",
                "nombre": "Producto 1",
                "precio": 100.0,
                "stock": 5,
                "categoria": "ELECTRONICA",
                "proveedor": "Proveedor A",
                "activo": True,
            })()
        )
        producto_2 = repository.crear(
            type("Payload", (), {
                "codigo": "P-002",
                "nombre": "Producto 2",
                "precio": 200.0,
                "stock": 6,
                "categoria": "ROPA",
                "proveedor": "Proveedor B",
                "activo": True,
            })()
        )

        assert producto_1.id is not None
        assert producto_2.id is not None
        assert producto_2.id > producto_1.id


class TestProductoRepositoryRead:
    def test_obtener_por_id_existente(self, repository: ProductoRepository):
        producto_creado = repository.crear(
            type("Payload", (), {
                "codigo": "P-001",
                "nombre": "Laptop",
                "precio": 1200.0,
                "stock": 10,
                "categoria": "ELECTRONICA",
                "proveedor": "Proveedor A",
                "activo": True,
            })()
        )

        producto_obtenido = repository.obtener_por_id(producto_creado.id)

        assert producto_obtenido is not None
        assert producto_obtenido.id == producto_creado.id
        assert producto_obtenido.nombre == "Laptop"

    def test_obtener_por_id_inexistente(self, repository: ProductoRepository):
        assert repository.obtener_por_id(9999) is None

    def test_obtener_por_codigo_existente(self, repository: ProductoRepository):
        producto_creado = repository.crear(
            type("Payload", (), {
                "codigo": "P-001",
                "nombre": "Laptop",
                "precio": 1200.0,
                "stock": 10,
                "categoria": "ELECTRONICA",
                "proveedor": "Proveedor A",
                "activo": True,
            })()
        )

        producto_obtenido = repository.obtener_por_codigo("P-001")

        assert producto_obtenido is not None
        assert producto_obtenido.id == producto_creado.id

    def test_obtener_por_codigo_inexistente(self, repository: ProductoRepository):
        assert repository.obtener_por_codigo("NO-EXISTE") is None

    def test_obtener_todos_vacio(self, repository: ProductoRepository):
        productos, total = repository.obtener_todos()
        assert productos == []
        assert total == 0

    def test_obtener_todos_con_datos(self, repository: ProductoRepository):
        repository.crear(
            type("Payload", (), {
                "codigo": "P-001",
                "nombre": "Laptop",
                "precio": 1200.0,
                "stock": 10,
                "categoria": "ELECTRONICA",
                "proveedor": "Proveedor A",
                "activo": True,
            })()
        )
        repository.crear(
            type("Payload", (), {
                "codigo": "P-002",
                "nombre": "Camisa",
                "precio": 90.0,
                "stock": 15,
                "categoria": "ROPA",
                "proveedor": "Proveedor B",
                "activo": True,
            })()
        )

        productos, total = repository.obtener_todos()

        assert len(productos) == 2
        assert total == 2
        assert all(isinstance(p, Producto) for p in productos)

    def test_obtener_todos_con_paginacion(self, repository: ProductoRepository):
        for i in range(1, 6):
            repository.crear(
                type("Payload", (), {
                    "codigo": f"P-{i:03d}",
                    "nombre": f"Producto {i}",
                    "precio": 100.0 + i,
                    "stock": i,
                    "categoria": "ELECTRONICA",
                    "proveedor": "Proveedor A",
                    "activo": True,
                })()
            )

        productos, total = repository.obtener_todos(skip=2, limit=2)

        assert len(productos) == 2
        assert total == 5


class TestProductoRepositoryUpdate:
    def test_actualizar_producto_existente(self, repository: ProductoRepository):
        producto_original = repository.crear(
            type("Payload", (), {
                "codigo": "P-001",
                "nombre": "Laptop",
                "precio": 1200.0,
                "stock": 10,
                "categoria": "ELECTRONICA",
                "proveedor": "Proveedor A",
                "activo": True,
            })()
        )

        producto_actualizado = repository.actualizar(
            producto_original.id,
            type("Payload", (), {
                "codigo": "P-999",
                "nombre": "Laptop Pro",
                "precio": 1500.0,
                "stock": 12,
                "categoria": "ELECTRONICA",
                "proveedor": "Proveedor B",
                "activo": False,
            })()
        )

        assert producto_actualizado is not None
        assert producto_actualizado.id == producto_original.id
        assert producto_actualizado.nombre == "Laptop Pro"
        assert producto_actualizado.precio == 1500.0
        assert producto_actualizado.stock == 12
        assert producto_actualizado.activo is False

    def test_actualizar_producto_inexistente(self, repository: ProductoRepository):
        producto = repository.actualizar(
            9999,
            type("Payload", (), {
                "codigo": "P-999",
                "nombre": "No existe",
                "precio": 200.0,
                "stock": 2,
                "categoria": "ROPA",
                "proveedor": "Proveedor",
                "activo": True,
            })()
        )
        assert producto is None


class TestProductoRepositoryDelete:
    def test_eliminar_producto_existente(self, repository: ProductoRepository):
        producto = repository.crear(
            type("Payload", (), {
                "codigo": "P-001",
                "nombre": "Laptop",
                "precio": 1200.0,
                "stock": 10,
                "categoria": "ELECTRONICA",
                "proveedor": "Proveedor A",
                "activo": True,
            })()
        )

        resultado = repository.eliminar(producto.id)

        assert resultado is True
        assert repository.obtener_por_id(producto.id) is None

    def test_eliminar_producto_inexistente(self, repository: ProductoRepository):
        assert repository.eliminar(9999) is False


class TestProductoRepositoryFilters:
    def test_obtener_por_categoria(self, repository: ProductoRepository):
        repository.crear(
            type("Payload", (), {
                "codigo": "P-001",
                "nombre": "Laptop",
                "precio": 1200.0,
                "stock": 10,
                "categoria": "ELECTRONICA",
                "proveedor": "Proveedor A",
                "activo": True,
            })()
        )
        repository.crear(
            type("Payload", (), {
                "codigo": "P-002",
                "nombre": "Camisa",
                "precio": 90.0,
                "stock": 15,
                "categoria": "ROPA",
                "proveedor": "Proveedor B",
                "activo": True,
            })()
        )

        productos, total = repository.obtener_por_categoria("ELECTRONICA")

        assert len(productos) == 1
        assert total == 1
        assert productos[0].categoria.value == "ELECTRONICA"

    def test_obtener_activos(self, repository: ProductoRepository):
        repository.crear(
            type("Payload", (), {
                "codigo": "P-001",
                "nombre": "Laptop",
                "precio": 1200.0,
                "stock": 10,
                "categoria": "ELECTRONICA",
                "proveedor": "Proveedor A",
                "activo": True,
            })()
        )
        repository.crear(
            type("Payload", (), {
                "codigo": "P-002",
                "nombre": "Laptop 2",
                "precio": 1500.0,
                "stock": 5,
                "categoria": "ELECTRONICA",
                "proveedor": "Proveedor B",
                "activo": False,
            })()
        )

        productos, total = repository.obtener_activos()

        assert len(productos) == 1
        assert total == 1
        assert productos[0].activo is True

    def test_obtener_con_stock_bajo(self, repository: ProductoRepository):
        repository.crear(
            type("Payload", (), {
                "codigo": "P-001",
                "nombre": "Laptop",
                "precio": 1200.0,
                "stock": 2,
                "categoria": "ELECTRONICA",
                "proveedor": "Proveedor A",
                "activo": True,
            })()
        )
        repository.crear(
            type("Payload", (), {
                "codigo": "P-002",
                "nombre": "Camisa",
                "precio": 80.0,
                "stock": 20,
                "categoria": "ROPA",
                "proveedor": "Proveedor B",
                "activo": True,
            })()
        )

        productos, total = repository.obtener_con_stock_bajo(limite_stock=5)

        assert len(productos) == 1
        assert total == 1
        assert productos[0].stock == 2
