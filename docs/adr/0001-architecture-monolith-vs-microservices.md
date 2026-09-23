# ADR-0001: Elección de arquitectura: monolito modular frente a microservicios

- Estado: Aceptado
- Fecha: 2026-09-23

## Contexto

El proyecto de reservas corporativas se plantea con un equipo pequeño y una primera versión con plazo de cuatro meses. El sistema necesita gestionar empleados, salas, recursos y reservas, con un crecimiento moderado a 2.000 usuarios. La importancia del tiempo de entrega y del coste inicial es clave. Además, el equipo tiene experiencia limitada en sistemas distribuidos y Kubernetes.

La decisión principal es si se construye una arquitectura:

- monolito modular, o
- microservicios desde el inicio.

## Decisión

Se adopta un monolito modular como arquitectura base para la fase inicial.

La aplicación se organiza por módulos funcionales: autenticación, usuarios, recursos, reservas, notificaciones, informes y auditoría. Se mantiene una base de datos relacional única y una estructura previa orientada a dominios y servicios de aplicación.

## Alternativas consideradas

### Monolito modular
Ventajas:
- entrega rápida
- bajo coste de infraestructura
- menos complejidad operativa
- más adecuado para un equipo pequeño

Desventajas:
- menos granularidad para escalar
- todos los módulos se despliegan juntos
- riesgo de acoplamiento si no se define bien la modularización

### Microservicios desde el inicio
Ventajas:
- mejor escalabilidad independiente
- mejor aislamiento de fallos
- aumento de autonomía de equipos

Desventajas:
- mayor coste inicial
- más complejidad de despliegue y operación
- mayor necesidad de observabilidad y coordinación
- difícil de sostener con equipo pequeño y poca experiencia operacional

## Consecuencias

### Positivas
- se obtiene una primera versión funcional antes
- se reduce la sobreinversión en infraestructura
- se facilita la coordinación técnica del equipo
- se permite crecer sin reescritura completa

### Negativas
- puede aparecer un cuello de botella en la base de datos
- el monolito necesita límites claros para mantenerse limpio
- la escalabilidad no será tan granular como en microservicios

## Justificación técnica

Para este proyecto, la complejidad de microservicios no está justificada en la primera fase. El objetivo es entregar valor rápido, controlar el coste y mantener una base sólida para crecimiento posterior. El monolito modular permite cumplir estos requisitos mientras deja una ruta de evolución clara.

## Riesgos y mitigaciones

- Riesgo: acoplamiento interno del monolito.
  Mitigación: definir módulos por dominio y evitar dependencias innecesarias.
- Riesgo: cuellos de botella en la base de datos.
  Mitigación: optimizar consultas, usar caché y extraer workers para procesos pesados.
- Riesgo: despliegues globales.
  Mitigación: despliegues progresivos y automatización con CI/CD.

## Seguimiento

Se revisará esta decisión si aparecen señales como:
- crecimiento por encima de 2.000 usuarios,
- escalar un módulo en particular de forma independiente,
- aumento del tiempo de despliegue,
- demasiada dependencia entre módulos.

Si se cumple alguna de estas condiciones, se evaluará una extracción gradual de servicios.
