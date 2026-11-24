# Validación del artefacto — 2026-11-23T19:02:12-06:00
Contenedor juice-hardened · imagen sha256:2ab64e96129d17cd50be04403e2070722eacd74c0aeaa3557a118e4c6e3fb3fd · juice-corregida-rasp:local · variante corregida-cierre-tecnico+rasp · salud healthy · reinicios 0
Base juice-corregida:local sha256:4a5b1079c5821b7316f84255f73b74c99c92c8a6d48ce1e8bbf2c984d1aaa3f0 · diff auditado 8cdc9fbb8bc60dbde9508817101d9509b43ba3ac6c8911a56d6fda934a1780ea · app f189f521266f42c6bd05884468292000cee852ed
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
