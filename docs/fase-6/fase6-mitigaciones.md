# Fase 6 – Mitigaciones, WAF, monitoreo y tratamiento del riesgo

**Estado:** Implementado y verificado. El entorno endurecido (`deploy/hardened/docker-compose.yml`) se levantó en
local; los mismos ataques de la Fase 4 se reejecutaron contra él. La matriz inherente vs. residual está en
`docs/fase-6/matriz-riesgo.md`.

> Etiquetas: **[V]** verificado · **[S]** simulado · **[P]** propuesto.

## 1. Arquitectura del entorno endurecido
```
Cliente → (127.0.0.1:8080) → WAF Nginx + ModSecurity + OWASP CRS 4.25.2 → red interna → Juice Shop (solo expuesto al WAF)
```
- La aplicación **no publica puertos**; solo es alcanzable por el WAF dentro de la red Docker `interna`.
- La app corre con el hardening de la Fase 5 (FS de solo lectura, `cap_drop ALL`, `no-new-privileges`, límites,
  usuario 65532, `NODE_ENV=production`).
- Único punto de entrada: el WAF en `127.0.0.1:8080` (regla de aislamiento).

## 2. Controles aplicados y verificados
| Control | Implementación | Evidencia |
|---|---|---|
| WAF contra inyección (SQLi, etc.) | ModSecurity 3.0.17 + OWASP CRS 4.25.2, paranoia 1, modo bloqueo | Regla CRS 942100 (libinjection) y 949110 en `evidence/fase-6/waf-logs/` |
| Bloqueo de rutas sensibles | nginx `deny` para `/ftp`, `/encryptionkeys`, `/support/logs`, `/.well-known/csaf`, `/metrics` | HTTP 403 (A4, A5, A6, A11) |
| Cabeceras de seguridad | nginx `more_set_headers`: CSP, HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, COOP, COEP, Permissions-Policy | A9 mitigado; `evidence/fase-4/despues/a9-security-headers.txt` |
| Control de CORS | `proxy_hide_header Access-Control-Allow-Origin` | A8 mitigado |
| Rate limiting de login | nginx `limit_req` 5 req/min por IP, burst 3 | HTTP 429 (A10) |
| Parche virtual asignación masiva | ModSecurity regla propia 100001 (bloquea `role` en POST `/api/Users`) | Regla 100001 en los logs; A7 mitigado |
| Parche virtual `/metrics` | ModSecurity regla propia 100002 | Regla 100002 en los logs |
| Correcciones de código | `app-hardened/patches/` (SQLi, bcrypt, clave a entorno, eval, registro, CORS) | `git apply --check` OK en 6/7 |

El registro legítimo (`POST /api/Users` sin `role`) sigue devolviendo **HTTP 201**: los controles no rompen la
funcionalidad válida (verificado).

## 3. Monitoreo y registro (logging / SIEM)
- **[V]** El WAF registra en formato **JSON** (`MODSEC_AUDIT_LOG_FORMAT=JSON`, `MODSEC_AUDIT_ENGINE=RelevantOnly`)
  en `deploy/hardened/logs/` (montado) y se recolectó en `evidence/fase-6/waf-logs/modsec-audit.log`.
  `evidence/fase-6/waf-logs/resumen-bloqueos.md` resume las reglas que dispararon durante los ataques.
- **[V]** Trazabilidad de eventos de seguridad: cada bloqueo incluye `rule id`, `msg`, `uri`, `client` y
  `anomaly score`, suficiente para alimentar un SIEM.
- **[P]** Pila SIEM (Grafana Loki + Promtail, o Wazuh): se propone `promtail` leyendo
  `deploy/hardened/logs/audit.log` → Loki → panel Grafana con alertas por `anomaly score` y por regla 1000xx.
  No se desplegó para no añadir servicios con consumo elevado en el equipo del laboratorio.

## 4. Correlación amenaza → requisito → control → evidencia → residual
Se cierra la trazabilidad iniciada en la Fase 1 (`docs/fase-1` §7). Cada fila de `docs/fase-6/matriz-riesgo.md`
enlaza la amenaza (STRIDE/Top 10 2025), el requisito ASVS 5.0.0, el control (WAF y/o parche), la evidencia de
bloqueo y el riesgo residual.

## 5. Tratamiento del riesgo (ISO/IEC 27005)
Resumen (detalle en la matriz §5):
- **Mitigar:** 11/11 ataques, con WAF + hardening de contenedor + parches de código.
- **Transferir:** controles gestionados de AWS (WAFv2, responsabilidad compartida) en el despliegue cloud (Fase 2).
- **Aceptar:** residual bajo de CRS paranoia 1 en el laboratorio.
- **Evitar:** no exponer la app vulnerable; retirar el modo `unsafe`.

## 6. Límites y trabajo propuesto
- Recompilar `app-hardened` con los parches y reejecutar los ataques **sin WAF** cuantificaría el residual por
  código puro; aquí el residual medido usa el WAF como control compensatorio.
- Actualización de dependencias con CVE (crypto-js, lodash, marsdb…) — rompe retos de Juice Shop; se documenta en
  el SCA (Fase 3) y queda **[P]**.
- Despliegue del SIEM y de la arquitectura cloud (Fase 2) requiere recursos/aprobación de costos.
