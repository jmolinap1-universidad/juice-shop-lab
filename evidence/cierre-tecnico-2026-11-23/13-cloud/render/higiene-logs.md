# Higiene de los logs en Render — 2026-11-24T00:57:20-06:00
Búsquedas en el panel de logs del servicio juice-lab-masi-staging (navegador; los valores nunca se copiaron):

| Búsqueda | Ventana (UTC) | Resultado |
|---|---|---|
| `eyJ` (JWT) | 2026-11-24 05:00–07:10 | No matching logs |
| `lab_acceso=` (cookie de acceso) | 2026-11-24 05:00–07:10 (incluye los despliegues con el fallo del 401) | No matching logs |
| `Authorization` | 2026-11-24 06:30–07:05 (validación) | No matching logs |

Motivo: en la nube no hay Alloy que redacte; el audit log de ModSecurity del contenedor cloud usa solo las partes A, F, H y Z
(sin cabeceras ni cuerpos de la petición) y el log de acceso de nginx no incluye cabeceras.
Diagnóstico de arranque (solo metadatos): `clave JWT: generada en el arranque (efímera, RSA 2048, 1704 bytes, tipo PEM: PRIVATE KEY)`,
`acceso: 1 usuario(s) autorizado(s): verificador` (12:31:57 a. m. CST).
