# Evidencia del cierre definitivo de la Fase 6 — 2026-11-21

Rama `cierre/fase6-definitiva` (derivada de `cierre/hito-a-local` = `9173cd9`; `main` = `cc08374`, sin cambios).
Todo se ejecutó contra instancias propias en `127.0.0.1` o en redes Docker internas sin puertos publicados. Tokens,
claves y la ruta del usuario local están redactados. Integridad: `evidence/MANIFEST.sha256`; registro: `evidence/bitacora.md`.

**Configuración vigente** = `make ops-corregido-up` (proyecto Compose `juice-corregida-defensa`): variante corregida
(parches 01-10) + WAF ModSecurity 3.0.17 / CRS 4.25.2 + RASP Aikido Zen 1.8.46 + SIEM Alloy → Loki → Grafana.

| Carpeta | Qué contiene | Resultado clave |
|---|---|---|
| `00-preflight/` | SHA de ramas y submódulo, servicios, configuración resuelta (sin secretos), imágenes con etiquetas de trazabilidad, endurecimiento por contenedor | Puertos solo en 127.0.0.1; app sin root, FS de solo lectura, `cap_drop ALL`; secreto montado |
| `01-build/` | `construir-corregida.log` | Fuente = diff auditado (`app-hardened/patches/v2/correcciones-fase6.patch`), 9 archivos; imágenes con ID |
| `02-bola-recursos/` | BOLA fuera de las cestas: línea base oficial, corregida antes y después del parche 10 | Oficial 6 VULNERABLE; hito A 6 VULNERABLE; con parche 10: 0 VULNERABLE / 10 PROTEGIDO, 7/7 operaciones del propietario |
| `03-escenario-A-vulnerable/` | A1-A12 contra la imagen oficial (instancia temporal en red interna) | 11/11 + A12 VULNERABLE |
| `04-escenario-B-corregida/` | Corregida sin WAF ni RASP: regresión, A1-A12, BOLA de recursos | Regresión 16/16 (token antiguo 401); 6 abiertos de configuración (A4-A6, A9-A11); BOLA 0 |
| `05-escenario-C-corregida-rasp/` | Corregida + RASP, atacando la app sin pasar por el WAF | Regresión 15/15; RASP bloquea A1 con 403; 0 reinicios |
| `06-escenario-D-defensa-completa/` | Defensa completa vía 127.0.0.1:8088: regresión, tráfico legítimo, A1-A12, BOLA de recursos. `previo-ajuste-waf/` = corrida anterior a los ajustes del WAF | Regresión 15/15; A1-A11 0 VULNERABLE; A12 403; BOLA 0/10; códigos 200/201/400/403 (sin 000 ni 5xx) |
| `07-waf/` | Inventario CRS cargado; pruebas por familia; falsos positivos medidos (configuración histórica vs. vigente) | XSS/LFI/SQLi 403 con IDs de regla; histórica 7 bloqueos legítimos, vigente 35/35 |
| `08-trivy/` | Trivy de las imágenes EN EJECUCIÓN (histórica vs. vigente) y análisis de dependencias | CRITICAL 11→9, HIGH 33→27; clave privada embebida eliminada; 3 secretos de ejemplo/prueba; 8 CRITICAL en dependencias (pendiente) |
| `09-rasp/` | Modo monitoreo y modo bloqueo por separado (dos corridas: antes y después del ajuste de ingesta) | Monitoreo 5/5 detectados (app 401); bloqueo 5/5 403 en ~0,02 s; 0 reinicios |
| `10-siem/` | Ingesta por fuente, estado de las 9 reglas (tráfico legítimo / disparadores), alerta de ingesta, proxy del socket, redacción de tokens, captura real de Grafana | 8/8 reglas de ataque firing; BOLA de alta confianza inactiva con tráfico legítimo; ingesta ausente pending→firing→resuelta |

## Hallazgos nuevos de este cierre (todos corregidos y verificados salvo lo indicado)
1. BOLA en artículos de cesta, direcciones y opiniones en la variante del hito A → **parche 10**.
2. WAF: falsos positivos que rompían la interfaz real (PUT/DELETE por 911100; `whoami` por 932260) → `ALLOWED_METHODS` y exclusión acotada.
3. SIEM: el audit log enviaba `Authorization`/cookies (JWT) a Loki y a Grafana → redacción en Alloy. **Pendiente:** las líneas anteriores al ajuste siguen en Loki (purgarlas borra datos: requiere autorización).
4. SIEM: pérdida de líneas al recrear contenedores (descubrimiento cada 60 s) → 5 s; hueco residual documentado.
5. SIEM: sin latido no se podía detectar la pérdida de ingesta → latido del WAF + regla `Ingesta_WAF_Ausente`.
6. Configuración: el stack corregido compartía proyecto, volúmenes y logs con el histórico → proyecto `juice-corregida-defensa` y `logs-corregido/`.
7. Respuestas 5xx de la capa REST genérica (finale) incluyen el mensaje de la base de datos (`SQLITE_CONSTRAINT…`), sin traza de pila → **pendiente**.

## Notas de lectura
- Una prueba con 000, 5xx inesperado o sin objeto creado se marca NO CONCLUYENTE, nunca como mitigación.
- `trivy-juice-corregida-rasp.json` informa 0 secretos, pero la cifra válida es 3 (ver `08-trivy/resumen-trivy.md`).
- La captura `10-siem/capturas/grafana-dashboard-siem-vigente.png` se tomó con Chromium sin interfaz dentro de la red del
  SIEM, con la ventana posterior a la redacción (`ventana-captura.txt`). Una primera captura mostraba un JWT y se borró sin versionarse.
