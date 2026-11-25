# Validación del modelo de Threat Dragon

Modelo: `/tmp/danado.json` · esquema: `/r/security/threat-dragon/threat-dragon-v2.schema.json` · jsonschema 4.23.0

| Comprobación | Resultado | Detalle |
|---|---|---|
| Esquema oficial threat-dragon-v2 (Draft7Validator) | **FALLO** | detail: 'reviewer' is a required property |
| Identificadores de celda únicos | OK | 65 celdas |
| Flujos conectados a actores, procesos o almacenes del mismo diagrama | **FALLO** | flujo 'HTTP(S) JSON/HTML': target no es un elemento del diagrama |
| Tipos STRIDE, estados y severidades admitidos por Threat Dragon | **FALLO** |  |
| hasOpenThreats coherente con el estado de las amenazas | OK |  |
| Números de amenaza únicos 1..threatTop | **FALLO** | threatTop=42 |
| Amenazas T01-T20 y TC01-TC10 presentes | **FALLO** | faltan: ['T05'] |
| Cobertura STRIDE 6/6 | OK | 6/6 |

**Resultado: 3 OK · 5 fallos.** Amenazas: 42 (15 abiertas, 27 mitigadas).
