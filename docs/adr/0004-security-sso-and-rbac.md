# ADR-0004: Seguridad: SSO corporativo y control de acceso basado en roles

- Estado: Aceptado
- Fecha: 2026-09-23

## Contexto

La plataforma gestionará empleados, reservas, salas y recursos corporativos. Por tanto, la autenticación y la autorización deben ser robustas y consistentes con el entorno empresarial. La solución debe integrarse con un proveedor corporativo de identidad y permitir una administración clara de permisos.

## Decisión

Se adopta autenticación mediante OAuth2/OIDC con un proveedor de identidad corporativo y control de acceso basado en roles (RBAC).

## Alternativas consideradas

### SSO corporativo + RBAC
Ventajas:
- seguridad centralizada
- facilita la gestión de usuarios y roles
- menor riesgo de errores en credenciales
- mejor integración con entorno empresarial

Desventajas:
- requiere integración con un proveedor externo
- se debe gestionar la expiración de tokens y renovación de sesión

### Autenticación propia con usuarios y roles locales
Ventajas:
- total control del flujo
- simple en sistemas muy pequeños

Desventajas:
- mayor complejidad operativa
- menos alineado con el entorno corporativo
- más esfuerzo de mantenimiento

## Consecuencias

### Positivas
- centraliza la identidad del empleado
- mejora la auditoría de acciones
- facilita permitir o denegar acceso por roles
- permite cumplimiento básico de políticas internas

### Negativas
- dependemos del proveedor de identidad para la autenticación
- el backend debe manejar correctamente tokens, expiración y revocación

## Justificación técnica

El ámbito del sistema es corporativo, por lo que SSO es la opción más racional. Un proveedor externo garantiza gestión centralizada, autenticación robusta y mejores políticas de seguridad. RBAC permite que permisos como "gestionar reservas", "administrar recursos" o "consultar informes" se apliquen con claridad.

## Riesgos y mitigaciones

- Riesgo: tokens caducados o mal validados.
  Mitigación: validación estricta del JWT y gestión de renovación.
- Riesgo: privilegios excesivos.
  Mitigación: política de permisos mínima y revisión por rol.
- Riesgo: dependencia de proveedor externo.
  Mitigación: configuración de fallback y análisis claro de respaldo.

## Seguimiento

Se revisará esta decisión si:
- se incorporan clientes externos,
- se introducen permisos más granulares por organización,
- se quiere una política de acceso basada en atributos (ABAC),
- se requiere multi-tenancy más fuerte.
