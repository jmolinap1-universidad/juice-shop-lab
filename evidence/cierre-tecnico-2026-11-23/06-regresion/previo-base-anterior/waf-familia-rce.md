# WAF: familia RCE (CRS 932) con cadenas de prueba inocuas — 2026-11-23T17:42:11-06:00
| Petición | HTTP |
|---|---|
| GET /rest/products/search?q=;cat /etc/passwd | 403 |
| GET /rest/products/search?q=$(id) | 403 |
| GET /rest/products/search?q=apple (control) | 200 |

Reglas 932xxx registradas:  1 "ruleId":"932130"  1 "ruleId":"932160" 
