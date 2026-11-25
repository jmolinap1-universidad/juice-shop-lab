# Política de release en CI (GitHub Actions, `.github/workflows/release.yml`)

## Ejecución válida (artefacto final)
- **Run:** https://github.com/jmolinap1-universidad/juice-shop-lab/actions/runs/45555578891
- **Commit:** `84241b4` (rama `main`) · disparo: push · estado: **Success** · duración 9 min 26 s · 3 artefactos (informes completos)

| Job | Duración | Resultado | Detalle (resumen del job) |
|---|---|---|---|
| IaC de Render (render.yaml) | 19 s | success | 15 OK · 0 fallos |
| Puerta de release — imagen de la app | 5 min 24 s | success | `sha256:e01e8117…` corregida-cierre-brechas+rasp · Gitleaks 0 · Hadolint 0 · Semgrep 12 ERROR (7 exceptuados) · Trivy C1/H2 (exceptuados: marsdb, libssl ×2) · **APTA** |
| Puerta de release — imagen cloud (Render) | 9 min 7 s | success | `sha256:14e8a341…` corregida-cierre-brechas+rasp+waf-cloud-alpine · Gitleaks 0 · Hadolint 0 · Trivy C1/H0 (marsdb exceptuado) · **APTA** |

Grype (informativo, no decide): app {Critical 1, High 18}; cloud {Critical 1, High 15}.

## Ejecuciones anteriores (fallidas, conservadas como evidencia)
| Run | Commit | Resultado | Causa |
|---|---|---|---|
| https://github.com/jmolinap1-universidad/juice-shop-lab/actions/runs/45550623082 | `39c5bd5` | failure | (1) Imagen cloud **Debian**: 61 HIGH + 1 CRITICAL sin corrección → BLOQUEADA (real). (2) **Defecto de la puerta**: 8 «avisos» de Hadolint que eran los mensajes de descarga de Docker en la máquina limpia del runner; también bloqueaba la imagen de la app. Reproducido en local (8 → 0) y corregido en `84241b4` |
| https://github.com/jmolinap1-universidad/juice-shop-lab/actions/runs/45555354367 | `768d1da` | cancelada por el push siguiente (concurrencia) | — |

La imagen que construye el CI no es byte a byte la de Render (npm resuelve versiones en cada construcción, sin package-lock),
pero es la misma receta y la misma fuente verificada contra el diff auditado (`fc3f765c…`).
