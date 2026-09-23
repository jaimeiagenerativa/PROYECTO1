# Índice de ADRs

| ADR | Título | Estado | Fecha | Descripción breve |
|-----|--------|--------|-------|-------------------|
| ADR-0001 | Elección de arquitectura: monolito modular frente a microservicios | Aceptado | 2026-09-23 | Se decide mantener un monolito modular como base para la primera fase del proyecto, evitando sobre-complejidad operativa. |
| ADR-0002 | Base de datos relacional: PostgreSQL como sistema principal | Aceptado | 2026-09-23 | Se adopta PostgreSQL como base de datos transaccional principal y fundamento para el modelo de negocio. |
| ADR-0003 | Comunicación interna: REST síncrono y cola de mensajes para tareas asíncronas | Aceptado | 2026-09-23 | Se usa REST para operaciones transaccionales y broker de mensajes para tareas tolerantes a latencia y eventos. |
| ADR-0004 | Seguridad: SSO corporativo y control de acceso basado en roles | Aceptado | 2026-09-23 | Se utiliza OAuth2/OIDC con RBAC para autenticar empleados y proteger operaciones críticas y administrativas. |
| ADR-0005 | Despliegue: infraestructura cloud gestionada | Aceptado | 2026-09-23 | Se favorece la nube con servicios gestionados para reducir el esfuerzo operativo y acelerar la entrega inicial. |
| ADR-0006 | Observabilidad: logs, métricas y trazas | Aceptado | 2026-09-23 | Se exige observabilidad básica desde el principio para facilitar diagnóstico, alarmado y análisis de rendimiento. |
| ADR-0007 | Integraciones externas: adaptadores y contratos explícitos | Aceptado | 2026-09-23 | Se encapsulan integraciones con calendarios, correo y RR. HH. para aislar el dominio del negocio de terceros. |
| ADR-0008 | Evolución de la arquitectura: crecimiento gradual y extracción selectiva de servicios | Aceptado | 2026-09-23 | Se define una estrategia evolutiva para escalar sin reescrituras masivas: monolito + workers + extracción guiada. |

## ADRs por tema

### Arquitectura
- ADR-0001: `0001-architecture-monolith-vs-microservices.md`
- ADR-0008: `0008-scalability-evolution-strategy.md`

### Datos
- ADR-0002: `0002-database-postgresql.md`

### Comunicación
- ADR-0003: `0003-service-communication-rest-vs-mq.md`

### Seguridad
- ADR-0004: `0004-security-sso-and-rbac.md`

### Infraestructura
- ADR-0005: `0005-deployment-cloud-managed.md`

### Operación
- ADR-0006: `0006-observability-logs-metrics-traces.md`

### Integraciones
- ADR-0007: `0007-integrations-calendar-email-hr.md`

## Resumen del conjunto de ADRs

El conjunto de ADRs define una arquitectura orientada a la capacidad de entregar una primera versión funcional en un plazo realista, sin introducir complejidad innecesaria desde el principio. Las decisiones más relevantes para la arquitectura del proyecto son:

- mantener un monolito modular como base tecnológica inicial,
- usar PostgreSQL como sistema transaccional principal,
- desacoplar tareas asíncronas mediante una cola de mensajes,
- usar autenticación corporativa y control de acceso por roles,
- desplegar en infraestructura cloud gestionada,
- construir observabilidad desde el inicio,
- encapsular integraciones externas y preparar una evolución gradual.

Las decisiones que más afectan al crecimiento y mantenimiento del sistema son:

- la modularización del monolito,
- el modelo de datos y el uso de PostgreSQL,
- la estrategia de comunicación asíncrona,
- la separación de responsabilidades en módulos y adaptadores,
- la política de extracción de servicios cuando aumente la carga o la complejidad.

Las decisiones que requieren revisión periódica son:

- la estrategia de extracción de servicios,
- la capacidad de infraestructura y su escalado,
- la gestión de observabilidad,
- la política de seguridad y auditoría,
- los contratos de integración con terceros.

Los ADRs críticos para el equipo y para futuros cambios son:

- ADR-0001: porque define el enfoque arquitectónico principal.
- ADR-0003: porque afecta la forma de diseñar comunicación y desacoplamiento.
- ADR-0005: porque condiciona despliegue y operación.
- ADR-0008: porque marca la estrategia de evolución del sistema y evita reescrituras costosas.

## Nota

Estos ADRs representan una base realista para una arquitectura de tipo híbrida con monolito modular como primer eslabón y evolución progresiva hacia servicios específicos si el crecimiento y la complejidad lo justifican.
