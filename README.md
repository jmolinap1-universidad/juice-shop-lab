# Laboratorio AppSec – OWASP Juice Shop

Proyecto final del curso **Seguridad en Aplicaciones** (Maestría en Seguridad Informática, UMG, 2026).

Equipo: Molina Pérez Juan Carlos · Sánchez Flores Juan Walter Ernesto · García Gonzalez Leopoldo Emanuel ·
Cambara Castillo Vanessa Odeth. Catedrático: Matthew Alexander Seigne Samayoa.

> ⚠️ `app/` es **OWASP Juice Shop v20.3.0**, una aplicación **intencionalmente vulnerable**. Solo se ejecuta en
> `127.0.0.1` o dentro del job efímero de GitHub Actions. No la exponga a Internet.

## Uso rápido
```bash
git clone --recurse-submodules https://github.com/jmolinap1-universidad/juice-shop-lab.git
make lab-up        # laboratorio vulnerable en http://127.0.0.1:3000
make scan          # SAST/SCA/contenedores/IaC locales vía Docker → evidence/
make attack        # casos de ataque automatizados (Fase 4) → evidence/fase-4/run-<fecha>/
make corregida-build      # Fase 6 VIGENTE: construye y verifica la variante corregida (parches 01-13)
make ops-corregido-up     # Fase 6 VIGENTE: corregida + WAF + RASP + SIEM (WAF_PORT=8088 si el 8080 está ocupado)
make ops-corregido-ps     #   estado, salud y variante;  make ops-corregido-down (no borra volúmenes)
make risk-vigente         # Fase 6 VIGENTE: registro de riesgos, heatmaps y tabla en docs/fase-6/riesgo-vigente/
make ops-up / make risk   # Fase 6 HISTÓRICO (2026-11-10): imagen OFICIAL vulnerable + defensa; residual v2
make release              # Cierre técnico: pipeline de release con puerta (falla si no cumple la política)
make validar-artefacto    # Cierre técnico: regresión funcional y de seguridad del artefacto, sin WAF y con WAF
make risk-cierre-tecnico  # Cierre técnico: registro de riesgos del artefacto final (0 críticos, 8 altos)
make lab-down
```
En Windows sin `make`: ejecutar los scripts equivalentes desde Git Bash (ver `docs/fase-6/GUIA_DEMOSTRACION_FASE6.md`).
**Estado técnico vigente (2026-11-24):** `docs/cierre-tecnico/ESTADO_TECNICO_CIERRE.md`. **Despliegue cloud real:** Render, capa
gratuita, acceso restringido — `docs/cierre-tecnico/DESPLIEGUE_CLOUD_RENDER.md` (Blueprint `render.yaml`, imagen `deploy/cloud/`).
Plan original de Seenode: `docs/cierre-tecnico/PLAN_DESPLIEGUE_SEENODE.md`.

Ver `CLAUDE.md` (reglas), `PROGRESO.md`, `DECISIONES.md` y `docs/` (entregables por fase).

**Fase 6 — análisis vigente (cierre 2026-11-21):** `docs/fase-6/CIERRE_FINAL_FASE6.md` (dictamen 6.1/6.2),
`docs/fase-6/GUIA_DEMOSTRACION_FASE6.md` (demo en vivo), `docs/fase-6/MATRIZ_VALIDACION_FINAL.md`,
`docs/fase-6/riesgo-vigente/tratamiento-riesgo-vigente.md` (24 riesgos: 1 crítico, 11 altos, 9 medios, 3 bajos) y
`docs/fase-6/PLAN_PENDIENTES_POST_CIERRE.md`. **Histórico:** `CIERRE_Y_VALIDACION_FASE6.md` y `tratamiento-riesgo.md`
(2026-11-10, imagen oficial: 4/12/7/1), `matriz-riesgo.md`.
