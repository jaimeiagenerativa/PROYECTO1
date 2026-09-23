# ADR-0007: Integraciones externas: adaptadores y contratos explícitos

- Estado: Aceptado
- Fecha: 2026-09-23

## Contexto

El sistema necesita integrarse con un proveedor de identidad, un calendario externo, un servicio de correo y un sistema interno de RR. HH. Estas integraciones son esenciales para la operación del negocio, pero no forman parte del núcleo del dominio. Deben aislarse para mantener una arquitectura limpia y evitar acoplamientos directos con proveedores externos.

## Decisión

Se encapsulan las integraciones externas mediante adaptadores con contratos explícitos y se mantienen fuera del núcleo del dominio.

## Alternativas consideradas

### Adaptadores y puertos
Ventajas:
- facilita la sustitución de proveedores
- reduce acoplamiento con dependencias externas
- mejora pruebas y mantenimiento

Desventajas:
- requiere disciplina para definir puertos y contratos
- añade plantillas de código para cada integración

### Llamadas directas desde el dominio a los clientes externos
Ventajas:
- implementación rápida
- menos estructura inicial

Desventajas:
- acoplamiento fuerte
- peor testeabilidad
- mayor coste cuando el proveedor cambia o falla

## Consecuencias

### Positivas
- se protege el dominio de cambios externos
- se mejora la testabilidad y la mantenibilidad
- se facilitan cambios de proveedor sin reescrituras grandes

### Negativas
- requiere más diseño inicial
- el número de adaptadores puede crecer con el tiempo

## Justificación técnica

El dominio de reservas no debe depender de APIs concretas de terceros. La capa de integración debe desacoplar el negocio de proveedores externos, lo que reduce riesgos y mejora la capacidad de evolución. Esto es especialmente importante cuando se integran servicios de identidad, calendarios y notificaciones.

## Riesgos y mitigaciones

- Riesgo: cambios de esquema en proveedores externos.
  Mitigación: adaptadores y validación de contratos.
- Riesgo: tiempo de respuesta lento.
  Mitigación: uso de colas y adaptadores con timeouts.
- Riesgo: fallos de integración que afectan al negocio.
  Mitigación: reintentos y manejo de errores con circuit breakers.

## Seguimiento

Se revisará esta decisión cuando:
- aparezcan más adaptadores externos,
- se añadan proveedores con diferente naturaleza técnica,
- el sistema necesite más sincronizaciones asíncronas.
