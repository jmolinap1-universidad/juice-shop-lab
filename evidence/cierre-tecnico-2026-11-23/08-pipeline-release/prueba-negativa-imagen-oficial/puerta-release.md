# Puerta de release — 2026-11-23

Imagen: `sha256:cea5a4af4aacee498c491491af0408934ec81d004035c0a02ef3e54395e3bf27 <no value>`

| Control | Resultado |
|---|---|
| Gitleaks (historial) | 0 hallazgos |
| Hadolint | 0 avisos |
| Semgrep reglas propias | 12 ERROR (7 excepciones documentadas), 33 WARNING |
| Trivy | CRITICAL 10 · HIGH 33 · MEDIUM 80 · LOW 21 · secretos 5 |
| Grype (SBOM Syft, informativo) | {'Critical': 12, 'High': 59, 'Medium': 74, 'Negligible': 11, 'Low': 13} |

## Veredicto: **BLOQUEADA**

- Trivy: 5 secretos en la imagen
- Trivy CRITICAL sin excepción: CVE-2015-9235 jsonwebtoken (corrección: 4.2.2)
- Trivy HIGH sin excepción: CVE-2016-1000223 jws (corrección: >=3.0.0)
- Trivy HIGH sin excepción: CVE-2017-18214 moment (corrección: 2.19.3)
- Trivy HIGH sin excepción: CVE-2018-16487 lodash (corrección: >=4.17.11)
- Trivy CRITICAL sin excepción: CVE-2019-10744 lodash (corrección: 4.17.12)
- Trivy HIGH sin excepción: CVE-2020-15084 express-jwt (corrección: 6.0.0)
- Trivy HIGH sin excepción: CVE-2021-23337 lodash (corrección: 4.17.21)
- Trivy HIGH sin excepción: CVE-2022-23539 jsonwebtoken (corrección: 9.0.0)
- Trivy HIGH sin excepción: CVE-2022-24785 moment (corrección: 2.29.2)
- Trivy HIGH sin excepción: CVE-2022-25881 http-cache-semantics (corrección: 4.1.1)
- Trivy HIGH sin excepción: CVE-2022-25887 sanitize-html (corrección: 2.7.1)
- Trivy CRITICAL sin excepción: CVE-2023-46233 crypto-js (corrección: 4.2.0)
- Trivy HIGH sin excepción: CVE-2025-65945 jws (corrección: 3.2.3, 4.0.1)
- Trivy CRITICAL sin excepción: CVE-2026-101894 decompress (corrección: ninguna)
- Trivy HIGH sin excepción: CVE-2026-102990 basic-ftp (corrección: 6.2.1)
- Trivy CRITICAL sin excepción: CVE-2026-106445 handlebars (corrección: 4.7.10)
- Trivy CRITICAL sin excepción: CVE-2026-106446 handlebars (corrección: 4.7.10)
- Trivy HIGH sin excepción: CVE-2026-109383 undici (corrección: 6.29.1, 7.30.1, 8.12.2)
- Trivy HIGH sin excepción: CVE-2026-109869 undici (corrección: 6.29.1, 7.30.1, 8.12.2)
- Trivy HIGH sin excepción: CVE-2026-111181 body-parser (corrección: 2.4.0, 1.20.9)
- Trivy HIGH sin excepción: CVE-2026-113872 multer (corrección: 2.5.0)
- Trivy HIGH sin excepción: CVE-2026-118664 decode-uri-component (corrección: 0.5.1)
- Trivy HIGH sin excepción: CVE-2026-23745 tar (corrección: 7.5.3)
- Trivy HIGH sin excepción: CVE-2026-23950 tar (corrección: 7.5.4)
- Trivy HIGH sin excepción: CVE-2026-24842 tar (corrección: 7.5.7)
- Trivy HIGH sin excepción: CVE-2026-26960 tar (corrección: 7.5.8)
- Trivy HIGH sin excepción: CVE-2026-26996 minimatch (corrección: 10.2.1, 9.0.6, 8.0.5, 7.4.7, 6.2.1, 5.1.7, 4.2.4, 3.1.3)
- Trivy HIGH sin excepción: CVE-2026-27903 minimatch (corrección: 10.2.3, 9.0.7, 8.0.6, 7.4.8, 6.2.2, 5.1.8, 4.2.5, 3.1.3)
- Trivy HIGH sin excepción: CVE-2026-27904 minimatch (corrección: 10.2.3, 9.0.7, 8.0.6, 7.4.8, 6.2.2, 5.1.8, 4.2.5, 3.1.4)
- Trivy HIGH sin excepción: CVE-2026-29786 tar (corrección: 7.5.10)
- Trivy HIGH sin excepción: CVE-2026-31802 tar (corrección: 7.5.11)
- Trivy CRITICAL sin excepción: CVE-2026-53486 decompress (corrección: ninguna)
- Trivy CRITICAL sin excepción: CVE-2026-59873 tar (corrección: 7.5.19)
- Trivy HIGH sin excepción: CVE-2026-59874 tar (corrección: 7.5.18)
- Trivy CRITICAL sin excepción: CVE-2026-71851 crypto-js (corrección: 4.0.0)
- Trivy HIGH sin excepción: CVE-2026-73566 tar (corrección: 7.5.21)
- Trivy HIGH sin excepción: CVE-2026-85091 zlib1g (corrección: 1:1.3.dfsg+really1.3.1-1+deb13u1)
- Trivy HIGH sin excepción: CVE-2026-87018 undici (corrección: 6.29.1, 7.30.1, 8.12.2)
- Trivy HIGH sin excepción: NSWG-ECO-17 jsonwebtoken (corrección: >=4.2.2)
- Trivy HIGH sin excepción: NSWG-ECO-428 base64url (corrección: >=3.0.0)

## Excepciones vigentes aplicadas
- HIGH exceptuada: CVE-2026-107494 libssl3t64 — Sin corrección en Debian 13 para la imagen base distroless vigente. Revisar en c… (vence 2026-12-31)
- HIGH exceptuada: CVE-2026-124709 libssl3t64 — Sin corrección en Debian 13 para la imagen base distroless vigente. Revisar en c… (vence 2026-12-31)
- CRITICAL exceptuada: GHSA-5mrr-rgp6-x4gr marsdb — Sin versión corregida publicada. Almacén en memoria de reseñas y pedidos de Juic… (vence 2026-12-31)

APTA significa que el artefacto cumple esta política, no que esté libre de vulnerabilidades ni que pueda publicarse en Internet sin otros controles (ver criterio de publicación).
