# Imagen de runtime endurecida que se CONSTRUYE y despliega en el laboratorio (Fase 5).
# Reutiliza la imagen oficial AUDITADA de Juice Shop fijada por digest (misma que escanea Trivy en la Fase 5)
# y añade solo metadatos de empaquetado y un HEALTHCHECK, sin reintroducir shell ni root.
# No modifica el código: las correcciones de dependencias y lógica son la Fase 6 (app-hardened).
FROM bkimminich/juice-shop:v20.3.0@sha256:cea5a4af4aacee498c491491af0408934ec81d004035c0a02ef3e54395e3bf27
LABEL org.opencontainers.image.title="OWASP Juice Shop (runtime endurecido)" \
      org.opencontainers.image.version="20.3.0-hardened" \
      org.opencontainers.image.vendor="MASI-UMG-2026" \
      org.opencontainers.image.source="https://github.com/jmolinap1-universidad/juice-shop-lab"
USER 65532
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD ["/nodejs/bin/node", "-e", "fetch('http://127.0.0.1:3000/rest/admin/application-version').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
