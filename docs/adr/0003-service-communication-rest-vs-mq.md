# ADR-0003: Comunicación interna: REST síncrono y cola de mensajes para tareas asíncronas

- Estado: Aceptado
- Fecha: 2026-09-23

## Contexto

El sistema necesita soportar operaciones transaccionales y síncronas, como la creación de una reserva, mientras que otras tareas no requieren una respuesta inmediata, como notificaciones, sincronización con calendarios o auditoría.

## Decisión

Se usa REST para la comunicación síncrona entre el frontend y el backend, y RabbitMQ (o un broker equivalente gestionado) para el intercambio de eventos y tareas asíncronas.

## Alternativas consideradas

### REST únicamente
Ventajas:
- sencilla de implementar
- muy adecuada para la capa web
- fácil de depurar

Desventajas:
- no es adecuado para tareas lentas o no críticas
- puede bloquear la petición principal si se usa para todo

### Microservicios con comunicación interna compleja desde el inicio
Ventajas:
- gran escalabilidad y desacoplamiento
- útil si los equipos crecen y se domina la infraestructura

Desventajas:
- demasiado compleja para el proyecto inicial
- más latencia y coordinación

### REST + broker de eventos
Ventajas:
- balance entre simplicidad y desacoplamiento
- mejora la tolerancia a fallos
- separa el flujo principal del procesamiento secundario

Desventajas:
- requiere manejar reintentos, idempotencia y trazabilidad
- aumenta la complejidad del diseño de eventos

## Consecuencias

### Positivas
- las operaciones críticas siguen siendo síncronas y transaccionales
- la aplicación no se bloquea con tareas pesadas
- se mejora la tolerancia a fallos
- se facilita el desacoplamiento funcional

### Negativas
- la consistencia final puede ser eventual
- se necesita gestionar eventos duplicados y reintentos
- es necesario diseñar consumidores idempotentes

## Justificación técnica

Para la operación principal, lo más seguro es mantener la consistencia y la latencia bajo control mediante llamadas síncronas. Para componentes como correo, auditoría o notificaciones, la naturaleza asíncrona y tolerante al retraso es más apropiada. La cola reduce la carga del flujo principal y mantiene un equilibrio entre robustez y simplicidad.

## Riesgos y mitigaciones

- Riesgo: eventos duplicados.
  Mitigación: idempotencia y almacenamiento de eventos procesados.
- Riesgo: mensajes perdidos.
  Mitigación: uso de broker duradero y patrón Outbox.
- Riesgo: fallos de integración externa.
  Mitigación: reintentos y cola de trabajos con backoff.

## Seguimiento

Si el sistema crece y aumentan las integraciones, se revisará:
- uso más intensivo de eventos,
- particionado o topic naming por dominio,
- necesidad de captura de eventos en streams,
- posible evolución a una arquitectura más distribuida.
