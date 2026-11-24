# Imagen CLOUD (DigitalOcean App Platform) — cierre técnico 2026-11-23.
# Un solo contenedor (plan de 512 MB): WAF nginx + ModSecurity 3 + OWASP CRS 4.25.2 delante de la VARIANTE CORREGIDA
# de Juice Shop (parches 01-13) con el RASP Aikido Zen. La plataforma la construye desde este repositorio:
#   - la fuente se reconstruye aquí desde el tag oficial fijado y se COMPRUEBA contra el diff auditado
#     (app-hardened/patches/v2/correcciones-cierre-tecnico.patch); si no coincide, la construcción falla.
#   - todas las imágenes base fijadas por digest; secretos solo en variables SECRET de la plataforma.
# Contexto de construcción: raíz del repositorio (ver .dockerignore: solo entra lo necesario).
# hadolint global ignore=DL3016

# ---- 1) Fuente oficial fijada + parches con git apply ----
FROM node:24-bookworm@sha256:9d266751ca3d7fdbe651c878ffd5ad0a42fed49a18c283509267c97f025b7496 AS fuente
COPY app-hardened/patches /h/patches
COPY deploy/cloud/preparar-fuente.sh /h/preparar-fuente.sh
RUN bash /h/preparar-fuente.sh git

# ---- 2) Parches 01/03/04/09-13 (reemplazos literales verificados) y comprobación contra el diff auditado ----
FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b AS parches
COPY --from=fuente /w /w
COPY app-hardened/aplicar_v2.py app-hardened/aplicar_fase6.py app-hardened/aplicar_cierre_tecnico.py /h/
COPY app-hardened/patches/v2/correcciones-cierre-tecnico.patch deploy/cloud/preparar-fuente.sh /h/
RUN bash /h/preparar-fuente.sh python

# ---- 3) Compilación (mismos pasos que app-hardened/Dockerfile) ----
FROM node:24-bookworm-slim@sha256:c86ecead9e55a5210ac1727de38a4ca840bf03dcaf34dc9749addbf383b1920c AS installer
COPY --from=parches /w/src /juice-shop
WORKDIR /juice-shop
ARG CYCLONEDX_NPM_VERSION='^4.0.0'
RUN npm install -g typescript@^6.0.3 @cyclonedx/cyclonedx-npm@"$CYCLONEDX_NPM_VERSION" && \
    npm install --omit=dev && \
    npm dedupe --omit=dev && \
    npm run sbom && \
    rm -rf frontend/node_modules frontend/.angular frontend/src/assets && \
    mkdir -p logs && \
    rm -f ftp/legal.md i18n/*.json && \
    rm -rf infrastructure && \
    find frontend/src -name '*.spec.ts' -delete

# ---- 4) Agente RASP (versión exacta, sin scripts de instalación) ----
FROM node:24-bookworm-slim@sha256:01d566e8d94d8c619591d78652babfccd3c6992a3dffa9ed5ab39e11cf6c70e9 AS rasp
WORKDIR /rasp
RUN npm init -y >/dev/null \
 && npm install --save-exact --omit=dev --ignore-scripts --no-audit --no-fund @aikidosec/firewall@1.8.46

# ---- 5) Runtime de Node (el mismo de la imagen distroless del artefacto local: Node 24.22.3) ----
FROM gcr.io/distroless/nodejs24-debian13@sha256:ba59ac9916b424cdfaaa8299695530251535843623a6d8f93d40b0a2ef69e390 AS node

# ---- 6) Imagen final: WAF oficial (Debian 13, usuario nginx) + Node + app ----
FROM owasp/modsecurity-crs@sha256:d69bfa07bbaeecd15f46188c2b624a4a365aeabf8c70b22e4aba32d72417d2d5
LABEL org.opencontainers.image.title="OWASP Juice Shop corregido + WAF + RASP (cloud)" \
      org.opencontainers.image.version="20.3.0-corregida-cierre-tecnico" \
      org.opencontainers.image.vendor="MASI-UMG-2026" \
      org.opencontainers.image.source="https://github.com/jmolinap1-universidad/juice-shop-lab" \
      masi.variante="corregida-cierre-tecnico+rasp+waf-cloud"
COPY --from=node /nodejs /nodejs
COPY --from=installer --chown=101:0 /juice-shop /juice-shop
COPY --from=rasp --chown=101:0 /rasp/node_modules/@aikidosec /juice-shop/node_modules/@aikidosec
COPY --from=parches /w/FUENTE_DIFF_SHA256 /w/APP_COMMIT /juice-shop/.masi/
COPY --chown=101:0 deploy/hardened/rasp/rasp-guard.js /juice-shop/rasp/rasp-guard.js
COPY deploy/cloud/default.conf.template /etc/nginx/templates/conf.d/default.conf.template
COPY deploy/cloud/acceso.html deploy/cloud/ok.txt /etc/nginx/
COPY deploy/hardened/waf/rules/99-virtual-patches.conf /etc/modsecurity.d/owasp-crs/rules/REQUEST-999-VIRTUAL-PATCHES.conf
COPY deploy/hardened/waf/rules/98-exclusiones-fase6.conf /etc/modsecurity.d/owasp-crs/rules/REQUEST-998-EXCLUSIONES-FASE6.conf
COPY --chmod=755 deploy/cloud/iniciar.sh /usr/local/bin/iniciar.sh
# WAF (mismos valores que deploy/hardened); audit log sin cabeceras ni cuerpos (partes A, F, H, Z): en la nube no hay
# Alloy que redacte tokens, cookies o contraseñas, así que no se registran.
# DL3064: falso positivo por el nombre SERVER_TOKENS (directiva server_tokens de nginx); aquí no hay secretos.
# hadolint ignore=DL3064
ENV BACKEND="http://127.0.0.1:3000" \
    MODSEC_RULE_ENGINE="On" \
    PARANOIA="1" \
    BLOCKING_PARANOIA="1" \
    ANOMALY_INBOUND="5" \
    ANOMALY_OUTBOUND="4" \
    ALLOWED_METHODS="GET HEAD POST OPTIONS PUT PATCH DELETE" \
    MODSEC_AUDIT_LOG="/dev/stdout" \
    MODSEC_AUDIT_LOG_FORMAT="JSON" \
    MODSEC_AUDIT_ENGINE="RelevantOnly" \
    MODSEC_AUDIT_LOG_PARTS="AFHZ" \
    SERVER_TOKENS="off" \
    NGINX_WORKER_PROCESSES="1" \
    REAL_IP_HEADER="do-connecting-ip" \
    SET_REAL_IP_FROM="0.0.0.0/0" \
    PORT="8080" \
    NODE_CONFIG='{"challenges":{"safetyMode":"enabled"}}' \
    NODE_OPTIONS="--max-old-space-size=256 --require @aikidosec/firewall --require /juice-shop/rasp/rasp-guard.js" \
    AIKIDO_BLOCK="true" \
    AIKIDO_DEBUG="true"
USER 101
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
    CMD ["curl", "-sf", "http://127.0.0.1:8080/healthz"]
ENTRYPOINT ["/usr/local/bin/iniciar.sh"]
CMD ["nginx", "-g", "daemon off;"]
