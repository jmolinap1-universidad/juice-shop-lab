# Fase 6 – Tratamiento formal del riesgo

> **Documento generado** por `docs/fase-6/datos/generar_md.py` (tras `riesgo.py`, que valida los datos). No editar
> las tablas a mano: modificar `datos/riesgos.json` y ejecutar `make risk`. Versión de datos: 2 (2026-11-10, auditoría de cierre).

## 1. Método
- **Marco:** ISO/IEC 27005:2022 define el proceso (identificar, analizar, evaluar, tratar) y las opciones de tratamiento; NO prescribe una fórmula aritmética. La escala 1-5, la derivación desde DREAD y las pautas de reducción son una CONVENCIÓN PROPIA del equipo, documentada aquí.
- **Escala:** Probabilidad (P) e Impacto (I) de 1 a 5; nivel = P x I: Bajo 1-4, Medio 5-9, Alto 10-16, Crítico 20-25.
- **Inherente:** P = ceil(media(R, E, Di) / 2); I = ceil(media(D, A) / 2), desde el DREAD de docs/fase-1 (orden D, R, E, A, Di). Riesgos sin DREAD (R21-R24): valoración del equipo con justificación escrita; R22 usa además la medición del escenario 2b.
- **Residual:** Valor EXPLÍCITO por riesgo, con razonamiento de P y de I. El validador (riesgo.py) rechaza cualquier reducción no respaldada por un control con estado 'verificado' y verificación 'probado'.
  - P solo baja con controles preventivos, de eliminación o de evitación PROBADOS (prueba representativa con evidencia).
  - Pauta orientativa: una capa preventiva probada, P-2; dos capas independientes probadas, P-3; eliminación o evitación probada de toda la causa, P=1. Si el control cubre solo parte de las vías de ataque, la reducción es menor y se justifica.
  - I solo baja con contención o respuesta PROBADAS que demuestren menor consecuencia. La detección (SIEM, SCA, alertas) aporta visibilidad y NO reduce el impacto.
  - Controles configurados pero no ejercitados ('inspeccionado'), diseñados o propuestos NO reducen el residual: se informan como plan.
- **Validación automática** (`datos/validacion-consistencia.txt`): 24 IDs únicos, escala 1-5, residual ≤ inherente,
  reducciones solo con control probado, coherencia decisión/estado, aceptaciones con condiciones, transferencias
  propuestas marcadas como tales, rutas de evidencia existentes y recuentos que suman 24. Prueba negativa del
  validador: `datos/prueba-negativa-validador.txt`.

## 2. Opciones de tratamiento
| Decisión | Significado en este proyecto |
|---|---|
| **Mitigar** | Reducir probabilidad o impacto con controles (ISO/IEC 27005: *modificar*). No elimina la causa. |
| **Eliminar** | Suprimir la causa raíz (corregir el código o la configuración). Registrarla como plan no equivale a haberla eliminado. |
| **Evitar** | No realizar la actividad o retirar la funcionalidad que origina el riesgo. |
| **Transferir** | Compartir el riesgo con un tercero (proveedor gestionado, póliza, contrato). No transfiere la responsabilidad del titular; aquí solo está **propuesta**. |
| **Aceptar** | Retener el riesgo de forma consciente, documentada, temporal y con condiciones (ISO/IEC 27005: *retener*). |

## 3. Registro de riesgos: categorización por tipo e impacto
| ID | Riesgo | Origen | Tipo | Impactos (principal primero) | OWASP 2025 | CWE |
|---|---|---|---|---|---|---|
| R01 | Inyección SQL en el login (bypass de autenticación) | T01 / A1 | Seguridad | Reputacional, Legal, Financiero | A05:2025 | CWE-89 |
| R02 | Inyección SQL UNION en búsqueda (extracción de tablas) | T02 / A2-A3 | Seguridad | Legal, Reputacional, Financiero | A05:2025 | CWE-89 |
| R03 | Clave privada JWT embebida en el código (forja de tokens) | T03 | Seguridad | Reputacional, Legal, Financiero | A04:2025 | CWE-798/321 |
| R04 | Bibliotecas JWT obsoletas (algoritmos débiles) | T04 | Software | Reputacional, Financiero | A03:2025 | CWE-347 |
| R05 | Contraseñas con MD5 sin sal | T05 | Seguridad | Legal, Reputacional | A04:2025 | CWE-916 |
| R06 | BOLA/IDOR: lectura de recursos de otro usuario | T06 / A12 | Seguridad | Legal, Reputacional | A01:2025 (API1:2023) | CWE-639 |
| R07 | Asignación masiva de role=admin en el registro | T07 / A7 | Seguridad | Reputacional, Financiero | A01:2025 | CWE-915 |
| R08 | Inyección NoSQL en reseñas (MarsDB) | T08 | Seguridad | Reputacional, Operacional | A05:2025 | CWE-943 |
| R09 | Ejecución de código vía eval()/vm | T09 | Seguridad | Operacional, Reputacional, Financiero | A05:2025 | CWE-95 |
| R10 | XXE en la carga de XML | T10 | Seguridad | Legal, Operacional | A02:2025 | CWE-611 |
| R11 | SSRF en la imagen de perfil por URL | T11 | Seguridad | Operacional, Legal | A01:2025 | CWE-918 |
| R12 | Listado de directorios y archivos internos (/ftp, /support/logs, /encryptionkeys) | T12 / A4-A5 | Seguridad | Reputacional, Legal | A02:2025 | CWE-548/538 |
| R13 | XSS (CSP débil, sin codificación de salida) | T13 | Seguridad | Reputacional, Legal | A05:2025 | CWE-79 |
| R14 | CORS permisivo (ACAO *) | T14 / A8 | Seguridad | Reputacional | A02:2025 | CWE-942 |
| R15 | Redirección abierta (lista blanca evadible) | T15 | Seguridad | Reputacional | A01:2025 | CWE-601 |
| R16 | Fuerza bruta en el login (sin limitación de intentos) | T16 / A10 | Seguridad | Reputacional, Operacional | A07:2025 | CWE-307 |
| R17 | /metrics expuesto sin autenticación | T17 / A6 | Seguridad | Reputacional | A02:2025 | CWE-200 |
| R18 | Denegación de servicio por vm/ZIP (agotamiento de recursos) | T18 | Técnico | Operacional, Financiero | A10:2025 | CWE-400 |
| R19 | Registro sin centralización ni alertas | T19 | Operacional | Operacional, Legal | A09:2025 | CWE-778 |
| R20 | Dependencias con CVE críticas (cadena de suministro) | T20 | Software | Financiero, Reputacional, Legal | A03:2025 | CWE-1395 |
| R21 | Configuración insegura al desplegar la arquitectura cloud (AWS) | Fase 2 | Cloud | Financiero, Operacional, Legal | A02:2025 | CWE-16 |
| R22 | Bloqueo del RASP que deja peticiones colgadas o termina el proceso (auto-DoS) | Hallazgo Fase 6 | Técnico | Operacional, Reputacional | A10:2025 | CWE-248/755 |
| R23 | Exposición de datos personales (incumplimiento de protección de datos) | R01, R02, R06 | Cumplimiento | Legal, Reputacional, Financiero | A01/A05:2025 | CWE-200 |
| R24 | SIEM del laboratorio: privilegio sobre Docker, un solo nodo, Loki sin autenticación | Riesgo introducido por la Fase 6 | Operacional | Operacional, Reputacional | A09:2025 | CWE-250 |

**Por tipo:** Seguridad: 16 · Software: 2 · Técnico: 2 · Operacional: 2 · Cloud: 1 · Cumplimiento: 1.  
**Por impacto (riesgos que lo incluyen):** Reputacional: 19 · Legal: 13 · Financiero: 10 · Operacional: 10.

## 4. Matriz de decisiones y plan de tratamiento
| ID | Inherente | Decisión principal (estado) | Complementaria (estado) | Residual | Prioridad | Responsable (rol) | Revisión |
|---|---|---|---|---|---|---|---|
| R01 | 5×5=25 Crítico | **Mitigar** (Ejecutado) | Eliminar (Planificado) | 2×5=10 **Alto** | Alta | Operaciones de seguridad (WAF/RASP); Desarrollo backend (parche 01) | Al desplegar el parche 01: repetir run.sh sin WAF y comprobar A1 sin vulnerabilidad |
| R02 | 5×5=25 Crítico | **Mitigar** (Ejecutado) | Eliminar (Planificado) | 2×5=10 **Alto** | Alta | Operaciones de seguridad (WAF/RASP); Desarrollo backend (parche 02) | Al desplegar el parche 02: repetir run.sh sin WAF (A2-A3) |
| R03 | 4×5=20 Crítico | **Eliminar** (Planificado) | Transferir (Propuesta) | 4×5=20 **Crítico** | Muy alta | Desarrollo backend (parche 04); Arquitectura cloud (gestor de secretos) | Antes de cualquier despliegue fuera del laboratorio; al aplicar el parche 04 |
| R04 | 3×5=15 Alto | **Aceptar** (Aceptado temporalmente) | Eliminar (Planificado) | 3×5=15 **Alto** | Alta | Dueño del riesgo: líder del proyecto (acepta); Desarrollo backend (actualización) | En cada ejecución del pipeline SCA y antes de cualquier uso fuera del laboratorio |
| R05 | 4×5=20 Crítico | **Eliminar** (Planificado) | Mitigar (Ejecutado parcialmente) | 3×5=15 **Alto** | Alta | Desarrollo backend (parche 03) | Al desplegar el parche 03 (rehash progresivo al iniciar sesión) |
| R06 | 5×4=20 Crítico | **Eliminar** (Planificado) | Mitigar (Ejecutado parcialmente) | 5×4=20 **Crítico** | Muy alta | Desarrollo backend (parche 08); Monitoreo (heurística SIEM) | Al desplegar el parche 08: repetir A12 (debe responder 403) y el tráfico legítimo |
| R07 | 4×4=16 Alto | **Mitigar** (Ejecutado) | Eliminar (Planificado) | 2×4=8 **Medio** | Media | Operaciones de seguridad (parche virtual); Desarrollo backend (parche 06) | Al desplegar el parche 06; revisión del parche virtual si cambia el modelo de usuario |
| R08 | 4×4=16 Alto | **Eliminar** (Planificado) | — | 4×4=16 **Alto** | Alta | Desarrollo backend | Al implementar la validación de operadores; incluir un caso en run.sh |
| R09 | 3×5=15 Alto | **Eliminar** (Planificado) | Mitigar (Ejecutado) | 3×4=12 **Alto** | Alta | Desarrollo backend (parche 05); Operaciones (runtime) | Al desplegar el parche 05 |
| R10 | 3×5=15 Alto | **Eliminar** (Planificado) | — | 3×5=15 **Alto** | Alta | Desarrollo backend | Al endurecer el parser; añadir caso de prueba |
| R11 | 4×3=12 Alto | **Mitigar** (Planificado) | Eliminar (Planificado) | 4×3=12 **Alto** | Alta | Desarrollo backend; Operaciones (filtrado de egreso) | Al implementar la lista blanca; probar con un destino interno del laboratorio |
| R12 | 5×4=20 Crítico | **Mitigar** (Ejecutado) | Evitar (Planificado) | 3×4=12 **Alto** | Alta | Operaciones de seguridad (WAF); Desarrollo backend (retirar serve-index) | Al retirar serve-index: repetir A4-A5 sin WAF |
| R13 | 4×4=16 Alto | **Mitigar** (Ejecutado parcialmente) | Eliminar (Planificado) | 4×4=16 **Alto** | Alta | Operaciones de seguridad (CSP); Desarrollo frontend (codificación de salida) | Al añadir casos de XSS al arnés (reflejado y persistente) |
| R14 | 4×3=12 Alto | **Mitigar** (Ejecutado) | Eliminar (Planificado) | 2×3=6 **Medio** | Media | Operaciones de seguridad (WAF); Desarrollo backend (parche 07) | Al desplegar el parche 07 |
| R15 | 4×3=12 Alto | **Eliminar** (Planificado) | — | 4×3=12 **Alto** | Alta | Desarrollo backend | Al corregir la comparación de destinos |
| R16 | 5×3=15 Alto | **Mitigar** (Ejecutado) | — | 3×3=9 **Medio** | Media | Operaciones de seguridad (WAF) | Si se publica detrás de un balanceador (revisar la IP de cliente usada por limit_req) |
| R17 | 5×2=10 Alto | **Mitigar** (Ejecutado) | Evitar (Planificado) | 3×2=6 **Medio** | Media | Operaciones de seguridad (WAF); Monitoreo (red de métricas) | Al exponer métricas a un recolector: solo por red interna y con autenticación |
| R18 | 3×4=12 Alto | **Mitigar** (Ejecutado parcialmente) | — | 3×4=12 **Alto** | Alta | Operaciones (runtime) | Tras una prueba de carga controlada en el laboratorio |
| R19 | 3×4=12 Alto | **Mitigar** (Ejecutado parcialmente) | Eliminar (Planificado) | 2×4=8 **Medio** | Media | Monitoreo (SIEM) | Al añadir notificaciones y monitorear la propia ingesta |
| R20 | 4×5=20 Crítico | **Aceptar** (Aceptado temporalmente) | Eliminar (Planificado) | 4×5=20 **Crítico** | Muy alta | Dueño del riesgo: líder del proyecto (acepta); Desarrollo (actualización) | En cada push (SCA en CI) y antes de cualquier uso fuera del laboratorio |
| R21 | 3×4=12 Alto | **Evitar** (Ejecutado) | Transferir (Propuesta) | 1×4=4 **Bajo** | Baja | Arquitectura cloud; Dueño del riesgo: líder del proyecto (aprobación de costos) | Antes de cualquier terraform apply: pruebas en ejecución además de Checkov |
| R22 | 5×3=15 Alto | **Eliminar** (Ejecutado parcialmente) | — | 2×3=6 **Medio** | Media | Operaciones de seguridad (integración del RASP) | Al ejercitar bloqueos en los sinks fs, http, child_process y vm |
| R23 | 5×5=25 Crítico | **Mitigar** (Ejecutado parcialmente) | Transferir (Propuesta) | 4×5=20 **Crítico** | Muy alta | Dueño del riesgo: líder del proyecto; Desarrollo backend (R06) | Al cerrar R06 (BOLA) y antes de tratar datos reales |
| R24 | 2×5=10 Alto | **Mitigar** (Ejecutado) | Aceptar (Aceptado temporalmente) | 2×3=6 **Medio** | Media | Monitoreo (SIEM); Dueño del riesgo: líder del proyecto (acepta un solo nodo) | Antes de cualquier uso fuera del laboratorio |

**Decisiones principales:** Mitigar: 13 · Eliminar: 8 · Aceptar: 2 · Evitar: 1.  
**Complementarias:** Eliminar (Planificado): 9 · Transferir (Propuesta): 3 · Mitigar (Ejecutado parcialmente): 2 · Evitar (Planificado): 2 · Mitigar (Ejecutado): 1 · Aceptar (Aceptado temporalmente): 1.
Los responsables se expresan por **rol**; el equipo asigna a la persona concreta de cada rol.

### 4.1 Aceptaciones temporales
| ID | Quién acepta | Motivo | Condiciones | Vigencia |
|---|---|---|---|---|
| R04 | Líder del proyecto (rol de dueño del riesgo; el equipo asigna la persona) | Actualizar las bibliotecas rompe retos de OWASP Juice Shop, que es el objeto de estudio del laboratorio. | Solo en el laboratorio: escucha en 127.0.0.1, sin datos reales ni usuarios externos; la versión vulnerable nunca se publica. | Hasta el cierre del curso. No aplica a producción, donde la decisión es Eliminar. |
| R20 | Líder del proyecto (rol de dueño del riesgo; el equipo asigna la persona) | La aplicación es intencionalmente vulnerable; actualizar dependencias rompe los retos que se estudian. | Solo en el laboratorio aislado (127.0.0.1), sin datos reales; WAF y RASP delante; SCA en cada push. | Hasta el cierre del curso. En producción: Eliminar (nunca aceptación automática). |
| R24 | Líder del proyecto (rol de dueño del riesgo; el equipo asigna la persona) | Un SIEM de un solo nodo, sin autenticación en Loki, basta para demostrar la centralización y la correlación en el laboratorio. | Puertos solo en 127.0.0.1; proxy del socket de solo lectura; red del proxy interna; sin telemetría externa. | Solo en el laboratorio. No es una configuración apta para producción. |

## 5. Justificación del riesgo residual (por riesgo)
| ID | Inherente | Residual | Razón de P | Razón de I | Actividad pendiente |
|---|---|---|---|---|---|
| R01 | 5×5 (DREAD Fase 1) | 2×5 | Dos capas preventivas independientes probadas (WAF y RASP en el sink) bloquean el vector: P-3. No llega a 1 porque la causa (consulta concatenada) sigue en el código y una evasión del CRS en PL1 no está descartada. | Si el ataque prospera, la consecuencia es la misma (sesión de administrador). Las alertas no reducen el impacto. | Recompilar la aplicación con el parche 01 (consulta parametrizada) y verificarlo |
| R02 | 5×5 (DREAD Fase 1) | 2×5 | Dos capas preventivas independientes probadas: P-3. La causa sigue en el código. | La extracción de tablas tendría la misma consecuencia; la detección no la reduce. | Recompilar con el parche 02 y verificarlo |
| R03 | 4×5 (DREAD Fase 1) | 4×5 | Ningún control desplegado impide ni detecta un JWT forjado con la clave embebida. | Forjar tokens de cualquier usuario sigue siendo posible. | Aplicar el parche 04 (manual: la clave no se versiona), rotar la clave y cargarla desde un gestor de secretos |
| R04 | 3×5 (DREAD Fase 1) | 3×5 | El SCA identifica el componente pero no lo actualiza: la vulnerabilidad sigue presente. | Sin cambio: la detección no reduce el impacto. | Actualizar jsonwebtoken/express-jwt y fijar algorithms: ['RS256'] en un entorno que no dependa de los retos |
| R05 | 4×5 (DREAD Fase 1) | 3×5 | Solo se bloqueó UNA vía de exposición de hashes (SQLi): P-1. Otras vías (XXE R10, respaldos u otros IDOR) no están probadas y el algoritmo sigue siendo MD5. | Si los hashes se filtran, MD5 sin sal sigue siendo trivial de revertir. | Aplicar el parche 03 (bcrypt) con migración de hashes existentes |
| R06 | 5×4 (DREAD Fase 1) | 5×4 | La lectura cruzada sigue funcionando a través de WAF y RASP (verificado). La heurística no bloquea. | La heurística aporta visibilidad (y tiene falsos positivos); no limita los datos expuestos. | Aplicar, compilar y probar el parche 08; extender la verificación de propietario a Addresses, Cards y Feedbacks |
| R07 | 4×4 (DREAD Fase 1) | 2×4 | Una capa preventiva probada en el perímetro: P-2. Sin WAF la asignación sigue funcionando (escenario 2d, A7). | Una cuenta de administrador creada tendría la misma consecuencia. | Aplicar el parche 06 (lista blanca de campos) |
| R08 | 4×4 (DREAD Fase 1) | 4×4 | Sin control probado: el RASP solo cubre NoSQL de MongoDB y el CRS no se ejercitó en esta ruta. | Sin cambio. | Rechazar operadores ($ne, $where...) en filtros y añadir un caso de prueba |
| R09 | 3×5 (DREAD Fase 1) | 3×4 | No hay control preventivo probado sobre eval/vm (el RASP instrumenta node:vm, pero no se ejercitó). | La escritura en el FS raíz está bloqueada (EROFS, probado en la Fase 5): sin persistencia ni modificación de binarios, I-1. La lectura de datos sigue siendo posible. | Aplicar el parche 05 (eliminar eval) y revisar b2bOrder/captcha (vm) |
| R10 | 3×5 (DREAD Fase 1) | 3×5 | Sin control probado. | Sin cambio. | Configurar el parser XML sin entidades externas ni DTD |
| R11 | 4×3 (DREAD Fase 1) | 4×3 | Sin control probado (la protección SSRF del RASP no se ejercitó). | Sin cambio. | Lista blanca de destinos y filtrado de egreso de red |
| R12 | 5×4 (DREAD Fase 1) | 3×4 | Una capa preventiva probada en el perímetro: P-2. Sin WAF los listados siguen expuestos (escenario 2d, A4-A5). | Sin cambio. | Retirar los listados y los archivos internos del servidor web (Evitar) |
| R13 | 4×4 (DREAD Fase 1) | 4×4 | La presencia de la cabecera CSP y de las reglas 941 no demuestra que los vectores XSS estén mitigados: no se ejercitó ningún vector. | Sin cambio. | Probar vectores XSS concretos contra el laboratorio y aplicar codificación de salida |
| R14 | 4×3 (DREAD Fase 1) | 2×3 | Una capa preventiva probada (la respuesta con Origin externo ya no lleva ACAO): P-2. | Sin cambio. | Aplicar el parche 07 (origen explícito) |
| R15 | 4×3 (DREAD Fase 1) | 4×3 | Sin control probado. | Sin cambio. | Comparación exacta de destinos permitidos |
| R16 | 5×3 (DREAD Fase 1) | 3×3 | Una capa preventiva probada desde una IP: P-2. Un ataque distribuido desde muchas IP no está cubierto. | Sin cambio. | Limitación por cuenta además de por IP (ataques distribuidos no probados) |
| R17 | 5×2 (DREAD Fase 1) | 3×2 | El deny de nginx y el parche 100002 están en el MISMO componente (WAF): cuentan como una capa, P-2. Sin WAF, /metrics sigue abierto (2d, A6). | Sin cambio. | Servir /metrics solo en la red de monitoreo (Evitar la exposición en la app) |
| R18 | 3×4 (DREAD Fase 1) | 3×4 | Sin control preventivo probado. | Los límites están configurados (docker inspect) pero no se probó que absorban un ataque de disponibilidad. | Prueba de carga controlada que demuestre el efecto de los límites |
| R19 | 3×4 (DREAD Fase 1) | 2×4 | La centralización y la correlación están probadas: P-1 respecto de 3. No llega a 1: no hay notificación a personas, es de un solo nodo y se observó una interrupción de 11 minutos en la ingesta de contenedores durante la validación. | Sin cambio. | Notificación externa (Alertmanager/correo), alta disponibilidad y alerta por ausencia de datos de cada fuente |
| R20 | 4×5 (DREAD Fase 1) | 4×5 | Los escáneres identifican los componentes, no eliminan la vulnerabilidad. | Sin cambio. | Actualizar crypto-js, lodash, marsdb y demás en un entorno que no dependa de los retos |
| R21 | 3×4 (Cualitativa) | 1×4 | Evitación probada: no hay despliegue, así que el riesgo no puede materializarse HOY. Esto NO valida la seguridad de la infraestructura. | Sin cambio. | Si se despliega: validar la seguridad en ejecución (no solo estática) y revaluar este riesgo |
| R22 | 5×3 (Cualitativa) | 2×3 | Corregido y probado para los sinks de sqlite3 (403 en 0,04-0,15 s; disponibilidad 41/41; RestartCount 0). No llega a 1: los bloqueos en fs, http, child_process y vm no se probaron. | En los sinks no probados la consecuencia podría seguir siendo una caída. | Probar el bloqueo en los demás sinks y extender rasp-guard si es necesario; respuesta 403 sin traza de pila |
| R23 | 5×5 (Cualitativa) | 4×5 | Se bloqueó la vía de SQLi (probado), pero la vía BOLA sigue abierta (probado): P-1. | La consecuencia legal y reputacional de una exposición no cambia; la transferencia solo está propuesta. | Eliminar el BOLA (parche 08) y evaluar póliza o cláusulas contractuales si hubiera datos reales |
| R24 | 2×5 (Cualitativa) | 2×3 | Sin cambio de exposición (no hay puertos nuevos). | Contención probada: comprometer Alloy ya solo permite LEER metadatos y logs de contenedores (crear, detener o ejecutar responde 403), I-2. El proxy sí mantiene el socket: es el componente de confianza. | Autenticación en Loki y Grafana, alta disponibilidad, notificaciones y alerta por pérdida de ingesta |

**Justificación de las valoraciones inherentes cualitativas:** R21: Si se desplegara: la mala configuración cloud es frecuente (P3) y expondría datos y costos (I4). R22: Medido en el escenario 2b: el primer bloqueo terminó el proceso (RestartCount 0->1; 5 de 6 sondeos sin respuesta). Cualquier intento de inyección lo provoca (P5); el servicio cae hasta el reinicio automático (I3). R23: La extracción de correos y hashes por SQLi está demostrada (A2) y el BOLA expone recursos de otros usuarios (A12). R24: Configuración inicial: Alloy como root con docker.sock montado ':ro', que NO limita la API. Comprometer Alloy equivalía a controlar Docker en el equipo (I5); no expone puertos (P2).

## 6. Controles por riesgo: implementación, verificación y evidencia
### R01 — Inyección SQL en el login (bypass de autenticación)
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| WAF ModSecurity + CRS 942100/949110 (HTTP 403) | preventivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/http.tsv` |
| RASP Aikido Zen + integración rasp-guard: bloqueo en sqlite3.all con HTTP 403 | preventivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/02d-rasp-bloqueo-integrado/http.tsv` |
| Alertas SIEM WAF_InyeccionSQL_Bloqueada y RASP_Ataque_Detectado | detectivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03b-rasp-a-siem/alertas.json` |
| Parche 01: consulta parametrizada | eliminacion | Diseñado (diff validado) | Sin verificar | `app-hardened/patches/01-sqli-login.patch` |

### R02 — Inyección SQL UNION en búsqueda (extracción de tablas)
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| WAF ModSecurity + CRS 942xxx (HTTP 403) | preventivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/http.tsv` |
| RASP Aikido Zen + rasp-guard: bloqueo en sqlite3.all (query.q) con HTTP 403 | preventivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/02d-rasp-bloqueo-integrado/http.tsv` |
| Alertas SIEM de inyección (WAF y RASP) | detectivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03b-rasp-a-siem/alertas.json` |
| Parche 02: consulta parametrizada | eliminacion | Diseñado (diff validado) | Sin verificar | `app-hardened/patches/02-sqli-search.patch` |

### R03 — Clave privada JWT embebida en el código (forja de tokens)
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| Parche 04: clave privada fuera del código (variable/secreto) | eliminacion | Diseñado (diff validado) | Sin verificar | `app-hardened/patches/04-clave-privada-embebida.patch` |
| Gestor de secretos / KMS del proveedor cloud (custodia compartida, no transfiere la responsabilidad) | transferencia | Propuesto | Sin verificar | `infra/terraform/` |

*Nota:* El endpoint /encryptionkeys/jwt.pub sirve la clave PÚBLICA: no es una vulnerabilidad y su bloqueo no reduce este riesgo.

### R04 — Bibliotecas JWT obsoletas (algoritmos débiles)
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| SCA en CI (npm audit, OSV, Grype) que identifica el componente | detectivo | Implementado | Probado | `evidence/fase-3/sca/` |
| Actualizar bibliotecas JWT y fijar algoritmos | eliminacion | Propuesto | Sin verificar | `docs/fase-1/fase1-modelado-amenazas.md` |

### R05 — Contraseñas con MD5 sin sal
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| Bloqueo de la vía de extracción por SQLi (WAF + RASP) | preventivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/http.tsv` |
| Parche 03: bcrypt (factor 12) | eliminacion | Diseñado (diff validado) | Sin verificar | `app-hardened/patches/03-md5-a-bcrypt.patch` |

### R06 — BOLA/IDOR: lectura de recursos de otro usuario
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| WAF: no bloquea la lectura cruzada (A12 HTTP 200 a través del WAF) | preventivo | Implementado, no efectivo | NO efectivo (probado) | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/bola/resultado-bola.md` |
| Heurística SIEM API_Enumeracion_Objetos_PosibleBOLA (con falsos positivos demostrados) | detectivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/04-falsos-positivos/alertas-tras-trafico-legitimo.json` |
| Parche 08: verificación de propietario (403) | eliminacion | Diseñado (diff validado) | Sin verificar | `app-hardened/patches/08-bola-cesta-propietario.patch` |

### R07 — Asignación masiva de role=admin en el registro
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| Parche virtual ModSecurity 100001 (HTTP 403) | preventivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/http.tsv` |
| Alerta SIEM WAF_ParcheVirtual_Activado | detectivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/reglas-estado.json` |
| Parche 06: lista blanca de campos | eliminacion | Diseñado (diff validado) | Sin verificar | `app-hardened/patches/06-asignacion-masiva-registro.patch` |

### R08 — Inyección NoSQL en reseñas (MarsDB)
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| Rechazar operadores en filtros de MarsDB | eliminacion | Propuesto | Sin verificar | `docs/fase-1/fase1-modelado-amenazas.md` |

### R09 — Ejecución de código vía eval()/vm
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| Contención: FS raíz de solo lectura (escritura bloqueada con EROFS), usuario no root, cap_drop ALL | contencion | Implementado | Probado | `evidence/fase-5/despues/runtime-hardening-inspect.txt` |
| Parche 05: eliminar eval() | eliminacion | Diseñado (diff validado) | Sin verificar | `app-hardened/patches/05-eval-userprofile.patch` |

### R10 — XXE en la carga de XML
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| Parser XML sin entidades externas ni DTD | eliminacion | Propuesto | Sin verificar | `app-hardened/patches/README.md` |

### R11 — SSRF en la imagen de perfil por URL
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| Lista blanca de destinos y filtrado de egreso | preventivo | Propuesto | Sin verificar | `app-hardened/patches/README.md` |

### R12 — Listado de directorios y archivos internos (/ftp, /support/logs, /encryptionkeys)
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| nginx deny de rutas sensibles (HTTP 403) | preventivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/http.tsv` |
| Alerta SIEM Acceso_Rutas_Sensibles_Denegado | detectivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/reglas-estado.json` |
| Retirar serve-index y archivos internos (Evitar) | evitacion | Propuesto | Sin verificar | `app-hardened/patches/README.md` |

*Nota:* En /encryptionkeys el problema es el LISTADO del directorio; la clave pública que contiene no es una vulnerabilidad.

### R13 — XSS (CSP débil, sin codificación de salida)
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| CSP (script-src 'self') y cabeceras en el WAF: presentes en la respuesta | preventivo | Implementado | Inspeccionado (configurado, no ejercitado) | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/a9-security-headers.txt` |
| CRS 941 (XSS) cargado, sin eventos observados | preventivo | Implementado | Inspeccionado (configurado, no ejercitado) | `evidence/fase-6/waf/crs-inventario.txt` |
| Codificación de salida en el frontend | eliminacion | Propuesto | Sin verificar | `docs/fase-1/fase1-modelado-amenazas.md` |

### R14 — CORS permisivo (ACAO *)
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| WAF oculta Access-Control-Allow-Origin (comprobado con Origin externo) | preventivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/a8-cors-headers.txt` |
| Parche 07: origen explícito | eliminacion | Diseñado (diff validado) | Sin verificar | `app-hardened/patches/07-cors-restringido.patch` |

### R15 — Redirección abierta (lista blanca evadible)
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| Comparación exacta de destinos permitidos | eliminacion | Propuesto | Sin verificar | `docs/fase-1/fase1-modelado-amenazas.md` |

### R16 — Fuerza bruta en el login (sin limitación de intentos)
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| Rate limiting nginx 5/min por IP, ráfaga 3 (HTTP 429) | preventivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/a10-bruteforce-login.txt` |
| Alerta SIEM Login_FuerzaBruta_RateLimit | detectivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/reglas-estado.json` |

### R17 — /metrics expuesto sin autenticación
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| nginx deny /metrics + parche virtual 100002 (mismo componente WAF) | preventivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/a6-metrics.txt` |
| Alerta SIEM Acceso_Rutas_Sensibles_Denegado | detectivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/reglas-estado.json` |

### R18 — Denegación de servicio por vm/ZIP (agotamiento de recursos)
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| Límites de pids (200), memoria (1 GiB) y CPU (1.0) configurados | contencion | Implementado | Inspeccionado (configurado, no ejercitado) | `evidence/fase-5/despues/runtime-hardening-inspect.txt` |

### R19 — Registro sin centralización ni alertas
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| SIEM: Alloy -> Loki -> Grafana; 3 fuentes ingestadas y 7 reglas (6 disparadas en las pruebas) | preventivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03b-rasp-a-siem/alertas.json` |

### R20 — Dependencias con CVE críticas (cadena de suministro)
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| SCA en CI (npm audit, OSV, Grype, Trivy) en cada push | detectivo | Implementado | Probado | `evidence/fase-3/sca/` |
| Actualizar dependencias vulnerables | eliminacion | Propuesto | Sin verificar | `docs/fase-5/fase5-contenedores-hardening.md` |

### R21 — Configuración insegura al desplegar la arquitectura cloud (AWS)
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| No desplegar sin aprobación (sin terraform apply, sin .tfstate, sin credenciales AWS) | evitacion | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/06-cloud-no-desplegado.txt` |
| Checkov sobre Terraform (144 passed / 0 failed): verificación ESTÁTICA | preventivo | Implementado | Inspeccionado (configurado, no ejercitado) | `evidence/fase-2/checkov-final/` |
| Servicios gestionados (AWS WAFv2, KMS) y responsabilidad compartida | transferencia | Propuesto | Sin verificar | `infra/terraform/` |

*Nota:* El residual Bajo vale solo mientras no se despliegue; al desplegar, el riesgo vuelve a su valor inherente (12) hasta probar la seguridad en ejecución.

### R22 — Bloqueo del RASP que deja peticiones colgadas o termina el proceso (auto-DoS)
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| Integración rasp-guard: el bloqueo en sqlite3 se entrega como error controlado HTTP 403 (sin --unhandled-rejections=warn) | eliminacion | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/02d-rasp-bloqueo-integrado/estado-contenedor.txt` |
| --unhandled-rejections=warn: evita la caída pero deja la petición sin respuesta (000 tras 20 s); descartado | contencion | Implementado, no efectivo | NO efectivo (probado) | `evidence/fase-6/validacion-2026-11-10/02c-rasp-bloqueo-warn/http.tsv` |

*Nota:* La respuesta 403 la genera el manejador de errores de Juice Shop, que muestra una traza de pila (comportamiento preexistente, A10).

### R23 — Exposición de datos personales (incumplimiento de protección de datos)
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| Bloqueo de la extracción masiva por SQLi (WAF + RASP) | preventivo | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/http.tsv` |
| Póliza de ciberriesgo / cláusulas contractuales (no transfiere la responsabilidad legal del titular) | transferencia | Propuesto | Sin verificar | `docs/fase-6/tratamiento-riesgo.md` |

### R24 — SIEM del laboratorio: privilegio sobre Docker, un solo nodo, Loki sin autenticación
| Control | Tipo | Implementación | Verificación | Evidencia |
|---|---|---|---|---|
| Proxy del socket de Docker de solo lectura (escrituras HTTP 403); Alloy sin root, sin socket, sin capacidades | contencion | Implementado | Probado | `evidence/fase-6/validacion-2026-11-10/05-siem-seguridad/proxy-socket-api.txt` |
| Loki y Grafana publicados solo en 127.0.0.1 | preventivo | Implementado | Inspeccionado (configurado, no ejercitado) | `deploy/hardened/docker-compose.ops.yml` |

## 7. Matriz de calor (Probabilidad × Impacto)
![Comparativo](img/heatmap-comparativo.png)

| Nivel | Inherente | Residual |
|---|---|---|
| Bajo | 0 | 1 |
| Medio | 0 | 7 |
| Alto | 16 | 12 |
| Crítico | 8 | 4 |
| **Total** | 24 | 24 |

Archivos: `img/heatmap-antes.png`, `img/heatmap-despues.png`, `img/heatmap-comparativo.png`, `img/niveles-antes-despues.png`.

## 8. Lectura del residual
- Quedan **4 riesgos críticos** (R03, R06, R20, R23) y **12 altos**. La mayoría depende de
  correcciones de código **diseñadas o propuestas, no desplegadas**, por lo que no reciben reducción.
- Los controles desplegados en esta fase son sobre todo **compensatorios en el perímetro y en ejecución** (WAF, RASP,
  contención): reducen la probabilidad de los vectores probados, no eliminan la causa.
- **R06 (BOLA)** sigue crítico: la lectura cruzada continúa con HTTP 200 a través del WAF. La alerta del SIEM es una
  heurística con falsos positivos demostrados, no una verificación de propietario.
- **R21** es Bajo solo porque la nube **no está desplegada** (evitación probada); eso no valida la seguridad de la infraestructura.
