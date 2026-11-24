#!/usr/bin/env bash
# Prepara, DENTRO de la construcción de la imagen cloud, la misma fuente corregida que scripts/construir-corregida.sh
# (variante corregida-cierre-tecnico, parches 01-13) y verifica que coincide con el diff auditado. Si no coincide,
# la construcción FALLA: la plataforma no puede desplegar una fuente distinta a la revisada.
#   etapa "git":    clona Juice Shop en el tag fijado, comprueba el commit y aplica 02, 05, 06, 07 y 08 (git apply)
#   etapa "python": aplica 01/03/04/09 (aplicar_v2.py), 10 (aplicar_fase6.py), 11-13 (aplicar_cierre_tecnico.py)
#                   y compara el diff regenerado con app-hardened/patches/v2/correcciones-cierre-tecnico.patch
set -euo pipefail
W=/w
H=/h
APP_TAG="${JUICE_SHOP_TAG:-v20.3.0}"
APP_ESPERADO="${JUICE_SHOP_COMMIT:-f189f521266f42c6bd05884468292000cee852ed}"

case "${1:-}" in
  git)
    git clone --quiet --depth 1 --branch "$APP_TAG" https://github.com/juice-shop/juice-shop.git /tmp/clon
    APP="$(git -C /tmp/clon rev-parse HEAD)"
    [ "$APP" = "$APP_ESPERADO" ] || { echo "FALLO: el tag $APP_TAG apunta a $APP, se esperaba $APP_ESPERADO"; exit 1; }
    mkdir -p "$W/orig" "$W/src"
    git -C /tmp/clon archive --format=tar HEAD | tar -x -C "$W/orig"
    git -C /tmp/clon archive --format=tar HEAD | tar -x -C "$W/src"
    echo "$APP" > "$W/APP_COMMIT"
    declare -A ARCH=([02-sqli-search]=routes/search.ts [05-eval-userprofile]=routes/userProfile.ts
                     [06-asignacion-masiva-registro]=server.ts [07-cors-restringido]=server.ts [08-bola-cesta-propietario]=routes/basket.ts)
    export GIT_CEILING_DIRECTORIES="$W"
    for p in 02-sqli-search 05-eval-userprofile 06-asignacion-masiva-registro 07-cors-restringido 08-bola-cesta-propietario; do
      antes="$(sha256sum "$W/src/${ARCH[$p]}" | cut -c1-64)"
      salida="$(cd "$W/src" && git apply -v "$H/patches/$p.patch" 2>&1)"
      despues="$(sha256sum "$W/src/${ARCH[$p]}" | cut -c1-64)"
      if ! printf '%s' "$salida" | grep -q 'Applied patch' || [ "$antes" = "$despues" ]; then
        echo "FALLO: el parche $p no cambió ${ARCH[$p]} ($salida)"; exit 1
      fi
      echo "ok  parche $p -> ${ARCH[$p]}"
    done ;;
  python)
    python -I "$H/aplicar_v2.py" "$W/src"
    python -I "$H/aplicar_fase6.py" "$W/src"
    python -I "$H/aplicar_cierre_tecnico.py" "$W/src"
    ARCHIVOS="lib/insecurity.ts models/user.ts routes/login.ts routes/changePassword.ts routes/2fa.ts server.ts routes/search.ts routes/userProfile.ts routes/basket.ts package.json lib/utils.ts lib/xml.ts routes/showProductReviews.ts routes/trackOrder.ts routes/updateProductReviews.ts routes/profileImageUrlUpload.ts routes/recycles.ts frontend/src/app/search-result/search-result.component.ts routes/b2bOrder.ts routes/chat.ts models/index.ts"
    GEN=/tmp/correcciones-regenerado.patch
    : > "$GEN"
    for f in $ARCHIVOS; do
      diff -u --label "a/$f" --label "b/$f" "$W/orig/$f" "$W/src/$f" >> "$GEN" || true
    done
    sed -i "s#^-const privateKey = '-----BEGIN RSA PRIVATE KEY-----.*#-const privateKey = '[REDACTADO: clave privada de prueba de Juice Shop; no se versiona]'#" "$GEN"
    CAMBIADOS="$( { diff -rq "$W/orig" "$W/src" || true; } | wc -l)"
    if cmp -s "$GEN" "$H/correcciones-cierre-tecnico.patch" && [ "$CAMBIADOS" = 21 ]; then
      sha256sum "$GEN" | cut -c1-64 > "$W/FUENTE_DIFF_SHA256"
      echo "ok  fuente = diff auditado (sha256 $(cat "$W/FUENTE_DIFF_SHA256")), 21 archivos; variante corregida-cierre-tecnico"
    else
      echo "FALLO: la fuente no coincide con el diff auditado ($CAMBIADOS archivos distintos)"; diff "$GEN" "$H/correcciones-cierre-tecnico.patch" | head -20; exit 1
    fi ;;
  *) echo "uso: preparar-fuente.sh git|python"; exit 2 ;;
esac
