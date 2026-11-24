#!/usr/bin/env bash
# Construye la VARIANTE CORREGIDA de Juice Shop (hito A) desde el submódulo app/ fijado, sin modificar app/.
#   1) comprueba que app/ está en v20.3.0 (f189f5212) y sin cambios
#   2) exporta app/ con finales LF a app-hardened/build/{orig,src} (carpeta ignorada por git)
#   3) aplica 02, 05, 06, 07, 08 con git apply aislado del repositorio superior y comprueba que CADA archivo cambió
#   4) aplica las correcciones v2 (01, 03, 04, 09) con aplicar_v2.py y el parche 10 (BOLA fuera de las cestas,
#      cierre de la Fase 6) con aplicar_fase6.py (reemplazos literales verificados)
#   5) regenera el diff y lo compara con el diff auditado vigente (clave redactada); si difiere, se detiene
#      (la fuente construida no es la auditada). Vigente: app-hardened/patches/v2/correcciones-fase6.patch
#      (= correcciones-hito-a.patch + parche 10). HITO_A=1 construye la variante del hito A (sin el parche 10).
#   6) construye juice-corregida:local y, con el RASP, juice-corregida-rasp:local
# Uso: bash scripts/construir-corregida.sh [archivo-de-registro]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export MSYS_NO_PATHCONV=1
PY=python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
APP_ESPERADO=f189f521266f42c6bd05884468292000cee852ed
LOG="${1:-/dev/null}"
hostpath() { if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else printf '%s' "$1"; fi; }
log() { printf '%s\n' "$*" | tee -a "$LOG"; }

: > "$LOG"
log "# Construcción de la variante corregida — $(date -Iseconds)"
APP="$(git -C app rev-parse HEAD)"
[ "$APP" = "$APP_ESPERADO" ] || { log "FALLO: app/ está en $APP, se esperaba $APP_ESPERADO"; exit 1; }
git -C app diff --quiet && git -C app diff --cached --quiet || { log "FALLO: app/ tiene cambios locales"; exit 1; }
log "app/ = $APP (v20.3.0), sin cambios"

rm -rf app-hardened/build/orig app-hardened/build/src
mkdir -p app-hardened/build/orig app-hardened/build/src
git -c core.autocrlf=false -C app archive --format=tar HEAD | tar -x -C app-hardened/build/orig
git -c core.autocrlf=false -C app archive --format=tar HEAD | tar -x -C app-hardened/build/src
log "exportado app/ (LF) a app-hardened/build/orig y src"

# Aísla git del repositorio superior (si no, omite en silencio los parches con formato `diff --git`). En Git Bash la
# ruta se convierte explícitamente (con MSYS_NO_PATHCONV=1 git.exe no entendería /c/...).
if command -v cygpath >/dev/null 2>&1; then GIT_CEILING_DIRECTORIES="$(cygpath -m "$ROOT/app-hardened/build")"; else GIT_CEILING_DIRECTORIES="$ROOT/app-hardened/build"; fi
export GIT_CEILING_DIRECTORIES
declare -A ARCH=([02-sqli-search]=routes/search.ts [05-eval-userprofile]=routes/userProfile.ts
                 [06-asignacion-masiva-registro]=server.ts [07-cors-restringido]=server.ts [08-bola-cesta-propietario]=routes/basket.ts)
for p in 02-sqli-search 05-eval-userprofile 06-asignacion-masiva-registro 07-cors-restringido 08-bola-cesta-propietario; do
  antes="$(sha256sum "app-hardened/build/src/${ARCH[$p]}" | cut -c1-64)"
  salida="$(cd app-hardened/build/src && git -c core.autocrlf=false apply -v "../../patches/$p.patch" 2>&1)"
  despues="$(sha256sum "app-hardened/build/src/${ARCH[$p]}" | cut -c1-64)"
  if ! printf '%s' "$salida" | grep -q 'Applied patch' || [ "$antes" = "$despues" ]; then
    log "FALLO: el parche $p no cambió ${ARCH[$p]} (salida: $salida)"; exit 1
  fi
  log "ok  parche $p -> ${ARCH[$p]}"
done

docker run --rm -v "$(hostpath "$ROOT/app-hardened"):/h" "$PY" python -I /h/aplicar_v2.py /h/build/src | tee -a "$LOG"
# VARIANTE_OBJETIVO: hito-a (01-09) · fase6 (+10) · cierre (+11 y 12, por defecto desde el cierre técnico 2026-11-23).
# HITO_A=1 se mantiene como sinónimo de VARIANTE_OBJETIVO=hito-a.
OBJ="${VARIANTE_OBJETIVO:-cierre}"; [ "${HITO_A:-0}" = 1 ] && OBJ=hito-a
ARCHIVOS="lib/insecurity.ts models/user.ts routes/login.ts routes/changePassword.ts routes/2fa.ts server.ts routes/search.ts routes/userProfile.ts routes/basket.ts"
ESPERADOS=9
case "$OBJ" in
  hito-a) AUDITADO=app-hardened/patches/v2/correcciones-hito-a.patch; VARIANTE=corregida-hito-a ;;
  fase6|cierre)
    docker run --rm -v "$(hostpath "$ROOT/app-hardened"):/h" "$PY" python -I /h/aplicar_fase6.py /h/build/src | tee -a "$LOG"
    AUDITADO=app-hardened/patches/v2/correcciones-fase6.patch; VARIANTE=corregida-fase6
    if [ "$OBJ" = cierre ]; then
      docker run --rm -v "$(hostpath "$ROOT/app-hardened"):/h" "$PY" python -I /h/aplicar_cierre_tecnico.py /h/build/src | tee -a "$LOG"
      AUDITADO=app-hardened/patches/v2/correcciones-cierre-tecnico.patch; VARIANTE=corregida-cierre-tecnico
      ARCHIVOS="$ARCHIVOS package.json lib/utils.ts lib/xml.ts routes/showProductReviews.ts routes/trackOrder.ts routes/updateProductReviews.ts routes/profileImageUrlUpload.ts routes/recycles.ts frontend/src/app/search-result/search-result.component.ts routes/b2bOrder.ts routes/chat.ts models/index.ts"
      ESPERADOS=21
    fi ;;
  *) log "FALLO: VARIANTE_OBJETIVO desconocida: $OBJ"; exit 1 ;;
esac
GEN="app-hardened/build/correcciones-regenerado.patch"
: > "$GEN"
for f in $ARCHIVOS; do
  diff -u --label "a/$f" --label "b/$f" "app-hardened/build/orig/$f" "app-hardened/build/src/$f" >> "$GEN" || true
done
sed -i "s#^-const privateKey = '-----BEGIN RSA PRIVATE KEY-----.*#-const privateKey = '[REDACTADO: clave privada de prueba de Juice Shop; no se versiona]'#" "$GEN"
CAMBIADOS="$( { diff -rq app-hardened/build/orig app-hardened/build/src || true; } | wc -l)"
if [ "${GENERAR_DIFF:-0}" = 1 ]; then
  # Solo para registrar un cambio de código YA revisado: escribe el diff auditado (debe revisarse antes de commitear).
  cp "$GEN" "$AUDITADO"; log "AVISO: diff auditado reescrito en $AUDITADO (revisar antes de commitear)"
fi
if cmp -s "$GEN" "$AUDITADO" && [ "$CAMBIADOS" = "$ESPERADOS" ]; then
  log "ok  fuente = diff auditado ($AUDITADO), $ESPERADOS archivos cambiados; variante $VARIANTE"
else
  log "FALLO: la fuente construida no coincide con $AUDITADO ($CAMBIADOS archivos distintos)"; diff "$GEN" "$AUDITADO" | head -20 | tee -a "$LOG"; exit 1
fi
FUENTE="$(sha256sum "$GEN" | cut -c1-64)"

log "docker build juice-corregida:local ..."
docker build -q -f app-hardened/Dockerfile --label "masi.variante=$VARIANTE" --label "masi.fuente.diff.sha256=$FUENTE" \
  --label "masi.app.commit=$APP" -t juice-corregida:local app-hardened/build/src >> "$LOG" 2>&1 \
  || { log "FALLO: docker build de la variante (ver $LOG)"; exit 1; }
log "imagen juice-corregida:local = $(docker image inspect juice-corregida:local --format '{{.Id}}')"
docker build -q -f deploy/hardened/Dockerfile.rasp --build-arg BASE_IMAGE=juice-corregida:local \
  --label "masi.variante=$VARIANTE+rasp" -t juice-corregida-rasp:local deploy/hardened >> "$LOG" 2>&1 \
  || { log "FALLO: docker build con RASP (ver $LOG)"; exit 1; }
log "imagen juice-corregida-rasp:local = $(docker image inspect juice-corregida-rasp:local --format '{{.Id}}')"
log "RESULTADO: ÉXITO"
