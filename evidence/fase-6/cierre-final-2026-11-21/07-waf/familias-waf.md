# Pruebas acotadas del WAF por familia — 2026-11-21T08:20:42-06:00 — objetivo http://127.0.0.1:8088 (stack vigente)
| Familia CRS | Petición (cadena de prueba inocua, sin efecto en la app) | HTTP |
|---|---|---|
| XSS (941) | GET /rest/products/search?q=<script>alert(1)</script> | 403 |
| XSS (941) en reseña | PUT /rest/products/1/reviews con <img src=x onerror=alert(1)> | 403 |
| LFI (930) | GET /rest/products/search?q=../../../../etc/passwd | 403 |
| SQLi (942) control | GET /rest/products/search?q=%27)) UNION SELECT 1-- | 403 |
| Control legítimo | GET /rest/products/search?q=apple | 200 |

Reglas registradas en el audit log durante estas peticiones:
          1 "ruleId":"930100"
          2 "ruleId":"930110"
          1 "ruleId":"930120"
          2 "ruleId":"941100"
          1 "ruleId":"941110"
          1 "ruleId":"941120"
          2 "ruleId":"941160"
          2 "ruleId":"941390"
          1 "ruleId":"942100"
          1 "ruleId":"942190"
          1 "ruleId":"942360"
