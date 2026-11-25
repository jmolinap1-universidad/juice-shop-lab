# Puerta de release — 2026-11-24

Imagen: `sha256:1849a86fc138e469809a4e42fac593fbf5db7b1498ae6375731be73340f9c1fb corregida-cierre-brechas+rasp`

| Control | Resultado |
|---|---|
| Gitleaks (historial) | 0 hallazgos |
| Hadolint | 0 avisos |
| Semgrep reglas propias | 12 ERROR (7 excepciones documentadas), 33 WARNING |
| Trivy | CRITICAL 1 · HIGH 2 · MEDIUM 40 · LOW 19 · secretos 0 |
| Grype (SBOM Syft, informativo) | {'Medium': 26, 'High': 18, 'Negligible': 11, 'Low': 7, 'Critical': 1} |

## Veredicto: **APTA según la política**

- Sin incumplimientos.

## Excepciones vigentes aplicadas
- HIGH exceptuada: CVE-2026-107494 libssl3t64 — Sin corrección en Debian 13 para la imagen base distroless vigente. Revisar en c… (vence 2026-12-31)
- HIGH exceptuada: CVE-2026-124709 libssl3t64 — Sin corrección en Debian 13 para la imagen base distroless vigente. Revisar en c… (vence 2026-12-31)
- CRITICAL exceptuada: GHSA-5mrr-rgp6-x4gr marsdb — Sin versión corregida publicada. Almacén en memoria de reseñas y pedidos de Juic… (vence 2026-12-31)

APTA significa que el artefacto cumple esta política, no que esté libre de vulnerabilidades ni que pueda publicarse en Internet sin otros controles (ver criterio de publicación).
