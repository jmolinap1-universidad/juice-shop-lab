# Evidencias de la Fase 1 — Activos, amenazas y riesgo inherente

Índice actualizado el 2026-11-25. **Tipo:** *C* = captura real de una herramienta; *D* = tabla o gráfica generada desde datos
del repositorio (no es una captura); *S* = salida nativa de herramienta. Las rutas son relativas a la raíz del repositorio.
Muchas evidencias viven en los ciclos de cierre: se enlazan aquí en lugar de duplicarse.

| Requisito | Evidencia (ruta) | Tipo | Fecha · entorno · versión | Herramienta | Resultado e interpretación |
|---|---|---|---|---|---|
| Laboratorio aislado | `evidence/fase-1/lab-puertos.txt` | S | 2026-11-03 · local · Juice Shop v20.3.0 (digest `cea5a4af…`) | docker compose | Solo `127.0.0.1:3000`: el laboratorio vulnerable no se expone |
| Inventario ISO/IEC 27001 y CIA | `docs/auditoria-final-2026-11-20/INVENTARIO_ACTIVOS_ISO27001.csv` / `.md` (generados desde `datos/inventario.json`) | D | 2026-11-25 · local y Render | `generar_inventario.py` (validación de campos) | 42 activos con tipo, ubicación, estado, proceso, descripción, C-I-D, criticidad, propietario y custodio por rol |
| DFD en OWASP Threat Dragon (dos diagramas reales) | `evidence/fase-1/capturas/threat-dragon-2026-11-25/02-diagrama-0-lienzo.png`, `03-diagrama-1-lienzo.png` (y capturas completas de la herramienta) | C | 2026-11-25 · contenedor local sin red externa · Threat Dragon v2.6.2 (digest `ec26312b…`) | Threat Dragon + Chromium (Playwright 1.49.1), resolución ×2 | Modelo `docs/fase-1/threat-dragon/juice-shop-lab.json` abierto en la herramienta: 18 y 17 elementos, 16 y 14 flujos dibujados; informe 30/30 amenazas (`threat-dragon-navegador.md`) |
| Validación del modelo | `evidence/fase-1/capturas/threat-dragon-2026-11-25/validacion-esquema.md`, `prueba-negativa.md` | S | 2026-11-25 · local | jsonschema 4.23.0 + esquema oficial v2.6.2 | 8/8 comprobaciones; una copia dañada se rechaza (5 fallos detectados) |
| STRIDE (T01-T20) y DREAD | `docs/fase-1/fase1-modelado-amenazas.md` §4-5; `docs/auditoria-final-2026-11-20/TRAZABILIDAD_STRIDE_DREAD_7_CAPAS.md` §1-2 | D | 2026-11-03 (a priori, desde el código) | Revisión de código (`app/` en `f189f5212`) | 20 amenazas, 6/6 clases STRIDE; 5 críticas y 15 altas por DREAD |
| Amenazas de la nube real (TC01-TC10) | `TRAZABILIDAD_STRIDE_DREAD_7_CAPAS.md` §6; `datos/trazabilidad.json` | D | 2026-11-24 · Render (commit `768d1da`) | Valoración del equipo | 10 amenazas, 6/6 clases; 8 altas y 2 medias |
| Siete capas (con subcapas 2a-2d) | `docs/fase-1/fase1-modelado-amenazas.md` §6 (inicial, escala 1-4); `TRAZABILIDAD_STRIDE_DREAD_7_CAPAS.md` §4-5 (vigente) | D | 2026-11-03 / 2026-11-25 | — | La capa 5 inicial no reflejaba la nube; la versión vigente incluye Render |
| Heatmap inherente | `docs/fase-6/riesgo-cierre-brechas/img/heatmap-antes.png` | D | 2026-11-25 | `riesgo.py` + matplotlib 3.9.2 | 8 críticos y 16 altos; gráfica generada desde `riesgos-calculados.json` |
| Validación de los datos de riesgo | `docs/fase-6/riesgo-cierre-brechas/validacion-consistencia.txt` | S | 2026-11-25 | `riesgo.py` | 382 comprobaciones, 0 fallas |

**Cifras que no deben confundirse:** 30 amenazas únicas con DREAD (T01-T20 y TC01-TC10) se convierten en 42 registros de amenaza en
Threat Dragon, porque una amenaza con varias letras STRIDE se registra una vez por letra. Los 24 riesgos (R01-R24) agrupan esas
amenazas y otros hallazgos; no equivalen a CVE.
