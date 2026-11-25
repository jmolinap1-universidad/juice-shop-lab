# Evidencia del cierre de brechas — 2026-11-24 / 25

Referencia: `main` desde `6f2fa61`. Despliegue vigente en Render: `768d1da` (imagen cloud Alpine, parches 01-14).
Todo lo atacado: instancias propias (local en 127.0.0.1 o redes Docker internas; en la nube solo el host autorizado por el
usuario, `juice-lab-masi-staging.onrender.com`). Sin credenciales en el repositorio; tokens y cookies nunca registrados.
Resumen y estado: `docs/cierre-tecnico/MATRIZ_CUMPLIMIENTO_SEIS_FASES.md`.

| Carpeta | Contenido | Resultado clave |
|---|---|---|
| `01-imagen-cloud/` | Construcciones de la imagen cloud (Debian reducida y Alpine) y su puerta | Debian reducida: HIGH 76→61, aún BLOQUEADA |
| `02-xss-navegador/` | XSS en Chromium (Playwright) contra 5 objetivos locales, 6 vectores | Oficial sin modo seguro 5/6; corregida (parche 14) 0/6 con y sin modo seguro; cloud 0/6 |
| `03-parche-14/` | Construcción verificada con el parche 14 | 22 archivos = `correcciones-cierre-brechas.patch` (fc3f765c…) |
| `04-validacion-local-imagen-final/` | Baterías sobre la imagen cloud Debian + parche 14 (local, 0,1 vCPU) | 27/27, 15/15, 35/35, 0 vulnerables |
| `05-iac-render/` | Esquema oficial de Render + política propia | 15/15; prueba negativa: 4 fallos detectados |
| `06-siem-render/` | Colector Render → Loki: simulador, clave de solo lectura, extremo a extremo | 48 s; 0 secretos en Loki; dos fallos del colector hallados y corregidos |
| `07-falso-positivo-socketio/` | Regla 920420 bloqueaba socket.io (POST text/plain) | EX-2 en REQUEST-900: 403 → 200; fuera de alcance sigue 403. `intento1-…`: la exclusión tras el CRS no funcionaba |
| `08-puerta-release-local/` | Puerta de release: app, cloud Debian, cloud Alpine | App APTA; Debian BLOQUEADA; **Alpine APTA (H0)** |
| `09-validacion-imagen-alpine-local/` | Imagen cloud final en local (0,1 vCPU, 512 MB, PostgreSQL 17) + XSS | 27/27, 15/15, 35/35, A1-A12 0/11, BOLA 0/10, T1-T10 0, XSS 0/6, 149 MiB |
| `10-validacion-render/` | **Despliegue real** `768d1da` | TLS 1.2/1.3; puerta 28/28 (incl. X-Forwarded-For); 15/15; 35/35; 0/11; BOLA 0/10; T1-T10 0; T5/T7 verificados desde el SIEM; socket.io 200 |
| `11-ci-release/` | `release.yml` en GitHub Actions | Run 45555578891: IaC, app y cloud en verde; run previo fallido documentado (Debian + defecto de Hadolint en CI) |
| `12-2fa/` | 2FA (TOTP) de Juice Shop: imagen cloud local y Render (`security/ops/prueba-2fa.py`, cuenta sintética) | 13/13 en ambos; observación: se desactiva con la contraseña sin segundo factor |
| `13-alertas-cloud/` | 6 reglas de alerta `entorno="cloud"` + reglas locales acotadas a `entorno="local"` | 4 alertas disparadas contra Render en ~1 min (SQLi, credenciales, límite, colector caído); 0 reglas locales disparadas |
| `14-threat-dragon/` | DFD en OWASP Threat Dragon (modelo generado desde los datos) | Esquema oficial 8/8; prueba negativa rechazada; Threat Dragon v2.6.2 real 7/7 (42 amenazas, 30/30 en el informe) |

Fallos propios hallados y corregidos en este ciclo (todos documentados en su carpeta): prueba de XSS que daba falsos
«no inyectado» (espera `networkidle`, banners que tapaban el producto, token antiguo en V6); colector con 429 y sin permiso
en su volumen; exclusión de fase 1 cargada tras el CRS; puerta de release que contaba como avisos los mensajes de descarga de
Docker en CI; reglas de alerta locales sin acotar por `entorno` (13); arnés de Threat Dragon que contaba la paleta de
figuras como elementos del diagrama (14). Ninguno se presentó como resultado válido.
