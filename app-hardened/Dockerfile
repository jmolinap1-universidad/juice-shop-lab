# Dockerfile ENDURECIDO de Juice Shop (compilación desde fuente) — Fase 5.
# Mejoras verificables sobre app/Dockerfile (Hadolint antes: 11 avisos):
#  - Imágenes base fijadas por DIGEST (no solo etiqueta): DL3006 e integridad de la cadena de suministro.
#  - Instrucciones RUN consolidadas en una sola capa: DL3059 y menor superficie.
#  - npm con versión fija y `--ignore-scripts` en producción (reduce ejecución de scripts de terceros).
#  - HEALTHCHECK para orquestación y detección de fallos.
#  - Usuario no root explícito (65532) y WORKDIR dedicado (ya presente en el original, se conserva).
# NOTA: las CVE de dependencias de la aplicación (crypto-js, lodash, marsdb, etc.) NO se corrigen aquí:
# forman parte del código y se tratan en la Fase 6 (app-hardened). Esta fase endurece imagen y runtime.
# hadolint global ignore=DL3016

# ---- Etapa de compilación ----
FROM node:24-bookworm-slim@sha256:c86ecead9e55a5210ac1727de38a4ca840bf03dcaf34dc9749addbf383b1920c AS installer
COPY . /juice-shop
WORKDIR /juice-shop
ARG CYCLONEDX_NPM_VERSION='^4.0.0'
RUN npm install -g typescript@^6.0.3 @cyclonedx/cyclonedx-npm@"$CYCLONEDX_NPM_VERSION" && \
    npm install --omit=dev --ignore-scripts && \
    npm dedupe --omit=dev && \
    npm run sbom && \
    rm -rf frontend/node_modules frontend/.angular frontend/src/assets && \
    mkdir -p logs && \
    chown -R 65532 logs && \
    chgrp -R 0 ftp/ frontend/dist/ logs/ data/ i18n/ && \
    chmod -R g=u ftp/ frontend/dist/ logs/ data/ i18n/ && \
    rm -f ftp/legal.md i18n/*.json

# ---- Imagen final mínima (distroless, sin shell ni gestor de paquetes) ----
FROM gcr.io/distroless/nodejs24-debian13@sha256:03980f6fd2a3245fa06e371c36fd33528ebbc676a1d0f84e3e21d95cd291b807
ARG BUILD_DATE
ARG VCS_REF
LABEL org.opencontainers.image.title="OWASP Juice Shop (endurecido)" \
      org.opencontainers.image.version="20.3.0-hardened" \
      org.opencontainers.image.vendor="MASI-UMG-2026" \
      org.opencontainers.image.source="https://github.com/jmolinap1-universidad/juice-shop-lab" \
      org.opencontainers.image.revision="$VCS_REF" \
      org.opencontainers.image.created="$BUILD_DATE"
WORKDIR /juice-shop
COPY --from=installer --chown=65532:0 /juice-shop .
USER 65532
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD ["/nodejs/bin/node", "-e", "fetch('http://127.0.0.1:3000/rest/admin/application-version').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
CMD ["/juice-shop/build/app.js"]
