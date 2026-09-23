# ADR-0005: Despliegue: infraestructura cloud gestionada

- Estado: Aceptado
- Fecha: 2026-09-23

## Contexto

El equipo no cuenta con una base operativa grande ni con un equipo de plataforma dedicado. Se necesita desplegar la solución en un plazo corto y mantener bajos los costes operativos. La infraestructura basada en cloud ofrece rapidez, servicios de base de datos, balanceadores y servicios gestionados.

## Decisión

Se despliega en una infraestructura cloud con servicios gestionados, priorizando simplicidad, velocidad y reducción del esfuerzo operativo.

## Alternativas consideradas

### Cloud con servicios gestionados
Ventajas:
- se reduce la complejidad de operación
- más rapidez de entrega
- menor necesidad de administrar servidores
- mejor integración con observabilidad y CI/CD

Desventajas:
- dependencia del proveedor cloud
- costes variables según tráfico y uso

### Infraestructura propia o semi-gestionada
Ventajas:
- mayor control
- útil cuando hay requisitos estrictos de infraestructura

Desventajas:
- más operación manual
- más complejidad inicial
- más tiempo para desplegar y mantener

## Consecuencias

### Positivas
- despliegues más rápidos
- menos tareas de administración de infraestructura
- el equipo puede centrarse en producto y negocio
- mayor capacidad de escalar horizontalmente con pocos cambios

### Negativas
- más dependencia del proveedor
- costes a largo plazo pueden crecer
- requiere disciplina en configuración y seguridad

## Justificación técnica

El proyecto necesita un despliegue sencillo y un equipo pequeño. Por ello, desplegar en cloud con servicios gestionados de PostgreSQL, Redis, cola de mensajes y observabilidad es la solución más razonable. Además, la fase inicial no requiere un entorno on-premise ni una infraestructura de bajo nivel.

## Riesgos y mitigaciones

- Riesgo: aumento del coste por uso.
  Mitigación: dimensionamiento adecuado y monitorización.
- Riesgo: dependencia del proveedor cloud.
  Mitigación: definición de contratos claros y posibilidad de migración futura
- Riesgo: configuración insegura.
  Mitigación: políticas de seguridad, secret management y entorno por perfil.

## Seguimiento

Se revisará esta decisión cuando:
- el número de usuarios crezca significativamente,
- el equipo disponga de más madurez en DevOps,
- se requieran despliegues en varias regiones,
- o aparezcan requisitos complejos de aislamiento de infraestructura.
