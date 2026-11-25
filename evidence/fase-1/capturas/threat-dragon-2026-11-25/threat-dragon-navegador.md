# Modelo abierto en OWASP Threat Dragon v2.6.2 (navegador real)

Instancia: `http://localhost:3000` (contenedor local, red interna) · Chromium/Playwright · modelo `juice-shop-lab.json`

| Prueba | Esperado | Obtenido | Resultado |
|---|---|---|---|
| Importación del JSON por la interfaz | se muestra el modelo con su título | http://localhost:3000/#/local/Laboratorio%20AppSec%20%E2%80%94%20OWASP%20Juice%20Shop%20(MASI-UMG%202026) | OK |
| Diagrama 0: «Aplicación — DFD de la Fase 1 (variante corregida)» — elementos y límites dibujados | 18 | 18 | OK |
| Diagrama 0: flujos de datos dibujados | 16 | 16 | OK |
| Diagrama 1: «Despliegue real — Render + PostgreSQL» — elementos y límites dibujados | 17 | 17 | OK |
| Diagrama 1: flujos de datos dibujados | 14 | 14 | OK |
| Informe de Threat Dragon: amenazas T01-T20 y TC01-TC10 | 30/30 | 30/30 | OK |
| Errores de JavaScript en la consola (sin contar recursos externos bloqueados por el aislamiento) | 0 | 0 | OK |

**Resultado: 7 OK · 0 fallos.**

Aviso excluido del recuento (1 veces, emitido por la cabecera CSP del servidor de Threat Dragon, no por el modelo): `Unrecognized Content-Security-Policy directive 'prefetch-src'`.

Recursos externos no resueltos (la red no tiene salida a Internet): fonts.googleapis.com.

Errores de consola:
- `Failed to load resource: net::ERR_NAME_NOT_RESOLVED`
