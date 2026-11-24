# ZAP baseline (pasivo) — variante final detrás del WAF — objetivo http://juice-waf:8080 (red interna)
ZAP 2.17.0 · generado Tue, 24 Nov 2026 01:35:23

| Riesgo | Alertas |
|---|---|
| High | 0 |
| Medium | 2 |
| Low | 2 |
| Informational | 3 |

| Plugin | Alerta | Riesgo | CWE | Instancias |
|---|---|---|---|---|
| 10055 | CSP: Failure to Define Directive with No Fallback | Medium (High) | 693 | 3 |
| 10055 | CSP: style-src unsafe-inline | Medium (High) | 693 | 3 |
| 90004 | Cross-Origin-Resource-Policy Header Missing or Invalid | Low (Medium) | 693 | 5 |
| 10110 | Dangerous JS Functions | Low (Low) | 749 | 1 |
| 10109 | Modern Web Application | Informational (Medium) | -1 | 2 |
| 10049 | Storable and Cacheable Content | Informational (Medium) | 524 | 1 |
| 10049 | Storable but Non-Cacheable Content | Informational (Medium) | 524 | 5 |

Comparación con la Fase 4 (imagen oficial, evidence/fase-4/zap/resumen-zap.md): 9 alertas (2 Medium: CSP ausente y CORS permisivo).
ZAP baseline es pasivo: no prueba inyecciones; estas se cubren con run.sh y pruebas-cierre-tecnico.sh.
