# Puerta de release — 2026-11-24

Imagen: `sha256:272c0dea15a753ed94532e457d0124ded63ea372ffc0a97f79274ea1df63b4ea corregida-cierre-brechas+rasp+waf-cloud-alpine`

| Control | Resultado |
|---|---|
| Gitleaks (historial) | 0 hallazgos |
| Hadolint | 0 avisos |
| Semgrep reglas propias | 12 ERROR (7 excepciones documentadas), 33 WARNING |
| Trivy | CRITICAL 1 · HIGH 0 · MEDIUM 6 · LOW 2 · secretos 0 |
| Grype (SBOM Syft, informativo) | {'Medium': 18, 'High': 15, 'Low': 1, 'Critical': 1} |

## Veredicto: **APTA según la política**

- Sin incumplimientos.

## Excepciones vigentes aplicadas
- CRITICAL exceptuada: GHSA-5mrr-rgp6-x4gr marsdb — Sin versión corregida publicada. Almacén en memoria de reseñas y pedidos de Juic… (vence 2026-12-31)

APTA significa que el artefacto cumple esta política, no que esté libre de vulnerabilidades ni que pueda publicarse en Internet sin otros controles (ver criterio de publicación).
