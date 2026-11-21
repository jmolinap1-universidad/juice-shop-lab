# Trivy 0.75.0 — imagen HISTÓRICA en ejecución (oficial + RASP) vs. VIGENTE (corregida + RASP), misma base de datos

| Métrica | Histórica juice-hardened-rasp | Variante corregida |
|---|---|---|
| Imagen | juice-hardened-rasp:local | juice-corregida-rasp:local |
| SO base | 13.7 | 13.7 |
| Vulnerabilidades únicas | 150 | 135 |
| CRITICAL | 11 | 9 |
| HIGH | 33 | 27 |
| MEDIUM | 85 | 79 |
| LOW | 16 | 16 |
| UNKNOWN | 5 | 4 |
| Origen Node.js | 81 | 67 |
| Origen SO | 69 | 68 |
| Secretos detectados | 5 | 0 |

## Secretos — oficial
- /juice-shop/build/lib/insecurity.js: private-key (HIGH)
- /juice-shop/frontend/src/app/app.guard.spec.ts: jwt-token (MEDIUM)
- /juice-shop/frontend/src/app/last-login-ip/last-login-ip.component.spec.ts: jwt-token (MEDIUM)
- /juice-shop/infrastructure/terraform/networking.tf: private-key (HIGH)
- /juice-shop/lib/insecurity.ts: private-key (HIGH)

## Secretos — corregida
- (ninguno)

## CRITICAL restantes en la variante corregida
- CVE-2023-46233 crypto-js 3.3.0 → 4.2.0
- CVE-2026-71851 crypto-js 3.3.0 → 4.0.0
- CVE-2026-101894 decompress 4.2.1 → sin corrección
- CVE-2026-53486 decompress 4.2.1 → sin corrección
- CVE-2015-9235 jsonwebtoken 0.1.0 → 4.2.2
- CVE-2019-10744 lodash 2.4.2 → 4.17.12
- GHSA-5mrr-rgp6-x4gr marsdb 0.6.11 → sin corrección
- CVE-2026-59873 tar 6.2.1 → 7.5.19

## Nota de validación sobre los secretos (no se acepta el 0)
El escaneo de `juice-corregida-rasp:local` informó 0 secretos, pero los archivos siguen en la imagen (comprobado con
`docker cp`: `frontend/src/app/app.guard.spec.ts`, `infrastructure/terraform/networking.tf`), y el escaneo de la imagen base
`juice-corregida:local` (mismas capas) informa **3** (`trivy-secretos-juice-corregida-base.json`). Cifra válida: **3 secretos**,
todos material de ejemplo o de prueba de Juice Shop (dos JWT en pruebas unitarias del frontend y una clave de ejemplo de
Terraform), **no** la clave de firma. La clave privada embebida (`lib/insecurity.ts` y `build/lib/insecurity.js`) sí desapareció:
los archivos existen, pero ya no contienen la clave (parche 04 v2). El 0 se trata como artefacto del escaneo.

Las 8 CRITICAL restantes están en dependencias de Juice Shop que no se actualizaron (ver `analisis-dependencias.md`).
