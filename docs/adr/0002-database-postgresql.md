# ADR-0002: Base de datos relacional: PostgreSQL como sistema principal

- Estado: Aceptado
- Fecha: 2026-09-23

## Contexto

El sistema requiere gestionar reservas, empleados, recursos y auditoría de acciones críticas. La integridad transaccional es importante y se necesitan consultas complejas por rol, organización, disponibilidad y fechas.

Dentro de la arquitectura seleccionada, se necesita decidir la tecnología principal de persistencia.

## Decisión

Se adopta PostgreSQL como base de datos relacional principal para la plataforma.

## Alternativas consideradas

### PostgreSQL
Ventajas:
- muy adecuado para transacciones y consistencia fuerte
- buena integración con FastAPI y SQLAlchemy
- madurez y ecosistema sólido
- soporte para JSON, índices complejos y extensiones

Desventajas:
- puede convertirse en cuello de botella si el volumen crece mucho
- requiere tuning y observabilidad en producción

### MongoDB
Ventajas:
- flexibilidad documental
- útil para datos semi-estructurados

Desventajas:
- menos apropiado para transacciones complejas de reservas
- menos natural para auditoría y reglas de negocio relacionales

### Bases de datos híbridas desde el inicio
Ventajas:
- potencialmente flexible
- útil para análisis avanzado

Desventajas:
- añade complejidad innecesaria al inicio
- requiere más operación y coordinación

## Consecuencias

### Positivas
- consistencia fuerte para reservas y disponibilidad
- modelado natural para relaciones
- buen soporte para auditoría y trazabilidad
- integración directa con el stack actual del equipo

### Negativas
- presión sobre la base de datos si el crecimiento es fuerte
- la optimización de consultas y el diseño de índices es crítico

## Justificación técnica

Las reservas y la validación de disponibilidad requieren transacciones y consistencia. PostgreSQL responde muy bien a ese tipo de requisitos y es una tecnología bien conocida por el equipo. Además, el sistema tendrá auditoría y control de datos sensibles, donde una base de datos relacional aporta claridad y fiabilidad.

## Riesgos y mitigaciones

- Riesgo: consultas lentas.
  Mitigación: índices, caché y consultas agregadas controladas.
- Riesgo: crecimiento de volumen histórico.
  Mitigación: particionado y políticas de retención de auditoría.
- Riesgo: bloqueo de la base de datos por consultas pesadas.
  Mitigación: separar reportes y cargas analíticas.

## Seguimiento

Si el volumen aumenta significativamente, se revisará:
- uso de replicas de lectura,
- particionamiento por fecha,
- extracción de reportes a almacenamiento analítico,
- separación del historial de eventos y auditoría.
