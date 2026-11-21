# Trivy 0.75.0 — imagen oficial vs. variante corregida (misma base de datos, mismo día)

| Métrica | Oficial v20.3.0 (reescaneo) | Variante corregida |
|---|---|---|
| Imagen | bkimminich/juice-shop:v20.3.0@sha256:cea5a4af4aacee498c49149 | juice-corregida:local |
| SO base | 13.7 | 13.7 |
| Vulnerabilidades únicas | 150 | 135 |
| CRITICAL | 11 | 9 |
| HIGH | 33 | 27 |
| MEDIUM | 85 | 79 |
| LOW | 16 | 16 |
| UNKNOWN | 5 | 4 |
| Origen Node.js | 81 | 67 |
| Origen SO | 69 | 68 |
| Secretos detectados | 5 | 3 |

## Secretos — oficial
- /juice-shop/build/lib/insecurity.js: private-key (HIGH)
- /juice-shop/frontend/src/app/app.guard.spec.ts: jwt-token (MEDIUM)
- /juice-shop/frontend/src/app/last-login-ip/last-login-ip.component.spec.ts: jwt-token (MEDIUM)
- /juice-shop/infrastructure/terraform/networking.tf: private-key (HIGH)
- /juice-shop/lib/insecurity.ts: private-key (HIGH)

## Secretos — corregida
- /juice-shop/frontend/src/app/app.guard.spec.ts: jwt-token (MEDIUM)
- /juice-shop/frontend/src/app/last-login-ip/last-login-ip.component.spec.ts: jwt-token (MEDIUM)
- /juice-shop/infrastructure/terraform/networking.tf: private-key (HIGH)

## CRITICAL restantes en la variante corregida
- CVE-2023-46233 crypto-js 3.3.0 → 4.2.0
- CVE-2026-71851 crypto-js 3.3.0 → 4.0.0
- CVE-2026-101894 decompress 4.2.1 → sin corrección
- CVE-2026-53486 decompress 4.2.1 → sin corrección
- CVE-2015-9235 jsonwebtoken 0.1.0 → 4.2.2
- CVE-2019-10744 lodash 2.4.2 → 4.17.12
- GHSA-5mrr-rgp6-x4gr marsdb 0.6.11 → sin corrección
- CVE-2026-59873 tar 6.2.1 → 7.5.19
