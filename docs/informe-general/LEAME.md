# Informe General – Opción B (UMG) — qué archivo es cuál

| Archivo | Contenido |
|---|---|
| `Informe_General_Opcion_B_UMG.docx` | Informe final editable (147 páginas): carátula institucional, resumen ejecutivo, índice automático, capítulos 1-6, anexos y referencias APA 7 |
| `Informe_General_Opcion_B_UMG.pdf` | PDF equivalente, exportado con Microsoft Word desde el mismo `.docx` |
| `MATRIZ_VERIFICACION_INFORME.md` | Matriz breve de verificación: criterio, sección y página, evidencia y estado (sin nota) |
| `img/` | Diagramas generados desde la documentación (`build/diagramas/*.mmd`) y recortes de las capturas de Threat Dragon |
| `build/` | Generador reproducible: fuentes del texto (`fuente/*.txt`), `gen.py`, `render-mmd.js`, `word-finalizar.ps1` |

Los informes parciales originales (`docs/fase-6/entregable/`, `docs/evidencias-fase4-5/`) no se modificaron.

## Regenerar
Desde Git Bash, en la raíz del repositorio (Docker Desktop y Microsoft Word instalados):
1. Diagramas: contenedor de Playwright 1.49.1 (fijado por digest) con `mermaid@10.9.1`, `node build/render-mmd.js` (sin red).
2. Word: `python:3.12-slim` (fijado por digest) con `python-docx==1.1.2` y `Pillow==10.4.0`:
   `python -I docs/informe-general/build/gen.py <repo> <carátula.docx> docs/informe-general/Informe_General_Opcion_B_UMG.docx docs/informe-general/build/fuente/*.txt`.
   La carátula es el documento institucional de la Fase 6 (`Fase 6 Operaciones, Monitoreo y Ciberseguridad.docx`, fuera del repositorio);
   el generador conserva su sección y solo cambia el título.
3. Índice y PDF: `powershell -File docs/informe-general/build/word-finalizar.ps1 <docx> <pdf>`.

Las tablas de inventario, amenazas, riesgos y controles se leen de los archivos de datos del repositorio (CSV y JSON validados);
no se transcriben a mano. El generador se detiene si una referencia cruzada no existe o si una clave de tabla o figura se repite.
