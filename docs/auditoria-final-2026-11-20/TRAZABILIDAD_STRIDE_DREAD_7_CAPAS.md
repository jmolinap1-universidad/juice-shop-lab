# Trazabilidad STRIDE · DREAD · casos A1-A12 · riesgos R01-R24 · siete capas

> Generado por `datos/generar_trazabilidad.py` desde `datos/trazabilidad.json`, el registro de riesgos de la Fase 6 y la
> evidencia de cada escenario. No modifica las matrices históricas (`docs/fase-1/`, `docs/fase-6/matriz-riesgo.md`).

## 1. Cobertura STRIDE (20 amenazas de la Fase 1)
| Clase | Amenazas | N.º |
|---|---|---|
| S · Suplantación | T01, T03, T04, T15, T16 | 5 |
| T · Manipulación | T06, T08, T13, T20 | 4 |
| R · Repudio | T19 | 1 |
| I · Divulgación de información | T02, T05, T06, T10, T11, T12, T13, T14, T17 | 9 |
| D · Denegación de servicio | T18 | 1 |
| E · Elevación de privilegios | T01, T07, T09, T11 | 4 |

Las seis clases STRIDE tienen al menos una amenaza. Repudio (T19) y Denegación de servicio (T18) tienen una sola: es una limitación del modelo, no un riesgo nulo.

## 2. Amenazas con DREAD (1-10) y riesgo vinculado
Orden D, R, E, A, Di (Daño, Reproducibilidad, Explotabilidad, Afectados, Descubribilidad); nivel por el promedio: ≥8 Crítico, 6-7.9 Alto, 4-5.9 Medio, <4 Bajo.

| Amenaza | Elemento DFD | STRIDE | Riesgo | D | R | E | A | Di | Promedio | Nivel |
|---|---|---|---|---|---|---|---|---|---|---|
| T01 | Login | S, E | R01 Inyección SQL en el login (bypass de autenticación) | 10 | 10 | 9 | 10 | 9 | 9.6 | Crítico |
| T02 | Búsqueda | I | R02 Inyección SQL UNION en búsqueda (extracción de tablas) | 10 | 10 | 7 | 10 | 8 | 9.0 | Crítico |
| T03 | Autenticación (JWT) | S | R03 Clave privada JWT embebida en el código (forja de tokens) | 10 | 10 | 6 | 10 | 7 | 8.6 | Crítico |
| T04 | Autenticación (bibliotecas) | S | R04 Bibliotecas JWT obsoletas (algoritmos débiles) | 9 | 7 | 5 | 10 | 5 | 7.2 | Alto |
| T05 | SQL Users | I | R05 Contraseñas con MD5 sin sal | 8 | 10 | 6 | 10 | 5 | 7.8 | Alto |
| T06 | API REST automática | I, T | R06 BOLA/IDOR: lectura de recursos de otro usuario | 7 | 10 | 8 | 8 | 8 | 8.2 | Crítico |
| T07 | API /api/Users | E | R07 Asignación masiva de role=admin en el registro | 8 | 10 | 7 | 5 | 6 | 7.2 | Alto |
| T08 | Reseñas (MarsDB) | T | R08 Inyección NoSQL en reseñas (MarsDB) | 5 | 9 | 6 | 8 | 5 | 6.6 | Alto |
| T09 | B2B / perfil / captcha | E | R09 Ejecución de código vía eval()/vm | 10 | 8 | 5 | 10 | 5 | 7.6 | Alto |
| T10 | Carga XML | I | R10 XXE en la carga de XML | 8 | 8 | 5 | 10 | 5 | 7.2 | Alto |
| T11 | Imagen por URL | I, E | R11 SSRF en la imagen de perfil por URL | 7 | 8 | 6 | 5 | 5 | 6.2 | Alto |
| T12 | Estáticos | I | R12 Listado de directorios y archivos internos (/ftp, /support/logs, /encryptionkeys) | 6 | 10 | 10 | 10 | 9 | 9.0 | Crítico |
| T13 | Frontend | T, I | R13 XSS (CSP débil, sin codificación de salida) | 6 | 9 | 7 | 7 | 8 | 7.4 | Alto |
| T14 | API (CORS) | I | R14 CORS permisivo (ACAO *) | 4 | 9 | 6 | 6 | 8 | 6.6 | Alto |
| T15 | Redirección | S | R15 Redirección abierta (lista blanca evadible) | 4 | 9 | 7 | 5 | 6 | 6.2 | Alto |
| T16 | Login / reset | S | R16 Fuerza bruta en el login (sin limitación de intentos) | 6 | 9 | 8 | 5 | 8 | 7.2 | Alto |
| T17 | Métricas | I | R17 /metrics expuesto sin autenticación | 3 | 10 | 10 | 2 | 7 | 6.4 | Alto |
| T18 | Proceso Node | D | R18 Denegación de servicio por vm/ZIP (agotamiento de recursos) | 5 | 6 | 5 | 10 | 4 | 6.0 | Alto |
| T19 | Registro | R | R19 Registro sin centralización ni alertas | 5 | 8 | 4 | 10 | 4 | 6.2 | Alto |
| T20 | Cadena de suministro | T | R20 Dependencias con CVE críticas (cadena de suministro) | 8 | 6 | 5 | 10 | 8 | 7.4 | Alto |

## 3. Casos de prueba A1-A12: clase, DREAD heredado y resultado por escenario
Clases: **E** Explotación demostrada · **X** Exposición observada · **C** Configuración insegura · **N** Ausencia de control · **I** Informativo (sin vulnerabilidad).

| Caso | Prueba | Clase | Amenaza | DREAD | Vulnerable | Vulnerable + WAF/RASP | Corregida sin WAF | Corregida + RASP sin WAF | Corregida + WAF/RASP |
|---|---|---|---|---|---|---|---|---|---|
| A1 | SQLi en el login (bypass de autenticación) | E | T01 | 9.6 (Crítico) | VULNERABLE | MITIGADO | MITIGADO | MITIGADO | MITIGADO |
| A2 | SQLi UNION en búsqueda (volcado de Users) | E | T02 | 9.0 (Crítico) | VULNERABLE | MITIGADO | MITIGADO | MITIGADO | MITIGADO |
| A3 | SQLi: enumeración del esquema | E | T02 | 9.0 (Crítico) | VULNERABLE | MITIGADO | MITIGADO | MITIGADO | MITIGADO |
| A4 | Listado de directorios | X | T12 | 9.0 (Crítico) | VULNERABLE | MITIGADO | VULNERABLE | VULNERABLE | MITIGADO |
| A5 | Exposición de documento interno (/ftp) | X | T12 | 9.0 (Crítico) | VULNERABLE | MITIGADO | VULNERABLE | VULNERABLE | MITIGADO |
| A6 | /metrics sin autenticación | X | T17 | 6.4 (Alto) | VULNERABLE | MITIGADO | VULNERABLE | VULNERABLE | MITIGADO |
| A7 | Asignación masiva (role=admin) | E | T07 | 7.2 (Alto) | VULNERABLE | MITIGADO | MITIGADO | MITIGADO | MITIGADO |
| A8 | CORS permisivo | C | T14 | 6.6 (Alto) | VULNERABLE | MITIGADO | MITIGADO | MITIGADO | MITIGADO |
| A9 | Cabeceras de seguridad ausentes | C | T13 | 7.4 (Alto) | VULNERABLE | MITIGADO | VULNERABLE | VULNERABLE | MITIGADO |
| A10 | Fuerza bruta sin límite de intentos | N | T16 | 7.2 (Alto) | VULNERABLE | MITIGADO | VULNERABLE | VULNERABLE | MITIGADO |
| A11 | Clave PÚBLICA JWT servida | I | — | No aplica | VULNERABLE | MITIGADO | VULNERABLE | VULNERABLE | MITIGADO |
| A12 | BOLA/IDOR entre dos cuentas | E | T06 | 8.2 (Crítico) | VULNERABLE | VULNERABLE | MITIGADO | MITIGADO | MITIGADO |

- **A11:** Informativo: servir una clave pública es aceptable por diseño. No hereda el DREAD de T03 (la clave PRIVADA embebida, hallazgo de caja blanca).
- El DREAD de un caso es el de su amenaza: el caso es la prueba que demuestra (o no) esa amenaza.
- «MITIGADO» solo se acepta con una respuesta HTTP válida en la petición principal; con 000, 5xx o timeout el caso queda «NO CONCLUYENTE».

Escenarios (evidencia):
- **Vulnerable:** `evidence/fase-6/validacion-2026-11-10/01-linea-base-vulnerable` — imagen oficial v20.3.0 sin controles (riesgo inherente).
- **Vulnerable + WAF/RASP:** `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem` — imagen oficial detrás de WAF + RASP + SIEM (Fase 6; el código sigue vulnerable).
- **Corregida sin WAF:** `evidence/cierre-2026-11-20/03-corregida-sin-waf` — variante con los parches 02, 05-08 y v2 (01, 03, 04, 09), sin WAF ni RASP: mide solo la corrección del código.
- **Corregida + RASP sin WAF:** `evidence/cierre-2026-11-20/05-corregida-rasp-sin-waf` — variante corregida con RASP, atacada dentro de la red Docker saltándose el WAF.
- **Corregida + WAF/RASP:** `evidence/cierre-2026-11-20/04-corregida-con-waf` — variante corregida con la defensa completa (WAF + RASP + SIEM), por 127.0.0.1:8088.

## 4. Riesgos R01-R24 por capa, con decisión y residual vigentes
| Riesgo | Capa principal | Capa secundaria | Origen | Decisión (estado) | Residual |
|---|---|---|---|---|---|
| R01 Inyección SQL en el login (bypass de autenticación) | 2a Aplicación · Código | 2d Aplicación · Perímetro de la aplicación | T01 / A1 | Mitigar (Ejecutado) | 2×5 Alto |
| R02 Inyección SQL UNION en búsqueda (extracción de tablas) | 2a Aplicación · Código | 1 Datos | T02 / A2-A3 | Mitigar (Ejecutado) | 2×5 Alto |
| R03 Clave privada JWT embebida en el código (forja de tokens) | 2c Aplicación · Implementación (dependencias, secretos, integración) | 1 Datos | T03 | Eliminar (Planificado) | 4×5 Crítico |
| R04 Bibliotecas JWT obsoletas (algoritmos débiles) | 2c Aplicación · Implementación (dependencias, secretos, integración) | 7 Políticas, procedimientos y concientización | T04 | Aceptar (Aceptado temporalmente) | 3×5 Alto |
| R05 Contraseñas con MD5 sin sal | 1 Datos | 2a Aplicación · Código | T05 | Eliminar (Planificado) | 3×5 Alto |
| R06 BOLA/IDOR: lectura de recursos de otro usuario | 2b Aplicación · Lógica de aplicación | 1 Datos | T06 / A12 | Eliminar (Planificado) | 5×4 Crítico |
| R07 Asignación masiva de role=admin en el registro | 2b Aplicación · Lógica de aplicación | 2d Aplicación · Perímetro de la aplicación | T07 / A7 | Mitigar (Ejecutado) | 2×4 Medio |
| R08 Inyección NoSQL en reseñas (MarsDB) | 2a Aplicación · Código | 1 Datos | T08 | Eliminar (Planificado) | 4×4 Alto |
| R09 Ejecución de código vía eval()/vm | 2a Aplicación · Código | 3 Host / contenedor | T09 | Eliminar (Planificado) | 3×4 Alto |
| R10 XXE en la carga de XML | 2a Aplicación · Código | 3 Host / contenedor | T10 | Eliminar (Planificado) | 3×5 Alto |
| R11 SSRF en la imagen de perfil por URL | 2b Aplicación · Lógica de aplicación | 4 Red interna | T11 | Mitigar (Planificado) | 4×3 Alto |
| R12 Listado de directorios y archivos internos (/ftp, /support/logs, /encryptionkeys) | 2d Aplicación · Perímetro de la aplicación | 1 Datos | T12 / A4-A5 | Mitigar (Ejecutado) | 3×4 Alto |
| R13 XSS (CSP débil, sin codificación de salida) | 2a Aplicación · Código | 2d Aplicación · Perímetro de la aplicación | T13 | Mitigar (Ejecutado parcialmente) | 4×4 Alto |
| R14 CORS permisivo (ACAO *) | 2d Aplicación · Perímetro de la aplicación | 2c Aplicación · Implementación (dependencias, secretos, integración) | T14 / A8 | Mitigar (Ejecutado) | 2×3 Medio |
| R15 Redirección abierta (lista blanca evadible) | 2b Aplicación · Lógica de aplicación | — | T15 | Eliminar (Planificado) | 4×3 Alto |
| R16 Fuerza bruta en el login (sin limitación de intentos) | 2d Aplicación · Perímetro de la aplicación | 2b Aplicación · Lógica de aplicación | T16 / A10 | Mitigar (Ejecutado) | 3×3 Medio |
| R17 /metrics expuesto sin autenticación | 2d Aplicación · Perímetro de la aplicación | 3 Host / contenedor | T17 / A6 | Mitigar (Ejecutado) | 3×2 Medio |
| R18 Denegación de servicio por vm/ZIP (agotamiento de recursos) | 3 Host / contenedor | 2a Aplicación · Código | T18 | Mitigar (Ejecutado parcialmente) | 3×4 Alto |
| R19 Registro sin centralización ni alertas | 7 Políticas, procedimientos y concientización | 3 Host / contenedor | T19 | Mitigar (Ejecutado parcialmente) | 2×4 Medio |
| R20 Dependencias con CVE críticas (cadena de suministro) | 2c Aplicación · Implementación (dependencias, secretos, integración) | 7 Políticas, procedimientos y concientización | T20 | Aceptar (Aceptado temporalmente) | 4×5 Crítico |
| R21 Configuración insegura al desplegar la arquitectura cloud (AWS) | 5 Perímetro cloud / red | 7 Políticas, procedimientos y concientización | Fase 2 | Evitar (Ejecutado) | 1×4 Bajo |
| R22 Bloqueo del RASP que deja peticiones colgadas o termina el proceso (auto-DoS) | 2c Aplicación · Implementación (dependencias, secretos, integración) | 3 Host / contenedor | Hallazgo Fase 6 | Eliminar (Ejecutado parcialmente) | 2×3 Medio |
| R23 Exposición de datos personales (incumplimiento de protección de datos) | 7 Políticas, procedimientos y concientización | 1 Datos | R01, R02, R06 | Mitigar (Ejecutado parcialmente) | 4×5 Crítico |
| R24 SIEM del laboratorio: privilegio sobre Docker, un solo nodo, Loki sin autenticación | 3 Host / contenedor | 4 Red interna | Riesgo introducido por la Fase 6 | Mitigar (Ejecutado) | 2×3 Medio |

## 5. Las siete capas: riesgos y controles con evidencia
| Capa | Riesgos | Controles probados (evidencia en el registro de riesgos) |
|---|---|---|
| 1 Datos | R02, R03, R05, R06, R08, R12, R23 | Alerta SIEM Acceso_Rutas_Sensibles_Denegado; Alertas SIEM de inyección (WAF y RASP); Bloqueo de la extracción masiva por SQLi (WAF + RASP); Bloqueo de la vía de extracción por SQLi (WAF + RASP); Heurística SIEM API_Enumeracion_Objetos_PosibleBOLA (con falsos positivos demostrados); RASP Aikido Zen + rasp-guard: bloqueo en sqlite3.all (query.q) con HTTP 403 … |
| 2a Aplicación · Código | R01, R02, R05, R08, R09, R10, R13, R18 | Alertas SIEM WAF_InyeccionSQL_Bloqueada y RASP_Ataque_Detectado; Alertas SIEM de inyección (WAF y RASP); Bloqueo de la vía de extracción por SQLi (WAF + RASP); Contención: FS raíz de solo lectura (escritura bloqueada con EROFS), usuario no root, cap_drop ALL; RASP Aikido Zen + integración rasp-guard: bloqueo en sqlite3.all con HTTP 403; RASP Aikido Zen + rasp-guard: bloqueo en sqlite3.all (query.q) con HTTP 403 … |
| 2b Aplicación · Lógica de aplicación | R06, R07, R11, R15, R16 | Alerta SIEM Login_FuerzaBruta_RateLimit; Alerta SIEM WAF_ParcheVirtual_Activado; Heurística SIEM API_Enumeracion_Objetos_PosibleBOLA (con falsos positivos demostrados); Parche virtual ModSecurity 100001 (HTTP 403); Rate limiting nginx 5/min por IP, ráfaga 3 (HTTP 429) |
| 2c Aplicación · Implementación (dependencias, secretos, integración) | R03, R04, R14, R20, R22 | Integración rasp-guard: el bloqueo en sqlite3 se entrega como error controlado HTTP 403 (sin --unhandled-rejections=warn); SCA en CI (npm audit, OSV, Grype) que identifica el componente; SCA en CI (npm audit, OSV, Grype, Trivy) en cada push; WAF oculta Access-Control-Allow-Origin (comprobado con Origin externo) |
| 2d Aplicación · Perímetro de la aplicación | R01, R07, R12, R13, R14, R16, R17 | Alerta SIEM Acceso_Rutas_Sensibles_Denegado; Alerta SIEM Login_FuerzaBruta_RateLimit; Alerta SIEM WAF_ParcheVirtual_Activado; Alertas SIEM WAF_InyeccionSQL_Bloqueada y RASP_Ataque_Detectado; Parche virtual ModSecurity 100001 (HTTP 403); RASP Aikido Zen + integración rasp-guard: bloqueo en sqlite3.all con HTTP 403 … |
| 3 Host / contenedor | R09, R10, R17, R18, R19, R22, R24 | Alerta SIEM Acceso_Rutas_Sensibles_Denegado; Contención: FS raíz de solo lectura (escritura bloqueada con EROFS), usuario no root, cap_drop ALL; Integración rasp-guard: el bloqueo en sqlite3 se entrega como error controlado HTTP 403 (sin --unhandled-rejections=warn); Proxy del socket de Docker de solo lectura (escrituras HTTP 403); Alloy sin root, sin socket, sin capacidades; SIEM: Alloy -> Loki -> Grafana; 3 fuentes ingestadas y 7 reglas (6 disparadas en las pruebas); nginx deny /metrics + parche virtual 100002 (mismo componente WAF) |
| 4 Red interna | R11, R24 | Proxy del socket de Docker de solo lectura (escrituras HTTP 403); Alloy sin root, sin socket, sin capacidades |
| 5 Perímetro cloud / red | R21 | No desplegar sin aprobación (sin terraform apply, sin .tfstate, sin credenciales AWS) |
| 6 Seguridad física | — | Ver nota |
| 7 Políticas, procedimientos y concientización | R04, R19, R20, R21, R23 | Bloqueo de la extracción masiva por SQLi (WAF + RASP); No desplegar sin aprobación (sin terraform apply, sin .tfstate, sin credenciales AWS); SCA en CI (npm audit, OSV, Grype) que identifica el componente; SCA en CI (npm audit, OSV, Grype, Trivy) en cada push; SIEM: Alloy -> Loki -> Grafana; 3 fuentes ingestadas y 7 reglas (6 disparadas en las pruebas) |

**Capa 6:** No hay riesgos registrados en la capa física: el laboratorio corre en una estación personal (HW-01) sin datos reales. Los controles físicos de un despliegue real (centro de datos del proveedor cloud) serían responsabilidad compartida y solo están en el DISEÑO de la Fase 2.
