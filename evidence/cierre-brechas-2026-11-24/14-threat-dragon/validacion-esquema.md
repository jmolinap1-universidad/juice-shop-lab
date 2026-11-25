# Validación del modelo de Threat Dragon

Modelo: `/r/docs/fase-1/threat-dragon/juice-shop-lab.json` · esquema: `/r/security/threat-dragon/threat-dragon-v2.schema.json` · jsonschema 4.23.0

| Comprobación | Resultado | Detalle |
|---|---|---|
| Esquema oficial threat-dragon-v2 (Draft7Validator) | OK | 0 errores |
| Identificadores de celda únicos | OK | 65 celdas |
| Flujos conectados a actores, procesos o almacenes del mismo diagrama | OK |  |
| Tipos STRIDE, estados y severidades admitidos por Threat Dragon | OK |  |
| hasOpenThreats coherente con el estado de las amenazas | OK |  |
| Números de amenaza únicos 1..threatTop | OK | threatTop=42 |
| Amenazas T01-T20 y TC01-TC10 presentes | OK | 30/30 |
| Cobertura STRIDE 6/6 | OK | 6/6 |

**Resultado: 8 OK · 0 fallos.** Amenazas: 42 (15 abiertas, 27 mitigadas).

Control del validador — demo oficial de Threat Dragon (`v2-threat-model.json`, v2.6.2): 11 errores de esquema (p. ej. `detail/diagrams/0/cells/4/attrs/body/strokeDasharray: None is not of type 'string'`).
