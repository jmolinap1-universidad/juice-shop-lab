# Guía de demostración en vivo — Fase 6 (5-10 minutos)

Todo corre en el equipo del presentador: la aplicación **no** se publica en Internet (solo `127.0.0.1`). Los resultados
«esperados» son los observados en `evidence/fase-6/cierre-final-2026-11-21/`.

## 0. Antes de la exposición (una sola vez, ~10 min)
Abrir **Git Bash** en la carpeta del proyecto (en PowerShell, `bash` abre WSL, no Git Bash; ver §6).
```bash
docker info --format '{{.ServerVersion}}'          # Docker Desktop encendido
bash scripts/construir-corregida.sh                 # = make corregida-build: construye y VERIFICA la variante corregida
```
Esperado: `ok  fuente = diff auditado (...correcciones-fase6.patch), 9 archivos cambiados` y `RESULTADO: ÉXITO`.

## 1. Levantar la configuración vigente (1 min)
```bash
WAF_PORT=8088 bash scripts/ops-corregido.sh up      # = make ops-corregido-up WAF_PORT=8088
```
Esperado: seis contenedores `running`, `juice-hardened` y `juice-waf` con `salud=healthy`, `reinicios=0`,
`variante=corregida`, y solo puertos `127.0.0.1:8088` (WAF), `127.0.0.1:3001` (Grafana), `127.0.0.1:3100` (Loki).
**Qué explicar:** la app no tiene puerto publicado; el único acceso es el WAF. Si el stack histórico estuviera activo, el
script se niega a arrancar (evita confundir la imagen vulnerable con la corregida).

## 2. Uso legítimo y bloqueo del WAF (1 min)
```bash
curl -s -o /dev/null -w 'busqueda legitima: %{http_code}\n' 'http://127.0.0.1:8088/rest/products/search?q=apple'
curl -s -o /dev/null -w 'ruta sensible /ftp: %{http_code}\n' http://127.0.0.1:8088/ftp
curl -s -o /dev/null -w 'inyeccion SQL: %{http_code}\n' -G --data-urlencode "q=')) UNION SELECT 1--" http://127.0.0.1:8088/rest/products/search
curl -sI http://127.0.0.1:8088/ | grep -iE 'content-security-policy|strict-transport|x-frame'
```
Esperado: `200`, `403`, `403` y las cabeceras de seguridad. **Qué explicar:** el WAF (ModSecurity + OWASP CRS) bloquea por
reglas (942 = SQLi) y por rutas; las cabeceras las añade el proxy.

## 3. Autorización por objeto (BOLA) corregida en el código (1-2 min)
```bash
BOLA_PAUSA=13 bash security/ops/bola-recursos.sh http://127.0.0.1:8088 "$TEMP/bola-demo.md" | tail -16
```
Esperado: `0 VULNERABLE, 10 PROTEGIDO` y `Controles positivos: 7 OK`. **Qué explicar:** el WAF no puede saber de quién es
una cesta; lo impide el código (parches 08 y 10) con 403, y el propietario sigue pudiendo operar sus objetos.

## 4. RASP: ataque que esquiva el WAF (1 min)
```bash
MSYS_NO_PATHCONV=1 docker run --rm --network juice-corregida-defensa_interna lab-tools:local \
  curl -s -o /dev/null -w 'inyeccion directa a la app: %{http_code}\n' -X POST http://juice-hardened:3000/rest/user/login \
  -H 'Content-Type: application/json' --data "{\"email\":\"' OR 1=1--\",\"password\":\"x\"}"
docker logs --since 1m juice-hardened 2>&1 | grep -E 'Zen has|rasp-guard'
docker inspect juice-hardened --format 'reinicios={{.RestartCount}} salud={{.State.Health.Status}}'
```
Esperado: `403`, la línea `Zen has blocked an SQL injection ... sqlite3.all` y `reinicios=0`. **Qué explicar:** el RASP
vive dentro del proceso Node; aquí el atacante ya está dentro de la red y no pasa por el WAF. Alcance probado: `sqlite3`.

## 5. SIEM en Grafana (2 min)
Abrir **http://127.0.0.1:3001** → panel «SIEM - Juice Shop endurecido (Fase 6)», rango *Last 15 minutes*.
Consultas para *Explore* (fuente `Loki`):
```
{job="waf_audit"} |= "\"ruleId\":\"942"                                 # auditoría del WAF: SQLi bloqueada
sum by (status) (count_over_time({job="waf_access"} [5m]))              # accesos por código HTTP
{job="docker", container="juice-hardened"} |~ "Zen has (blocked|detected)"   # eventos del RASP
```
Estado de las alertas (Loki ruler):
```bash
curl -s http://127.0.0.1:3100/prometheus/api/v1/rules | grep -oE '"state":"[a-z]+","name":"[A-Za-z_0-9]+"'   # 9 reglas
```
Esperado tras los pasos 2-4: `WAF_InyeccionSQL_Bloqueada`, `Acceso_Rutas_Sensibles_Denegado`, `API_BOLA_AccesoAjenoDenegado`
y `RASP_Ataque_Detectado` en `firing` (o `pending` durante los primeros segundos). **Qué explicar:** tres fuentes
centralizadas (WAF auditoría, WAF acceso, salida de la app con el RASP); la regla de enumeración BOLA es solo un indicador
(dispara con usuarios legítimos); los tokens se redactan antes de llegar a Loki.

## 6. Riesgo inherente vs. residual (1 min)
Abrir `docs/fase-6/riesgo-vigente/img/heatmap-comparativo.png`. Mensaje: 8 críticos / 16 altos → **1 crítico** (R20,
dependencias con CVE, aceptado temporalmente) / 11 altos / 9 medios / 3 bajos; cada reducción tiene un control probado
(`make risk-vigente`: 324 comprobaciones, 0 fallas). Mostrar `docs/fase-6/CIERRE_FINAL_FASE6.md` §5 (riesgos abiertos).

## 7. Cierre
```bash
bash scripts/ops-corregido.sh down     # = make ops-corregido-down; NO borra volúmenes
```

## Contingencias
| Problema | Solución |
|---|---|
| El 8080 está ocupado | Usar `WAF_PORT=8088` (ya incluido en esta guía) |
| `RECHAZADO: el stack HISTÓRICO ... está activo` | `cd deploy/hardened && docker compose -f docker-compose.yml -f docker-compose.ops.yml down` |
| `Falta juice-corregida...: ejecute make corregida-build` | Paso 0 |
| Docker Desktop detenido | Abrir Docker Desktop y esperar a que `docker info` responda |
| Login con 429 | Es el límite de 5 intentos/min del WAF (control esperado): esperar 60 s |
| Grafana no abre | `docker logs siem-grafana | tail`; mientras tanto, usar las consultas por API: `curl -s -G http://127.0.0.1:3100/loki/api/v1/query --data-urlencode 'query=sum(count_over_time({job="waf_access"}[15m]))'` |
| El panel no muestra el evento del RASP | Alloy descubre contenedores cada 5 s: repetir el paso 4 si la app se acababa de recrear |
| Sin red para descargar imágenes | Construir y arrancar todo antes de la exposición (paso 0 y 1) |

### Desde PowerShell (sin Git Bash abierto)
Desde la carpeta del proyecto:
```powershell
$env:WAF_PORT = '8088'; & "C:\Program Files\Git\bin\bash.exe" scripts/ops-corregido.sh up
& "C:\Program Files\Git\bin\bash.exe" scripts/ops-corregido.sh ps
curl.exe -s -o NUL -w "busqueda legitima: %{http_code}`n" "http://127.0.0.1:8088/rest/products/search?q=apple"
curl.exe -s -o NUL -w "ruta sensible /ftp: %{http_code}`n" "http://127.0.0.1:8088/ftp"
```

## Guion breve por herramienta
- **WAF (Nginx + ModSecurity 3 + OWASP CRS 4.25):** filtra en el perímetro por firmas y anomalías; además oculta CORS, añade
  cabeceras, limita el login y aplica dos parches virtuales. No entiende de propietarios de datos.
- **Código corregido (parches 01-10):** elimina la causa: consultas parametrizadas, contraseñas con scrypt, clave JWT fuera del
  código, lista blanca en el registro, verificación de propietario, errores sin trazas.
- **RASP (Aikido Zen + rasp-guard):** dentro del proceso; ve la consulta SQL real y la frena aunque el WAF sea evadido.
- **SIEM (Alloy → Loki → Grafana):** reúne los registros, correlaciona con 9 reglas y muestra el panel; avisa si deja de
  recibir datos.
- **Gestión del riesgo (ISO/IEC 27005):** cada riesgo con decisión (aceptar, eliminar, evitar, mitigar, transferir), residual
  justificado solo con controles probados y mapas de calor generados desde datos versionados.
