# Fase 6 – Matriz de riesgo: inherente vs. residual

**Estado:** Implementado y verificado. El riesgo **inherente** se midió en el laboratorio vulnerable (Fase 4) y
el **residual** reejecutando exactamente los mismos ataques (`security/attacks/run.sh`) contra el entorno
endurecido (`deploy/hardened`: app con FS de solo lectura + WAF ModSecurity/CRS). Evidencia:
`evidence/fase-4/antes/`, `evidence/fase-4/despues/`, `evidence/fase-6/waf-logs/`.

## 1. Resultado global
| | Inherente (laboratorio) | Residual (endurecido) |
|---|---|---|
| Observaciones de ataque (4 explotación demostrada + 7 debilidades) | **11 detectadas** | **0 activas** (todas bloqueadas) |
| Evidencia | `evidence/fase-4/antes/resumen-ataques.md` | `evidence/fase-4/despues/resumen-ataques.md` + logs del WAF |

## 2. Rúbrica DREAD (igual que Fase 1)
Riesgo = promedio de D,R,E,A,D (1-10): ≥8 crítico · 6-7.9 alto · 4-5.9 medio · <4 bajo.
El residual recalcula Reproducibilidad/Explotabilidad/Descubribilidad tras el control (el Daño potencial no cambia,
pero la probabilidad de alcanzarlo cae).

## 3. Matriz por vulnerabilidad
| ID | Vulnerabilidad | CWE | DREAD inh. | Nivel inh. | Control aplicado (evidencia) | DREAD res. | Nivel res. | Tratamiento ISO/IEC 27005 |
|---|---|---|---|---|---|---|---|---|
| A1 | SQLi bypass de login | CWE-89 | 9.6 | Crítico | WAF CRS 942100 libinjection (score 8 → 403); código: `01-sqli-login.patch` | 2.2 | Bajo | Mitigar |
| A2 | SQLi UNION (volcado Users) | CWE-89 | 9.0 | Crítico | WAF CRS 942xxx (403); código: `02-sqli-search.patch` | 2.2 | Bajo | Mitigar |
| A3 | SQLi enumeración de esquema | CWE-89 | 8.0 | Crítico | WAF CRS (403); código: `02-sqli-search.patch` | 2.0 | Bajo | Mitigar |
| A4 | Listado de directorios | CWE-548 | 9.0 | Crítico | nginx `deny` /ftp,/encryptionkeys,/support/logs (403) | 2.0 | Bajo | Mitigar |
| A5 | Exposición de documento interno `/ftp` | CWE-538 | 7.0 | Alto | nginx `deny` (403) | 2.0 | Bajo | Mitigar |
| A6 | `/metrics` sin autenticación | CWE-200 | 6.4 | Alto | nginx `deny` + ModSecurity VP 100002 (403) | 1.8 | Bajo | Mitigar |
| A7 | Asignación masiva `role=admin` | CWE-915 | 7.2 | Alto | ModSecurity VP 100001 (403); código: `06-asignacion-masiva-registro.patch` | 2.4 | Bajo | Mitigar |
| A8 | CORS permisivo | CWE-942 | 6.6 | Alto | nginx `proxy_hide_header ACAO`; código: `07-cors-restringido.patch` | 2.2 | Bajo | Mitigar |
| A9 | Cabeceras de seguridad ausentes | CWE-693 | 6.0 | Alto | nginx `more_set_headers` (CSP, HSTS, X-CTO, X-Frame, etc.) | 2.0 | Bajo | Mitigar |
| A10 | Fuerza bruta en login | CWE-307 | 7.2 | Alto | nginx `limit_req` 5/min (HTTP 429) | 3.0 | Bajo | Mitigar |
| A11 | Clave privada JWT embebida (y endpoint `/encryptionkeys`) | CWE-798 | 8.6 | Crítico | nginx `deny` /encryptionkeys (403); código: `04` clave a entorno | 2.6 | Bajo | Mitigar |

**Nota sobre riesgo residual bajo, no nulo:** el WAF es un control compensatorio perimetral; la aplicación sigue
siendo vulnerable detrás de él. El residual se reduce aún más al aplicar los parches de código (`app-hardened`),
que eliminan la causa raíz. Vulnerabilidades no cubiertas por estos ataques automatizados (XXE, SSRF, XSS
persistente, IDOR) mantienen su tratamiento **Propuesto** en el código y se apoyan en las reglas CRS mientras tanto.

## 4. Riesgo por capa — residual (comparar con Fase 1 §6)
| Capa | Riesgo inherente (Fase 1) | Control de Fase 5/6 | Riesgo residual |
|---|---|---|---|
| 1. Datos | 16 Crítico | SQLi bloqueada; (cifrado en reposo [P]) | 6 Medio |
| 2a. Código | 16 Crítico | WAF + parches de código | 6 Medio |
| 2b. Aplicación (lógica) | 12 Crítico | VP asignación masiva; parche registro | 6 Medio |
| 2c. Dependencias | 12 Crítico | SCA en CI; actualización [P] Fase 6 | 9 Alto |
| 2d. Perímetro de app | 12 Crítico | WAF, CORS, cabeceras, rate limit | 4 Medio |
| 3. Host/contenedor | 6 Medio | FS solo lectura, cap_drop, no-new-priv, límites | 3 Bajo |
| 7. Políticas/concientización | 9 Alto | Logs del WAF en JSON + bitácora; SIEM [P] | 6 Medio |

## 5. Tratamiento del riesgo (ISO/IEC 27005)
- **Mitigar (aplicado):** A1-A11 mediante WAF + hardening de contenedor + parches de código.
- **Mitigar (propuesto):** actualización de dependencias con CVE (2c), cifrado en reposo de SQLite, parser XML
  sin entidades externas (XXE), lista blanca SSRF, CSP estricta sin `unsafe-inline`.
- **Transferir:** en despliegue cloud (Fase 2), AWS WAF gestionado y responsabilidad compartida del proveedor.
- **Aceptar:** riesgo residual bajo de las reglas CRS en paranoia 1 (posibles evasiones), aceptado para el
  laboratorio; en producción se elevaría la paranoia y se añadiría tuning.
- **Evitar:** no exponer la aplicación vulnerable a Internet (regla de aislamiento); el modo `unsafe` se retira
  en el entorno endurecido (`NODE_ENV=production`).
