Total: 90

| Severidad | Cantidad |
|---|---|
| WARNING | 62 |
| ERROR | 26 |
| MEDIUM | 2 | 

| Regla (CWE) | Cantidad |
|---|---|
| express-directory-listing (CWE-548) | 33 |
| github-actions-mutable-action-tag (CWE-1357) | 7 |
| express-sequelize-injection (CWE-89) | 6 |
| run-shell-injection (CWE-78) | 5 |
| sequelize-raw-query-template-literal (CWE-89) | 5 |
| aws-subnet-has-public-ip-address (CWE-1220) | 5 |
| insecure-load-balancer-tls-version (CWE-326) | 5 |
| node-eval-user-input (CWE-95) | 5 |
| express-check-directory-listing (CWE-548) | 5 |
| express-res-sendfile (CWE-73) | 4 |
| npm-missing-minimum-release-age (CWE-829) | 2 |
| weak-password-hash-md5 (CWE-916) | 2 |
| gha-curl-pipe-shell (CWE-78) | 1 |
| hardcoded-private-key (CWE-798) | 1 |
| hardcoded-jwt-secret (CWE-798) | 1 |
| express-open-redirect (CWE-601) | 1 |
| code-string-concat (CWE-95) | 1 |
| cors-wildcard (CWE-942) | 1 | 

| Regla | Archivo:línea |
|---|---|
| gha-curl-pipe-shell | app/.github/workflows/ci.yml:374 |
| run-shell-injection | app/.github/workflows/update-challenges-ebook.yml:22 |
| run-shell-injection | app/.github/workflows/update-challenges-www-legacy.yml:27 |
| run-shell-injection | app/.github/workflows/update-challenges-www-legacy.yml:36 |
| run-shell-injection | app/.github/workflows/update-challenges-www.yml:27 |
| run-shell-injection | app/.github/workflows/update-challenges-www.yml:36 |
| express-sequelize-injection | app/data/static/codefixes/dbSchemaChallenge_1.ts:5 |
| sequelize-raw-query-template-literal | app/data/static/codefixes/dbSchemaChallenge_3.ts:11 |
| express-sequelize-injection | app/data/static/codefixes/dbSchemaChallenge_3.ts:11 |
| sequelize-raw-query-template-literal | app/data/static/codefixes/unionSqlInjectionChallenge_1.ts:6 |
| express-sequelize-injection | app/data/static/codefixes/unionSqlInjectionChallenge_1.ts:6 |
| sequelize-raw-query-template-literal | app/data/static/codefixes/unionSqlInjectionChallenge_3.ts:10 |
| express-sequelize-injection | app/data/static/codefixes/unionSqlInjectionChallenge_3.ts:10 |
| hardcoded-private-key | app/lib/insecurity.ts:21 |
| weak-password-hash-md5 | app/lib/insecurity.ts:41 |
| node-eval-user-input | app/lib/xml.ts:38 |
| node-eval-user-input | app/routes/b2bOrder.ts:23 |
| node-eval-user-input | app/routes/captcha.ts:22 |
| node-eval-user-input | app/routes/fileUpload.ts:114 |
| sequelize-raw-query-template-literal | app/routes/login.ts:34 |
| express-sequelize-injection | app/routes/login.ts:34 |
| sequelize-raw-query-template-literal | app/routes/search.ts:23 |
| express-sequelize-injection | app/routes/search.ts:23 |
| code-string-concat | app/routes/userProfile.ts:65 |
| node-eval-user-input | app/routes/userProfile.ts:65 |
| weak-password-hash-md5 | app/scripts/package.mjs:121 |
