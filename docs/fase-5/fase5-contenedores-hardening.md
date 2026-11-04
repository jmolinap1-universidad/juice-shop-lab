# Fase 5 – Seguridad de contenedores y hardening

**Estado:** Implementado y verificado. Escaneos con Trivy 0.75.0, Hadolint 2.15.1 y Checkov 3.4.0 (vía Docker,
versiones fijas); runtime endurecido construido y ejecutado en local, verificado con `docker inspect`.

> Etiquetas: **[V]** verificado · **[S]** simulado · **[P]** propuesto.
> Alcance de esta fase: endurecer **imagen, Dockerfile y runtime del contenedor** y escanear IaC de despliegue.
> Las **CVE de las dependencias de la aplicación** (crypto-js, lodash, marsdb, etc.) pertenecen al código y se
> corrigen en la **Fase 6** (`app-hardened`), no al empaquetado de la imagen.

## 1. Escaneo de la imagen (Trivy) — antes vs. después
`evidence/fase-5/antes/resumen-trivy.md` y `evidence/fase-5/despues/resumen-trivy.md`.

| Métrica | Imagen original | Imagen endurecida | Comentario |
|---|---|---|---|
| CRITICAL | 11 | 11 | Idénticas: mismo árbol de la app |
| HIGH | 32 | 32 | Idénticas |
| MEDIUM / LOW / UNKNOWN | 71 / 11 / 1 | 71 / 11 / 1 | Idénticas |
| Origen de las CVE | 81 en dependencias Node.js, 45 en el SO base (debian 13) | igual | — |
| Secretos | 5 (clave privada en `build/lib/insecurity.js`, JWT de prueba) | 5 | Son material de reto del propio código |
| Malas configuraciones | 66 | 66 | Provienen de archivos de reto incrustados (`data/static/codefixes/*.tf`, `infrastructure/`), no del despliegue |

**Hallazgo clave (honesto):** repaquetar o re-etiquetar la imagen **no reduce** las CVE de dependencias ni los
secretos de reto, porque residen en el código fuente de Juice Shop. Su tratamiento es la Fase 6 (actualización de
dependencias y eliminación de claves embebidas en `app-hardened`). Lo que la Fase 5 **sí** mejora de forma
medible es la higiene del Dockerfile y el endurecimiento del runtime (secciones 2 y 3).

## 2. Hardening del Dockerfile (Hadolint) — antes vs. después
`evidence/fase-5/antes/resumen-hadolint.md` → `evidence/fase-5/despues/resumen-hadolint.md`.

| Dockerfile | Avisos Hadolint |
|---|---|
| `app/Dockerfile` (original) | **11** (10× DL3059 RUN consecutivos, 1× DL3006 imagen sin fijar) |
| `app-hardened/Dockerfile` | **0** |

Cambios aplicados en `app-hardened/Dockerfile`:
- Imágenes base fijadas por **digest** (`node:24-bookworm-slim@sha256:…`, `distroless/nodejs24@sha256:…`): integridad de la cadena de suministro.
- Instrucciones `RUN` consolidadas en una sola capa (menos capas, menor superficie).
- `npm install --omit=dev --ignore-scripts` (evita scripts de postinstalación de terceros en producción).
- `HEALTHCHECK` para detección de fallos por el orquestador.
- Usuario no root `65532` y `WORKDIR` dedicado (conservados del original).

## 3. Hardening del runtime (verificado con `docker inspect`)
`deploy/hardened/docker-compose.yml` + `deploy/hardened/Dockerfile`. Evidencia: `evidence/fase-5/despues/runtime-hardening-inspect.txt`.

| Control | Valor verificado | Riesgo que mitiga |
|---|---|---|
| Root filesystem de solo lectura | `ReadonlyRootfs = true`; escritura en `/juice-shop` → **EROFS** | Persistencia de webshells, manipulación de binarios |
| Capacidades de Linux | `CapDrop = [ALL]`, `CapAdd = []` | Escalada por capacidades (p. ej. NET_RAW, DAC_OVERRIDE) |
| Sin nuevos privilegios | `SecurityOpt = [no-new-privileges:true]` | Escalada por binarios setuid |
| Usuario no root | `User = 65532:0` | Compromiso con privilegios de root en el contenedor |
| Límite de procesos | `PidsLimit = 200` | Fork bombs / DoS (T18) |
| Límite de memoria/CPU | `Memory = 1 GiB`, `cpus = 1.0` | Agotamiento de recursos del host |
| Modo de ejecución | `NODE_ENV = production` (no el `unsafe` del laboratorio) | Funciones de depuración/reto expuestas |
| HEALTHCHECK | definido en la imagen (`docker inspect` lo muestra) | Detección y reinicio ante fallos |

El filesystem de solo lectura es compatible con Juice Shop usando **volúmenes nombrados sembrados desde la
imagen** solo en las rutas que la app escribe al iniciar (`data`, `ftp`, `.well-known`, `frontend/dist`, `i18n`)
y `tmpfs` para `/tmp` y `logs`. Resultado: la app responde **HTTP 200** y el resto del sistema de archivos
permanece inmutable (0 errores EROFS en el arranque; escritura en `/` bloqueada, comprobado).

## 4. IaC de despliegue (Checkov)
`evidence/fase-5/iac/`. Frameworks `dockerfile` y `yaml` sobre `deploy/` y `app-hardened/`.

| Resultado | Valor |
|---|---|
| Passed | 47 |
| Failed | 0 |
| Skipped | 0 |

(La arquitectura cloud Terraform se cubre en la Fase 2: Checkov 144/0 con 5 omisiones justificadas.)

## 5. Trazabilidad y límites
- **Docker Bench for Security:** **[P]** pendiente; requiere acceso al daemon del host. Los controles que
  evalúa (usuario no root, capacidades, FS de solo lectura, límites) ya están aplicados y verificados aquí.
- **WAF (Nginx + ModSecurity + OWASP CRS 4.25.2):** declarado en `deploy/hardened/docker-compose.yml`; su
  configuración, reglas y evidencia de bloqueo se desarrollan en la **Fase 6**.
- Lo medido en esta fase alimenta la columna "control de contenedor/host" de la matriz de riesgo residual (Fase 6).
