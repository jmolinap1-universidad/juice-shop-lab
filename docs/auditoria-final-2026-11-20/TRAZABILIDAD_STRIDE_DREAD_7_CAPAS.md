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

| Caso | Prueba | Clase | Amenaza | DREAD | Vulnerable | Vulnerable + WAF/RASP | Corregida sin WAF | Corregida + RASP sin WAF | Corregida + WAF/RASP | Imagen cloud final (local) | Render (despliegue real) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | SQLi en el login (bypass de autenticación) | E | T01 | 9.6 (Crítico) | VULNERABLE | MITIGADO | MITIGADO | MITIGADO | MITIGADO | MITIGADO | MITIGADO |
| A2 | SQLi UNION en búsqueda (volcado de Users) | E | T02 | 9.0 (Crítico) | VULNERABLE | MITIGADO | MITIGADO | MITIGADO | MITIGADO | MITIGADO | MITIGADO |
| A3 | SQLi: enumeración del esquema | E | T02 | 9.0 (Crítico) | VULNERABLE | MITIGADO | MITIGADO | MITIGADO | MITIGADO | MITIGADO | MITIGADO |
| A4 | Listado de directorios | X | T12 | 9.0 (Crítico) | VULNERABLE | MITIGADO | VULNERABLE | VULNERABLE | MITIGADO | MITIGADO | MITIGADO |
| A5 | Exposición de documento interno (/ftp) | X | T12 | 9.0 (Crítico) | VULNERABLE | MITIGADO | VULNERABLE | VULNERABLE | MITIGADO | MITIGADO | MITIGADO |
| A6 | /metrics sin autenticación | X | T17 | 6.4 (Alto) | VULNERABLE | MITIGADO | VULNERABLE | VULNERABLE | MITIGADO | MITIGADO | MITIGADO |
| A7 | Asignación masiva (role=admin) | E | T07 | 7.2 (Alto) | VULNERABLE | MITIGADO | MITIGADO | MITIGADO | MITIGADO | MITIGADO | MITIGADO |
| A8 | CORS permisivo | C | T14 | 6.6 (Alto) | VULNERABLE | MITIGADO | MITIGADO | MITIGADO | MITIGADO | MITIGADO | MITIGADO |
| A9 | Cabeceras de seguridad ausentes | C | T13 | 7.4 (Alto) | VULNERABLE | MITIGADO | VULNERABLE | VULNERABLE | MITIGADO | MITIGADO | MITIGADO |
| A10 | Fuerza bruta sin límite de intentos | N | T16 | 7.2 (Alto) | VULNERABLE | MITIGADO | VULNERABLE | VULNERABLE | MITIGADO | MITIGADO | MITIGADO |
| A11 | Clave PÚBLICA JWT servida | I | — | No aplica | VULNERABLE | MITIGADO | VULNERABLE | VULNERABLE | MITIGADO | MITIGADO | MITIGADO |
| A12 | BOLA/IDOR entre dos cuentas | E | T06 | 8.2 (Crítico) | VULNERABLE | VULNERABLE | MITIGADO | MITIGADO | MITIGADO | MITIGADO | MITIGADO |

- **A11:** Informativo: servir una clave pública es aceptable por diseño. No hereda el DREAD de T03 (la clave PRIVADA embebida, hallazgo de caja blanca).
- El DREAD de un caso es el de su amenaza: el caso es la prueba que demuestra (o no) esa amenaza.
- «MITIGADO» solo se acepta con una respuesta HTTP válida en la petición principal; con 000, 5xx o timeout el caso queda «NO CONCLUYENTE».

Escenarios (evidencia):
- **Vulnerable:** `evidence/fase-6/validacion-2026-11-10/01-linea-base-vulnerable` — imagen oficial v20.3.0 sin controles (riesgo inherente).
- **Vulnerable + WAF/RASP:** `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem` — imagen oficial detrás de WAF + RASP + SIEM (Fase 6; el código sigue vulnerable).
- **Corregida sin WAF:** `evidence/cierre-2026-11-20/03-corregida-sin-waf` — variante con los parches 02, 05-08 y v2 (01, 03, 04, 09), sin WAF ni RASP: mide solo la corrección del código.
- **Corregida + RASP sin WAF:** `evidence/cierre-2026-11-20/05-corregida-rasp-sin-waf` — variante corregida con RASP, atacada dentro de la red Docker saltándose el WAF.
- **Corregida + WAF/RASP:** `evidence/cierre-2026-11-20/04-corregida-con-waf` — variante corregida con la defensa completa (WAF + RASP + SIEM), por 127.0.0.1:8088.
- **Imagen cloud final (local):** `evidence/cierre-brechas-2026-11-24/09-validacion-imagen-alpine-local/baterias/ataques` — imagen que se despliega en Render (Alpine, parches 01-14, WAF + RASP + puerta) con 0,1 vCPU, 512 MB y PostgreSQL 17, en local.
- **Render (despliegue real):** `evidence/cierre-brechas-2026-11-24/10-validacion-render/baterias/ataques` — https://juice-lab-masi-staging.onrender.com, host autorizado por el usuario; mismo arnés a través de la puerta de acceso.

## 4. Riesgos R01-R24 por capa, con decisión y residual vigentes
| Riesgo | Capa principal | Capa secundaria | Origen | Decisión (estado) | Residual |
|---|---|---|---|---|---|
| R01 Inyección SQL en el login (bypass de autenticación) | 2a Aplicación · Código | 2d Aplicación · Perímetro de la aplicación | T01 / A1 | Mitigar (Ejecutado) | 1×5 Medio |
| R02 Inyección SQL UNION en búsqueda (extracción de tablas) | 2a Aplicación · Código | 1 Datos | T02 / A2-A3 | Mitigar (Ejecutado) | 1×5 Medio |
| R03 Clave privada JWT embebida en el código (forja de tokens) | 2c Aplicación · Implementación (dependencias, secretos, integración) | 1 Datos | T03 | Eliminar (Ejecutado) | 2×5 Alto |
| R04 Bibliotecas JWT obsoletas (algoritmos débiles) | 2c Aplicación · Implementación (dependencias, secretos, integración) | 7 Políticas, procedimientos y concientización | T04 | Eliminar (Ejecutado) | 1×5 Medio |
| R05 Contraseñas con MD5 sin sal | 1 Datos | 2a Aplicación · Código | T05 | Eliminar (Ejecutado) | 1×5 Medio |
| R06 BOLA/IDOR: lectura de recursos de otro usuario | 2b Aplicación · Lógica de aplicación | 1 Datos | T06 / A12 | Eliminar (Ejecutado parcialmente) | 2×4 Medio |
| R07 Asignación masiva de role=admin en el registro | 2b Aplicación · Lógica de aplicación | 2d Aplicación · Perímetro de la aplicación | T07 / A7 | Mitigar (Ejecutado) | 1×4 Bajo |
| R08 Inyección NoSQL en reseñas (MarsDB) | 2a Aplicación · Código | 1 Datos | T08 | Eliminar (Ejecutado) | 1×4 Bajo |
| R09 Ejecución de código vía eval()/vm | 2a Aplicación · Código | 3 Host / contenedor | T09 | Eliminar (Planificado) | 3×4 Alto |
| R10 XXE en la carga de XML | 2a Aplicación · Código | 3 Host / contenedor | T10 | Eliminar (Ejecutado) | 1×5 Medio |
| R11 SSRF en la imagen de perfil por URL | 2b Aplicación · Lógica de aplicación | 4 Red interna | T11 | Mitigar (Ejecutado) | 2×3 Medio |
| R12 Listado de directorios y archivos internos (/ftp, /support/logs, /encryptionkeys) | 2d Aplicación · Perímetro de la aplicación | 1 Datos | T12 / A4-A5 | Mitigar (Ejecutado) | 3×4 Alto |
| R13 XSS (CSP débil, sin codificación de salida) | 2a Aplicación · Código | 2d Aplicación · Perímetro de la aplicación | T13 | Mitigar (Ejecutado) | 2×4 Medio |
| R14 CORS permisivo (ACAO *) | 2d Aplicación · Perímetro de la aplicación | 2c Aplicación · Implementación (dependencias, secretos, integración) | T14 / A8 | Mitigar (Ejecutado) | 1×3 Bajo |
| R15 Redirección abierta (lista blanca evadible) | 2b Aplicación · Lógica de aplicación | — | T15 | Eliminar (Planificado) | 4×3 Alto |
| R16 Fuerza bruta en el login (sin limitación de intentos) | 2d Aplicación · Perímetro de la aplicación | 2b Aplicación · Lógica de aplicación | T16 / A10 | Mitigar (Ejecutado) | 3×3 Medio |
| R17 /metrics expuesto sin autenticación | 2d Aplicación · Perímetro de la aplicación | 3 Host / contenedor | T17 / A6 | Mitigar (Ejecutado) | 3×2 Medio |
| R18 Denegación de servicio por vm/ZIP (agotamiento de recursos) | 3 Host / contenedor | 2a Aplicación · Código | T18 | Mitigar (Ejecutado parcialmente) | 3×4 Alto |
| R19 Registro sin centralización ni alertas | 7 Políticas, procedimientos y concientización | 3 Host / contenedor | T19 | Mitigar (Ejecutado parcialmente) | 2×4 Medio |
| R20 Dependencias con CVE críticas (cadena de suministro) | 2c Aplicación · Implementación (dependencias, secretos, integración) | 7 Políticas, procedimientos y concientización | T20 | Eliminar (Ejecutado parcialmente) | 2×5 Alto |
| R21 Configuración insegura de la infraestructura cloud desplegada (Render + PostgreSQL) | 5 Perímetro cloud / red | 7 Políticas, procedimientos y concientización | Fase 2 | Mitigar (Ejecutado parcialmente) | 2×4 Medio |
| R22 Bloqueo del RASP que deja peticiones colgadas o termina el proceso (auto-DoS) | 2c Aplicación · Implementación (dependencias, secretos, integración) | 3 Host / contenedor | Hallazgo Fase 6 | Eliminar (Ejecutado parcialmente) | 2×3 Medio |
| R23 Exposición de datos personales (incumplimiento de protección de datos) | 7 Políticas, procedimientos y concientización | 1 Datos | R01, R02, R06 | Mitigar (Ejecutado parcialmente) | 2×5 Alto |
| R24 SIEM del laboratorio: privilegio sobre Docker, un solo nodo, Loki sin autenticación | 3 Host / contenedor | 4 Red interna | Riesgo introducido por la Fase 6 | Mitigar (Ejecutado) | 2×3 Medio |

## 5. Las siete capas: riesgos y controles con evidencia
| Capa | Riesgos | Controles probados (evidencia en el registro de riesgos) |
|---|---|---|
| 1 Datos | R02, R03, R05, R06, R08, R12, R23 | Alerta SIEM API_BOLA_AccesoAjenoDenegado (403 a objetos ajenos; inactiva con tráfico legítimo, activa con el intento cruzado); Alerta SIEM Acceso_Rutas_Sensibles_Denegado; Alertas SIEM de inyección (WAF y RASP); Arranque fail-closed: sin secreto la aplicación no inicia (código de salida 1); Bloqueo de la extracción masiva por SQLi (WAF + RASP); Bloqueo de la vía de extracción por SQLi (WAF + RASP) … |
| 2a Aplicación · Código | R01, R02, R05, R08, R09, R10, R13, R18 | Alertas SIEM WAF_InyeccionSQL_Bloqueada y RASP_Ataque_Detectado; Alertas SIEM de inyección (WAF y RASP); Bloqueo de la vía de extracción por SQLi (WAF + RASP); CRS 941 (XSS): 403 con dos vectores acotados (parámetro de búsqueda y cuerpo de una reseña); reglas 941100/941110/941160/941390 en el audit log; CSP del WAF (script-src 'self'): bloquea scripts en línea en la nube; Contención: FS raíz de solo lectura (escritura bloqueada con EROFS), usuario no root, cap_drop ALL … |
| 2b Aplicación · Lógica de aplicación | R06, R07, R11, R15, R16 | 2FA (TOTP) de Juice Shop probada en local y en Render (13/13): con la 2FA activa la contraseña sola no da sesión (401 totp_token_required); código erróneo y tmpToken forjado (alg none) → 401; Alerta SIEM API_BOLA_AccesoAjenoDenegado (403 a objetos ajenos; inactiva con tráfico legítimo, activa con el intento cruzado); Alerta SIEM Login_FuerzaBruta_RateLimit; Alerta SIEM WAF_ParcheVirtual_Activado; Heurística SIEM API_Enumeracion_Objetos_PosibleBOLA (con falsos positivos demostrados); Límite de intentos en la nube: 429 al 5.º intento, también con X-Forwarded-For falsificado distinto en cada petición … |
| 2c Aplicación · Implementación (dependencias, secretos, integración) | R03, R04, R14, R20, R22 | Arranque fail-closed: sin secreto la aplicación no inicia (código de salida 1); En la nube la clave JWT la genera el contenedor en cada arranque (nadie la copia ni la pega; falla cerrada si no se activa): 5 casos de arranque; Imagen cloud con base Alpine de la misma versión del WAF: Trivy CRITICAL 3→1 (marsdb, exceptuada) y HIGH 135→0; puerta de release APTA; Integración rasp-guard: el bloqueo en sqlite3 se entrega como error controlado HTTP 403 (sin --unhandled-rejections=warn); Parche 04 v2: clave privada fuera del código, cargada de un secreto montado y rotada; un token firmado con la clave antigua recibe HTTP 401; Parche 07: CORS con origen explícito (variante corregida); sin ACAO abierto con Origin externo y sin WAF … |
| 2d Aplicación · Perímetro de la aplicación | R01, R07, R12, R13, R14, R16, R17 | 2FA (TOTP) de Juice Shop probada en local y en Render (13/13): con la 2FA activa la contraseña sola no da sesión (401 totp_token_required); código erróneo y tmpToken forjado (alg none) → 401; Alerta SIEM Acceso_Rutas_Sensibles_Denegado; Alerta SIEM Login_FuerzaBruta_RateLimit; Alerta SIEM WAF_ParcheVirtual_Activado; Alertas SIEM WAF_InyeccionSQL_Bloqueada y RASP_Ataque_Detectado; CRS 941 (XSS): 403 con dos vectores acotados (parámetro de búsqueda y cuerpo de una reseña); reglas 941100/941110/941160/941390 en el audit log … |
| 3 Host / contenedor | R09, R10, R17, R18, R19, R22, R24 | Alerta Ingesta_WAF_Ausente: latido del WAF cada 30 s; con el colector detenido pasó a pending (2 min) y firing (+1 min); resuelta al reanudar, 6/6 líneas recuperadas; Alerta SIEM Acceso_Rutas_Sensibles_Denegado; Alertas propias de la nube (6 reglas, entorno=cloud): SQLi bloqueada, credenciales fallidas y límite en la puerta, RASP, arranque fallido y salud del colector; 4 disparadas extremo a extremo contra Render (~1 min) sin disparar reglas locales; reglas locales acotadas a entorno=local; Centralización AUTOMÁTICA y AUTENTICADA de eventos cloud: colector de la API de Render (HTTPS + clave de solo lectura) → Loki con entorno=cloud, redacción y cursor; prueba extremo a extremo con marca; Colector cloud endurecido: sin root (65534), sistema de archivos de solo lectura, sin capacidades, clave como secreto de Docker y redacción antes de Loki (probada con simulador); Contención: FS raíz de solo lectura (escritura bloqueada con EROFS), usuario no root, cap_drop ALL … |
| 4 Red interna | R11, R24 | Colector cloud endurecido: sin root (65534), sistema de archivos de solo lectura, sin capacidades, clave como secreto de Docker y redacción antes de Loki (probada con simulador); Parche 12: la URL de imagen se valida (http/https, resolución DNS solo a IP públicas, sin redirecciones); T5: la app ya no pide la URL interna (0 peticiones en el log del WAF); Proxy del socket de Docker de solo lectura (escrituras HTTP 403); Alloy sin root, sin socket, sin capacidades; Redacción en Alloy de Authorization/Cookie/Set-Cookie y JWT en las tres fuentes antes de Loki (hallazgo: el audit log de ModSecurity guardaba el token de sesión) |
| 5 Perímetro cloud / red | R21 | Despliegue real en Render con puerta de acceso propia: sin cookie → 302, 401 sin cookie, cookie de 256 bits Secure/HttpOnly/SameSite, falsificada → 302; probado en la nube; IaC de Render validada (esquema oficial + política: plan free, BD sin acceso externo, secretos sync:false, despliegue manual, rama existente): 15/15; prueba negativa detecta 4 fallos; TLS medido en el borde: 1.0/1.1 rechazadas, 1.2 y 1.3 aceptadas (TLS_AES_256_GCM_SHA384), HTTP→HTTPS 301, HSTS |
| 6 Seguridad física | — | Ver nota |
| 7 Políticas, procedimientos y concientización | R04, R19, R20, R21, R23 | Alerta Ingesta_WAF_Ausente: latido del WAF cada 30 s; con el colector detenido pasó a pending (2 min) y firing (+1 min); resuelta al reanudar, 6/6 líneas recuperadas; Alertas propias de la nube (6 reglas, entorno=cloud): SQLi bloqueada, credenciales fallidas y límite en la puerta, RASP, arranque fallido y salud del colector; 4 disparadas extremo a extremo contra Render (~1 min) sin disparar reglas locales; reglas locales acotadas a entorno=local; Bloqueo de la extracción masiva por SQLi (WAF + RASP); Centralización AUTOMÁTICA y AUTENTICADA de eventos cloud: colector de la API de Render (HTTPS + clave de solo lectura) → Loki con entorno=cloud, redacción y cursor; prueba extremo a extremo con marca; Descubrimiento de contenedores cada 5 s (antes 60 s): 5/5 detecciones del RASP llegan a Loki tras recrear la app; Despliegue real en Render con puerta de acceso propia: sin cookie → 302, 401 sin cookie, cookie de 256 bits Secure/HttpOnly/SameSite, falsificada → 302; probado en la nube … |

**Capa 6:** El laboratorio local corre en una estación personal (HW-01) sin datos reales. El despliegue real (Render, región virginia) delega la seguridad física en el centro de datos del proveedor: responsabilidad compartida, no verificable por el equipo (sin contrato ni SLA revisado). El diseño AWS de la Fase 2 sigue siendo solo diseño.

**Capa 5:** Perímetro cloud REAL: borde de Render (Cloudflare + balanceador, TLS 1.2/1.3 medido, DDoS de la plataforma) y la puerta propia en nginx (autenticación previa, límite de intentos, WAF). Sin CDN con caché ni WAF gestionado propios (requieren dominio): ver docs/cierre-tecnico/REQUISITOS_CLOUD_DISENO_VS_IMPLEMENTADO.md.

## 6. Infraestructura cloud real (Render + PostgreSQL): amenazas STRIDE y DREAD
Amenazas del despliegue real (no del diseño AWS). DREAD con la misma escala y orden (D, R, E, A, Di); valoración del equipo.

| Amenaza | Elemento | STRIDE | Descripción | D | R | E | A | Di | Promedio | Nivel | Riesgo (residual vigente) | Control | Evidencia |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TC01 | Borde de Render → puerta /__acceso | S, E | Acceso no autorizado a la demostración pública (omisión de la puerta de acceso) | 8 | 6 | 5 | 9 | 8 | 7.2 | Alto | R21 (2×4 Medio) | Puerta propia; un 401 no entrega cookie; cookie de 256 bits Secure/HttpOnly/SameSite | `evidence/cierre-brechas-2026-11-24/10-validacion-render/baterias/puerta-acceso.md` |
| TC02 | Borde de Render → login y puerta | S, D | Fuerza bruta evadiendo el límite con X-Forwarded-For falsificado | 6 | 8 | 7 | 6 | 7 | 6.8 | Alto | R16 (3×3 Medio) | IP real = última dirección de X-Forwarded-For (sin recursión); 429 al 5.º intento | `evidence/cierre-brechas-2026-11-24/10-validacion-render/baterias/puerta-acceso.md` |
| TC03 | Servicio web → PostgreSQL administrado | I, T | BD administrada expuesta a Internet o con credenciales en el repositorio | 9 | 5 | 4 | 9 | 6 | 6.6 | Alto | R21 (2×4 Medio) | ipAllowList vacía; DATABASE_URL por referencia del Blueprint; TLS obligatorio | `evidence/cierre-brechas-2026-11-24/05-iac-render/validacion.md` |
| TC04 | Panel de Render / repositorio | I, S | Secretos de la nube expuestos (clave JWT, usuarios de la puerta, API key) | 9 | 4 | 5 | 9 | 6 | 6.6 | Alto | R03 (2×5 Alto) | Clave JWT generada por el contenedor; secretos sync:false; API key de solo lectura fuera de git; Gitleaks en CI | `evidence/cierre-tecnico-2026-11-23/13-cloud/arranque-casos.md` |
| TC05 | Contenedor → logs de Render | I | Tokens, cookies o contraseñas en los logs de la plataforma o del SIEM | 7 | 6 | 4 | 8 | 5 | 6.0 | Alto | R23 (2×5 Alto) | Auditoría del WAF sin cabeceras ni cuerpos (A,F,H,Z); redacción en el colector; 0 secretos en Loki | `evidence/cierre-brechas-2026-11-24/06-siem-render/extremo-a-extremo.md` |
| TC06 | Imagen del contenedor cloud | T, E, D | Paquetes del sistema vulnerables en la imagen del WAF (cadena de suministro) | 7 | 4 | 4 | 9 | 9 | 6.6 | Alto | R20 (2×5 Alto) | Base Alpine de la misma versión del WAF; puerta de release APTA (0 HIGH) en local y en CI | `evidence/cierre-brechas-2026-11-24/08-puerta-release-local/cloud-alpine/puerta-release.md` |
| TC07 | Blueprint render.yaml | T | Configuración insegura del Blueprint (plan de pago, BD abierta, despliegue automático, rama equivocada) | 6 | 5 | 4 | 8 | 6 | 5.8 | Medio | R21 (2×4 Medio) | validar-render.py (esquema oficial + política) en CI; prueba negativa | `evidence/cierre-brechas-2026-11-24/05-iac-render/prueba-negativa.md` |
| TC08 | Plataforma (plan free) | D | Indisponibilidad: suspensión por inactividad, vencimiento de la BD free (30 días), límite de memoria | 3 | 9 | 8 | 9 | 9 | 7.6 | Alto | R21 (2×4 Medio) | Supervisión del arranque (el contenedor se detiene si la app cae); memoria medida 132-204 MiB de 512; procedimiento de reactivación documentado | `evidence/cierre-brechas-2026-11-24/09-validacion-imagen-alpine-local/recursos.txt` |
| TC09 | Contenedor → SIEM | R | Pérdida de trazabilidad de lo ocurrido en la nube (logs 7 días en Render, sin centralizar) | 5 | 6 | 5 | 7 | 6 | 5.8 | Medio | R19 (2×4 Medio) | Colector automático y autenticado (API de Render) → Loki con entorno=cloud; latencia medida 48 s; 6 alertas propias de la nube (4 disparadas extremo a extremo, ~1 min) y alerta de salud del colector | `evidence/cierre-brechas-2026-11-24/13-alertas-cloud/LEAME.md` |
| TC10 | Cuenta de Render (plano de control) | S, T, E | Compromiso de la cuenta del equipo en Render o GitHub | 10 | 3 | 4 | 10 | 5 | 6.4 | Alto | R21 (2×4 Medio) | Inicio de sesión con GitHub; API key con permiso mínimo. MFA SIN VERIFICAR (pendiente del equipo) | `evidence/cierre-brechas-2026-11-24/06-siem-render/api-key-render.md` |

Clases STRIDE cubiertas en la nube: D, E, I, R, S, T (6 de 6).

Registro de riesgos usado: `docs/fase-6/riesgo-cierre-brechas/riesgos-calculados.json`.
