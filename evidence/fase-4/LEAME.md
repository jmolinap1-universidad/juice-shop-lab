# Evidencias de la Fase 4 — Ciberdefensa: pruebas de seguridad y superficie de ataque

Índice actualizado el 2026-11-25. **Tipo:** *C* = captura real; *S* = salida nativa o petición/respuesta registrada.
**Entorno:** *Local-V* = laboratorio vulnerable (127.0.0.1 / red Docker); *Local-P* = variante protegida en local;
*Render* = despliegue real autorizado (`juice-lab-masi-staging.onrender.com`, commit `768d1da`).

## Capturas de la línea base (laboratorio vulnerable, 2026-11-04)
Copiadas el 2026-11-25 desde `docs/evidencias-fase4-5/img/` (versionadas en el commit `29f262f`, «14 capturas reales»; la carpeta
del entregable se retiró del árbol vigente). Solo se copiaron las capturas reales de navegador; las imágenes que reproducían salidas
de terminal no se incluyen, porque las salidas originales ya están en esta carpeta como texto.

| Archivo | Qué muestra | Prueba |
|---|---|---|
| `capturas/01-app-homepage.jpg` | Tienda Juice Shop v20.3.0 en el laboratorio | Contexto |
| `capturas/02-sqli-union-users.jpg` | La búsqueda devuelve correos y hashes de `Users` (SQLi UNION) | A2 |
| `capturas/03-ftp-directory-listing.jpg` | Listado navegable de `/ftp` | A4/A5 |
| `capturas/04-encryptionkeys-listing.jpg` | Listado de `/encryptionkeys` | A4/A11 |
| `capturas/05-metrics-expuesto.jpg` | `/metrics` de Prometheus sin autenticación | A6 |
| `capturas/06-zap-reporte-resumen.jpg`, `07-zap-alertas.jpg` | Informe HTML de ZAP baseline (9 alertas) | DAST pasivo |

## Índice de evidencias
| Requisito | Evidencia (ruta) | Tipo | Fecha · entorno | Herramienta | Resultado e interpretación |
|---|---|---|---|---|---|
| Reconocimiento | `evidence/fase-4/nmap-127-3000.txt` | S | 2026-11-04 · Local-V | Nmap 7.98 | Un único servicio (3000/tcp); cabeceras con CORS `*` y sin CSP |
| DAST pasivo | `evidence/fase-4/zap/` (HTML, JSON, resumen); `evidence/cierre-tecnico-2026-11-23/12-caja-negra/` | S/C | 2026-11-04 Local-V · 2026-11-24 Local-P | ZAP 2.17.0 baseline | 9 alertas (2 Medium) en la línea base; 7 (0 High, 2 Medium de CSP) tras los controles. Pasivo: no prueba inyecciones |
| Prueba activa de caja negra | `evidence/fase-4/blackbox-2026-11-04/` | S | 2026-11-04 · Local-V | sqlmap 1.10.4 | SQLi *boolean* y *time-based blind* en `q`; SQLite; 169 peticiones, sin volcado masivo |
| Caja gris A1-A12 (antes) | `evidence/fase-4/antes/`, `run-20261107-074053/`, `inherente-2026-11-04/` | S | 2026-11-03/07 · Local-V | `security/attacks/run.sh` | 4 explotaciones (A1-A3, A7), 7 debilidades y BOLA (A12) |
| Caja gris A1-A12 (después) | `evidence/fase-4/despues/`; `evidence/cierre-brechas-2026-11-24/09-validacion-imagen-alpine-local/` (Local-P) y `10-validacion-render/` (Render) | S | 2026-11-24/25 | `run.sh`, `validar-cloud.sh` | 0 de 11 vulnerables y A12 protegido, en local y en Render |
| BOLA/IDOR | `evidence/fase-4/bola/` (Local-V); `10-validacion-render/baterias/bola-recursos.md` (Render) | S | 2026-11-04 · 2026-11-25 | dos cuentas sintéticas | Vulnerable (200 con la cesta ajena) → 0/10 accesos ajenos en 5 tipos de objeto, 7/7 operaciones del propietario |
| Casos complementarios T1-T10 | `10-validacion-render/baterias/pruebas/resultados.md` | S | 2026-11-25 · Render | `pruebas-cierre-tecnico.sh` | 0 vulnerables (T5 y T7 confirmados en el SIEM) |
| XSS en navegador | `evidence/cierre-brechas-2026-11-24/02-xss-navegador/` (capturas V1-V6 por objetivo) | C/S | 2026-11-25 · Local-V y Local-P | Chromium (Playwright 1.49.1) | Oficial sin modo seguro 5/6 ejecutados; corregida 0/6; imagen cloud 0/6 |
| 2FA (TOTP) | `evidence/cierre-brechas-2026-11-24/12-2fa/` (`local-imagen-cloud.md`, `render.md`) | S | 2026-11-25 · Local-P y Render | `security/ops/prueba-2fa.py`, pyotp 2.9.0 | 13 comprobaciones: 12 controles verificados y 1 **observación** (la 2FA se desactiva solo con la contraseña) |
| Superficie y perímetro | `docs/fase-4/fase4-pruebas-seguridad.md` §2; `10-validacion-render/tls.md`, `puerta-acceso.md` | S | 2026-11-04 · 2026-11-24 | grep sobre `server.ts`; OpenSSL; curl | 109 rutas literales, 14 modelos CRUD; en Render solo 443 (80 redirige), puerta 28/28 |

Burp Suite figuraba como complemento manual a cargo del equipo; no hay evidencia (`evidence/fase-4/burp/` no existe). Las pruebas
equivalentes de caja gris (curl dirigido, dos cuentas, Playwright) cubren los casos del alcance.
