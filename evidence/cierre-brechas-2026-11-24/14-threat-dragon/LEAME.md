# DFD en OWASP Threat Dragon — 2026-11-25

**Modelo:** `docs/fase-1/threat-dragon/juice-shop-lab.json` (Threat Dragon v2, dos diagramas STRIDE).
**Cómo se obtuvo:** `security/threat-dragon/generar_modelo_td.py` lo genera desde los datos versionados (amenazas T01-T20 y
DREAD de `docs/fase-1/fase1-modelado-amenazas.md`; TC01-TC10 de `trazabilidad.json`; estado según el residual vigente de
`riesgo-cierre-brechas`). Nada del modelo se escribió a mano: regenerar da el mismo archivo (UUID deterministas).
**Reproducir:** `make threat-dragon` (o `bash security/threat-dragon/ejecutar-threat-dragon.sh <carpeta>`).

| Archivo | Qué prueba | Resultado |
|---|---|---|
| `validacion-esquema.md` | Esquema oficial `threat-dragon-v2.schema.json` (tag v2.6.2) + coherencia propia | 8 OK · 0 fallos; 42 amenazas STRIDE (15 abiertas, 27 mitigadas), 30/30 amenazas, STRIDE 6/6 |
| `prueba-negativa.md` | Copia dañada (flujo a celda inexistente, T05 retirada, estado no admitido, sin `reviewer`) | Rechazada: 5 fallos detectados |
| `control-demo-oficial-v2-threat-model.json` | Demo oficial de Threat Dragon validada con el mismo esquema | 11 errores: el esquema declara `strokeDasharray` como texto y la demo usa `null` (palabra clave `nullable`, que el validador estándar no aplica). Nuestro modelo usa `""` y pasa sin excepciones |
| `threat-dragon-navegador.md` + `01..04-*.png` | Threat Dragon **v2.6.2 real** (imagen `owasp/threat-dragon@sha256:ec26312b…`, red interna, sesión local), importado por la interfaz en Chromium | 7 OK · 0 fallos: importa, dibuja 18+17 elementos y 16+14 flujos, el informe lista las 30 amenazas |
| `informe-texto.txt` | Texto del informe que genera Threat Dragon | Fuente de la comprobación 30/30 |

Elementos en rojo = con amenazas abiertas (residual Alto o control sin verificar, p. ej. TC10 por la MFA de las cuentas).
Una amenaza con varias letras STRIDE se divide en una por letra (Threat Dragon admite un tipo por amenaza): 30 amenazas → 42.
Avisos de consola excluidos y explicados en `threat-dragon-navegador.md` (directiva CSP del propio servidor; fuentes de
Google no resueltas porque la red no tiene salida). Revisión del equipo pendiente (`reviewer` lo declara).
