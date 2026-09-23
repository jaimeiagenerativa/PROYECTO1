# ADR-0008: Evolución de la arquitectura: crecimiento gradual y extracción selectiva de servicios

- Estado: Aceptado
- Fecha: 2026-09-23

## Contexto

El sistema puede crecer en usuarios, carga y complejidad. Es razonable asumir que el monolito modular será suficiente en la fase inicial, pero no puede asumirse que será la solución definitiva con el tiempo. La arquitectura debe permitir crecer sin crisis ni reescrituras masivas.

## Decisión

Se adopta una estrategia de evolución gradual: mantener un monolito modular durante la fase inicial, incorporar workers para tareas asíncronas y extraer servicios específicos solo cuando exista una necesidad técnica clara y medible.

## Alternativas consideradas

### Evolución gradual desde monolito modular
Ventajas:
- reduce riesgos iniciales
- permite validar carga real antes de mover servicios
- menor costo y menor complejidad

Desventajas:
- si se retrasa demasiado, puede aparecer acoplamiento
- hace falta disciplina para saber cuándo extraer

### Microservicios desde el inicio
Ventajas:
- buena escalabilidad técnica
- mejor aislamiento para equipos grandes

Desventajas:
- gran complejidad operativa y de coordinación
- muy costoso para una fase inicial pequeña

## Consecuencias

### Positivas
- la arquitectura inicial es simple y rápida de mover
- el crecimiento se gestiona con evidencia
- la extracción de servicios se hace solo cuando es realmente necesaria
- se reducen costes de sobreingeniería

### Negativas
- requiere disciplina y medición constante
- puede haber momentos de transición si se extraen servicios
- es necesario definir correctamente qué módulos se convierten en servicios

## Justificación técnica

El crecimiento no debe decidirse a priori en abstracto. La decisión de extraer servicios debe basarse en señales objetivas: sobrecarga de base de datos, latencia, necesidad de escalar un módulo concreto, requerimientos de despliegue independiente o equipos especializados. Por ello, la arquitectura elegida favorece una evolución guiada por datos y evidencia.

## Riesgos y mitigaciones

- Riesgo: extracción prematura de servicios.
  Mitigación: esperar a que haya evidencia de carga o necesidad real.
- Riesgo: extraer servicios por motivos de organización sin técnica.
  Mitigación: evaluar límites de dominio y necesidad de aislamiento.
- Riesgo: migración compleja del monolito.
  Mitigación: usar eventos y adaptadores para desacoplar la evolución.

## Seguimiento

Se revisará esta decisión cuando:
- crezca el volumen de usuarios,
- aparezcan cuellos de botella modularizados,
- haya más de 8 desarrolladores,
- existan cargas muy diferentes entre funcionalidades,
- se necesite escalar un módulo de forma independiente.

Los primeros candidatos a extracción serán servicios como notificaciones, reportes, sincronización con calendarios o auditoría.
