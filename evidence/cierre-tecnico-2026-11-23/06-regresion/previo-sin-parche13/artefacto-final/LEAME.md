# Validación del artefacto — 2026-11-23T17:55:26-06:00
Contenedor juice-hardened · imagen sha256:574cef822c4831b2b49bf7e5b697b410a100c73c9e6958acb91448d185cbae5f · juice-corregida-rasp:local · variante corregida-cierre-tecnico+rasp · salud healthy · reinicios 0
Base juice-corregida:local sha256:680f4d88e0fa75c681988f3a9a788211517f7b8e69b4de1ef86331ff7794a3d0 · diff auditado 38c96706ac500e350759f1d18451204d75f6d95c3c4b8bdd834939a6e4b33859 · app f189f521266f42c6bd05884468292000cee852ed
Entorno: local (Docker Desktop), stack juice-corregida-defensa, WAF http://127.0.0.1:8088

| Batería | Sin WAF | Con WAF |
|---|---|---|
| Regresión funcional | Resultado: 15 OK, 0 FALLAS.  | Resultado: 15 OK, 0 FALLAS.  |
| Recorrido de la interfaz (35 llamadas) | Resultado: 35 OK, 0 BLOQUEOS DEL WAF (falsos positivos), 0 respuestas distintas de lo esperado.  | Resultado: 35 OK, 0 BLOQUEOS DEL WAF (falsos positivos), 0 respuestas distintas de lo esperado.  |
| BOLA en 5 tipos de objeto | Controles positivos: 7 OK, 0 FALLAS. (Si alguna fila anterior es VULNERABLE, B ya alteró o borró ese objeto y el contr | Controles positivos: 7 OK, 0 FALLAS. (Si alguna fila anterior es VULNERABLE, B ya alteró o borró ese objeto y el contr |
| Pruebas T1-T10 | Resultado parcial: 0 VULNERABLE, 9 PROTEGIDO, 2 pendientes de log o no concluyentes.  | Resultado parcial: 0 VULNERABLE, 9 PROTEGIDO, 2 pendientes de log o no concluyentes.  |
| A1-A12 (run.sh) | — | === 0 VULNERABLE / 11 MITIGADO de 11 casos (validar-artefacto) ===  |

Códigos HTTP del arnés con WAF:  4 200  2 201  1 400  7 403 
Estado final: salud healthy · reinicios 0
