# Riesgo residual tras el hito A (variante corregida + defensa en profundidad)

> Generado por `datos/generar_comparativo_riesgo.py` a partir de `docs/fase-6/datos/riesgos-calculados.json` (v2) y
> `riesgo-hito-a/riesgos-calculados.json`. El registro del hito A se construye con `datos/construir_riesgos_hito_a.py`
> (delta explícito sobre v2) y se valida con el mismo `riesgo.py` de la Fase 6: 307 comprobaciones, 0 fallas.

**Configuración evaluada:** Variante corregida (juice-corregida:local, parches 02, 05-08 y v2 01/03/04/09) + WAF + RASP + SIEM (deploy/hardened/docker-compose.corregido.yml). Delta aplicado por construir_riesgos_hito_a.py.

**Alcance de la afirmación:** el residual del hito A vale para esa configuración. La configuración por defecto del
repositorio (`make ops-up`, imagen oficial + WAF/RASP/SIEM) conserva el residual v2 de la Fase 6.

## 1. Distribución por nivel
| Nivel | Inherente | Residual v2 (Fase 6) | Residual hito A |
|---|---|---|---|
| Bajo | 0 | 1 | 3 |
| Medio | 0 | 7 | 8 |
| Alto | 16 | 12 | 11 |
| Crítico | 8 | 4 | 2 |

## 2. Riesgos que cambian
| Riesgo | Inherente | Residual v2 | Residual hito A | Control que lo justifica (evidencia) | Razón de P |
|---|---|---|---|---|---|
| R01 Inyección SQL en el login (bypass de autenticación) | 5×5=25 Crítico | 2×5=10 Alto | **1×5=5 Medio** | Parche 01 v2: consulta parametrizada + verificación scrypt (variante corregida); A1 sin token y HTTP 401 sin WAF ni RASP [probado] (`evidence/cierre-2026-11-20/03-corregida-sin-waf/resumen-ataques.md`) | Causa eliminada y probada SIN WAF ni RASP (A1 → 401, sin token); WAF y RASP quedan como capas adicionales (el RASP bloqueó además el mismo payload, escenario 05): P=1. |
| R02 Inyección SQL UNION en búsqueda (extracción de tablas) | 5×5=25 Crítico | 2×5=10 Alto | **1×5=5 Medio** | Parche 02: consulta parametrizada en la búsqueda (variante corregida); A2 y A3 sin datos sin WAF ni RASP y búsqueda legítima con resultados [probado] (`evidence/cierre-2026-11-20/03-corregida-sin-waf/resumen-ataques.md`) | Causa eliminada y probada sin WAF ni RASP (A2/A3 mitigados; la búsqueda legítima devuelve productos): P=1. |
| R03 Clave privada JWT embebida en el código (forja de tokens) | 4×5=20 Crítico | 4×5=20 Crítico | **2×5=10 Alto** | Parche 04 v2: clave privada fuera del código, cargada de un secreto montado y rotada; un token firmado con la clave antigua recibe HTTP 401 [probado] (`evidence/cierre-2026-11-20/03-corregida-sin-waf/regresion-funcional.md`)<br>Arranque fail-closed: sin secreto la aplicación no inicia (código de salida 1) [probado] (`evidence/cierre-2026-11-20/03-corregida-sin-waf/arranque-sin-secreto.txt`) | La clave embebida ya no está en la imagen (Trivy: sin secreto private-key en insecurity.ts/.js) y los tokens de la clave antigua se rechazan: la causa se eliminó. No baja a 1 porque la clave nueva es un archivo en el host, sin gestor de secretos/KMS ni rotación automática. |
| R05 Contraseñas con MD5 sin sal | 4×5=20 Crítico | 3×5=15 Alto | **1×5=5 Medio** | Parche 03 v2: scrypt con sal aleatoria (sin dependencias nuevas); 27/27 usuarios con scrypt, login y cambio de contraseña probados [probado] (`evidence/cierre-2026-11-20/03-corregida-sin-waf/regresion-funcional.md`) | MD5 sin sal eliminado para todas las cuentas (27/27 scrypt en la base del contenedor); revertir un hash filtrado deja de ser trivial: P=1. La ruta 2FA usa la misma función pero no se ejercitó. |
| R06 BOLA/IDOR: lectura de recursos de otro usuario | 5×4=20 Crítico | 5×4=20 Crítico | **3×4=12 Alto** | Parche 08: verificación de propietario en /rest/basket/:id (variante corregida); A12 → 403 y la cesta propia → 200 [probado] (`evidence/cierre-2026-11-20/03-corregida-sin-waf/bola/resultado-bola.md`) | La lectura cruzada de cestas queda bloqueada en el código (403 sin WAF, con RASP y con la defensa completa): P-2. No baja más porque la verificación de propietario no cubre Addresses, Cards ni Feedbacks. |
| R07 Asignación masiva de role=admin en el registro | 4×4=16 Alto | 2×4=8 Medio | **1×4=4 Bajo** | Parche 06: lista blanca de campos en el registro (variante corregida); role=admin ignorado (role customer) sin WAF [probado] (`evidence/cierre-2026-11-20/03-corregida-sin-waf/resumen-ataques.md`) | Causa eliminada y probada sin WAF (A7: role customer); el parche virtual del WAF queda como capa adicional: P=1. |
| R09 Ejecución de código vía eval()/vm | 3×5=15 Alto | 3×4=12 Alto | **3×4=12 Alto** | Parche 05: eval() eliminado en routes/userProfile.ts (revisado en el diff). No ejercitable dinámicamente: Juice Shop desactiva esa rama en Docker (safetyMode auto, disabledEnv Docker) [inspeccionado] (`app-hardened/patches/v2/correcciones-hito-a.patch`) | No hay control preventivo probado sobre eval/vm (el RASP instrumenta node:vm, pero no se ejercitó). |
| R14 CORS permisivo (ACAO *) | 4×3=12 Alto | 2×3=6 Medio | **1×3=3 Bajo** | Parche 07: CORS con origen explícito (variante corregida); sin ACAO abierto con Origin externo y sin WAF [probado] (`evidence/cierre-2026-11-20/03-corregida-sin-waf/resumen-ataques.md`) | Causa eliminada y probada sin WAF (A8 mitigado): P=1. |

## 3. Lo que NO cambia y por qué
- **I (impacto)** no baja en ningún riesgo corregido: la convención del equipo solo reduce I con contención o respuesta probadas.
- **R09** (eval): el parche 05 está aplicado, pero la rama de código está desactivada en Docker; queda «inspeccionado» y no reduce.
- **R20** (dependencias con CVE): Trivy baja de 11 a 9 CRITICAL en la variante (`evidence/cierre-2026-11-20/02-escaneos/resumen-trivy.md`), pero quedan 8 CRITICAL en dependencias que no se actualizaron; la aceptación temporal sigue vigente.
- **R23** (datos personales): sigue Crítico en este registro. La extracción por SQLi está eliminada, pero no se re-evaluó con el equipo el resto de vías (BOLA en otros recursos, XXE): queda como candidato a revisión, no como reducción.

## 4. Riesgos que siguen Crítico en el hito A
- **R20 Dependencias con CVE críticas (cadena de suministro)** — 4×5=20. Pendiente: Actualizar crypto-js, lodash, marsdb y demás en un entorno que no dependa de los retos
- **R23 Exposición de datos personales (incumplimiento de protección de datos)** — 4×5=20. Pendiente: Re-evaluar con el equipo las vías restantes de extracción (BOLA en Addresses/Cards/Feedbacks, XXE R10) tras eliminar la SQLi y el BOLA de cestas; póliza o cláusulas si hubiera datos reales

Mapas de calor: `riesgo-hito-a/img/` (mismo generador que la Fase 6).
