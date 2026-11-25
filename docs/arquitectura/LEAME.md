# Diagramas de arquitectura (fuentes)

`diagramas/*.mmd` son las fuentes Mermaid de los diagramas de arquitectura: stack local, despliegue real en Render, arquitectura
objetivo en AWS (diseño), flujo de una petición hasta PostgreSQL y pipeline DevSecOps. Son **diagramas elaborados** a partir de la
documentación, la IaC y la configuración del repositorio; no son capturas.

Las imágenes se generan sin red con Mermaid 10.9.1 en el contenedor de Playwright 1.49.1 (fijado por digest):
```bash
PW=mcr.microsoft.com/playwright@sha256:70e367e0cbf60340a5b5fd562f6247a34eb3196efab9f88a3dd56482d9fe09d2
docker run --rm -v informe-npm:/work $PW bash -c "cd /work && npm i --no-audit --no-fund playwright@1.49.1 mermaid@10.9.1"
docker run --rm --network none -v informe-npm:/work -v "$PWD/docs/arquitectura/diagramas:/d:ro" \
  -v "$PWD/evidence/fase-2/capturas/diagramas:/o" -v "$PWD/docs/arquitectura/render-mmd.js:/r.js:ro" $PW node /r.js
```
Salida vigente: `evidence/fase-2/capturas/diagramas/` (indexada en `evidence/fase-2/LEAME.md`).
