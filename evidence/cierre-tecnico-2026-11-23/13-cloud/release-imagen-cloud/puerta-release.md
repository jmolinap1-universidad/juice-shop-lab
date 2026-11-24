# Puerta de release — 2026-11-24

Imagen: `sha256:75b91b779076bf889156fbe2ece67dfe13adce2716124b777ebc70c1a524ff69 corregida-cierre-tecnico+rasp+waf-cloud`

| Control | Resultado |
|---|---|
| Gitleaks (historial) | 1 hallazgos |
| Hadolint | 0 avisos |
| Semgrep reglas propias | 12 ERROR (7 excepciones documentadas), 33 WARNING |
| Trivy | CRITICAL 2 · HIGH 76 · MEDIUM 146 · LOW 213 · secretos 0 |
| Grype (SBOM Syft, informativo) | {'Negligible': 119, 'High': 175, 'Critical': 27, 'Medium': 104, 'Low': 17, 'Unknown': 1} |

## Veredicto: **BLOQUEADA**

- Gitleaks: 1 secretos en el repositorio
- Trivy HIGH sin excepción: CVE-2025-69720 libtinfo6 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2025-69720 ncurses-base (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2025-69720 ncurses-bin (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-107494 openssl (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-107494 openssl-provider-legacy (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-113351 libexpat1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-115506 libexpat1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-117610 libexpat1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-118370 libexpat1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-119373 libsqlite3-0 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-119374 libsqlite3-0 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-119379 libsqlite3-0 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-12064 curl (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-12064 libcurl3t64-gnutls (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-12064 libcurl4t64 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-124709 openssl (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-124709 openssl-provider-legacy (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-16742 libsystemd0 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-16742 libudev1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-36849 libtiff6 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-52490 libtiff6 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-54369 libacl1 (corrección: ninguna)
- Trivy CRITICAL sin excepción: CVE-2026-6653 libxml2 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-74860 libxml2 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-76642 bsdutils (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-76642 libblkid1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-76642 liblastlog2-2 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-76642 libmount1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-76642 libsmartcols1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-76642 libuuid1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-76642 login (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-76642 mount (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-76642 util-linux (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78408 bsdutils (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78408 libblkid1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78408 liblastlog2-2 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78408 libmount1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78408 libsmartcols1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78408 libuuid1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78408 login (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78408 mount (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78408 util-linux (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78409 bsdutils (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78409 libblkid1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78409 liblastlog2-2 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78409 libmount1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78409 libsmartcols1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78409 libuuid1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78409 login (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78409 mount (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78409 util-linux (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78410 bsdutils (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78410 libblkid1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78410 liblastlog2-2 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78410 libmount1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78410 libsmartcols1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78410 libuuid1 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78410 login (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78410 mount (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-78410 util-linux (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-8458 curl (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-8458 libcurl3t64-gnutls (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-8458 libcurl4t64 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-86138 libxml2 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-86139 libxml2 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-86140 libxml2 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-86142 libxml2 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-86143 libxml2 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-86144 libxml2 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-88806 libx11-6 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-88806 libx11-data (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-9538 libperl5.40 (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-9538 perl (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-9538 perl-base (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-9538 perl-modules-5.40 (corrección: ninguna)

## Excepciones vigentes aplicadas
- HIGH exceptuada: CVE-2026-107494 libssl3t64 — Sin corrección en Debian 13 para la imagen base distroless vigente. Revisar en c… (vence 2026-12-31)
- HIGH exceptuada: CVE-2026-124709 libssl3t64 — Sin corrección en Debian 13 para la imagen base distroless vigente. Revisar en c… (vence 2026-12-31)
- CRITICAL exceptuada: GHSA-5mrr-rgp6-x4gr marsdb — Sin versión corregida publicada. Almacén en memoria de reseñas y pedidos de Juic… (vence 2026-12-31)

APTA significa que el artefacto cumple esta política, no que esté libre de vulnerabilidades ni que pueda publicarse en Internet sin otros controles (ver criterio de publicación).
