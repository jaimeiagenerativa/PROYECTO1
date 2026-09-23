# ADR-0006: Observabilidad: logs, métricas y trazas desde el principio

- Estado: Aceptado
- Fecha: 2026-09-23

## Contexto

El sistema va a crecer en funcionalidad, usuarios y carga. Sin un nivel mínimo de observabilidad, resultará difícil diagnosticar errores de negocio, cuellos de botella o incidentes con integraciones externas.

## Decisión

Se instrumenta el sistema con logs estructurados, métricas básicas y trazas distribuidas (o al menos identificadores de correlación), con una infraestructura mínima de monitorización.

## Alternativas consideradas

### Observabilidad básica desde el inicio
Ventajas:
- más fácil diagnosticar errores
- mejor apoyo para el despliegue y la operación
- útil para el crecimiento posterior

Desventajas:
- requiere cierta disciplina en instrumentación
- se debe mantener la calidad de logs y trazas

### Observabilidad mínima o reactiva
Ventajas:
- menor esfuerzo inicial
- menos configuración

Desventajas:
- cuando aparecen fallos, cuesta diagnósticos rápidos
- suele aumentar el coste de incidentes

## Consecuencias

### Positivas
- mejora la capacidad de depuración
- permite detectar cuellos de botella antes
- facilita la detección de errores en integraciones
- ayuda a la operación del sistema y a la toma de decisiones técnica

### Negativas
- requiere almacenamiento y mantenimiento de métricas y trazas
- se debe definir una política clara de retención

## Justificación técnica

Para un sistema que crece y evoluciona, la observabilidad no es un lujo. Es una necesidad funcional de operación. Permite monitorizar disponibilidad, latencia, errores y flujo del negocio. La falta de observabilidad acaba costando más en incidentes que la inversión inicial.

## Riesgos y mitigaciones

- Riesgo: logs demasiado verbosos.
  Mitigación: definir niveles y filtros.
- Riesgo: trazas no correlacionadas.
  Mitigación: usar IDs de correlación por solicitud y evento.
- Riesgo: métricas poco útiles.
  Mitigación: definir SLIs clave del negocio y la plataforma.

## Seguimiento

Se revisará cuando:
- haya más de un servicio o más de un entorno operativo,
- se sumen más integraciones,
- el equipo necesite alertado más proactivo,
- se quieran dashboards de nivel de negocio.
