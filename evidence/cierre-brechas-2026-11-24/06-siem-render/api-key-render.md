# API key de Render para el colector del SIEM — 2026-11-24T23:06:21-06:00
Creada por el asistente con autorización expresa del usuario en el chat («hazlo tú para hacerlo posible funcionar»),
en la sesión de Render que el propio usuario inició. El valor NUNCA se mostró: se copió con el botón del panel y se guardó
directamente desde el portapapeles en `deploy/corregido/secrets/render_api_key` (ignorado por git; se vació el portapapeles).

| Propiedad | Valor |
|---|---|
| Nombre | siem-laboratorio |
| Workspace | My Workspace (único) |
| Permisos | **solo Monitoring → Read** («Read resource logs, metrics, events, and export settings»); el resto desactivado |
| Formato verificado | prefijo `rnd_`, 32 caracteres (sin registrar el valor) |
| Uso | `colector-render` (perfil nube), montada como secreto de Docker en /run/secrets/render_api_key |
| Revocación | Render → Account Settings → API Keys → siem-laboratorio → borrar (y vaciar el archivo local) |

Menor privilegio: con esta clave no se puede desplegar, cambiar variables ni leer secretos; solo leer logs y métricas.
