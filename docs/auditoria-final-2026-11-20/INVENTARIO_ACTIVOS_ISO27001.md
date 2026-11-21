# Inventario de activos (ISO/IEC 27001:2022) — Juice Shop Lab

> Generado por `datos/generar_inventario.py` desde `datos/inventario.json` (validado). Versión descargable: [`INVENTARIO_ACTIVOS_ISO27001.csv`](INVENTARIO_ACTIVOS_ISO27001.csv).

**Alcance:** Laboratorio OWASP Juice Shop v20.3.0 (MASI-UMG 2026): instancia vulnerable local (127.0.0.1), entorno endurecido local (WAF, RASP, SIEM), variante corregida (hito A), repositorio y CI en GitHub, y arquitectura AWS solo DISEÑADA. Inventario con criterios de ISO/IEC 27001:2022 (control 5.9, inventario de información y otros activos asociados).

## 1. Regla de valoración CIA (reproducible)
| Dimensión | Alta (3) | Media (2) | Baja (1) |
|---|---|---|---|
| Confidencialidad | Su divulgación permite suplantar usuarios, causar daño legal o exponer secretos o datos personales | Información interna sin datos personales sensibles | Información pública o sin valor para un atacante |
| Integridad | Su alteración permite fraude, pérdida económica o romper la autenticación o autorización | Su alteración afecta el funcionamiento sin fraude directo | Su alteración tiene efecto cosmético |
| Disponibilidad | Su indisponibilidad detiene la venta o el servicio | Su indisponibilidad degrada el servicio o la operación | Su indisponibilidad no afecta al servicio |

Suma C+I+D: 9 Crítica, 7-8 Alta, 5-6 Media, 3-4 Baja (metodología heredada de la Fase 1).

## 2. Roles
- **PROP**: Líder del proyecto (propietario del activo y dueño del riesgo)
- **DEV**: Desarrollo backend
- **OPS**: Operaciones del laboratorio (administrador de Docker y del host)
- **SEC**: Seguridad de aplicaciones (WAF, RASP, SIEM)
- **DOC**: Documentación y evidencias

Los responsables se expresan por ROL. El equipo asigna la persona de cada rol; esta auditoría no inventa asignaciones.

## 3. Inventario
| ID | Fase 1 | Activo | Tipo | Ubicación | Estado | Proceso | C | I | D | Crit. | Propietario | Custodio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| INF-01 | A01 | Credenciales de usuario | Información | Local | Implementado | Autenticación de clientes | A | A | M | 8 Alta | PROP | DEV |
| INF-02 | A02 | Clave privada JWT y tokens de sesión | Información | Local | Implementado | Emisión y verificación de sesiones | A | A | M | 8 Alta | PROP | OPS |
| INF-03 | A03 | Datos de tarjetas de pago (ficticios) | Información | Local | Implementado | Pago de pedidos | A | A | B | 7 Alta | PROP | DEV |
| INF-04 | A04 | Datos personales (direcciones, teléfono, IP, imagen de perfil) | Información | Local | Implementado | Gestión de cuentas y envíos | A | M | B | 6 Media | PROP | DEV |
| INF-05 | A05 | Respuestas de seguridad | Información | Local | Implementado | Recuperación de cuenta | A | A | B | 7 Alta | PROP | DEV |
| INF-06 | A06 | Monedero y cupones | Información | Local | Implementado | Pagos y promociones | M | A | M | 7 Alta | PROP | DEV |
| INF-07 | A07 | Pedidos y cestas de compra | Información | Local | Implementado | Venta en línea | M | A | M | 7 Alta | PROP | DEV |
| INF-08 | A08 | Contenido de usuarios (reseñas, feedback, quejas, memorias) | Información | Local | Implementado | Interacción con clientes | B | M | B | 4 Baja | PROP | DEV |
| INF-09 | A09 | Catálogo de productos y precios | Información | Local | Implementado | Venta en línea | B | A | A | 7 Alta | PROP | DEV |
| INF-10 | A10 | Documentos internos en /ftp | Información | Local | Implementado | Operación interna de la tienda | A | B | B | 5 Media | PROP | OPS |
| INF-11 | A11 | Registros de acceso de la aplicación | Información | Local | Implementado | Trazabilidad | M | A | M | 7 Alta | PROP | OPS |
| INF-12 | A12 | Métricas Prometheus | Información | Local | Implementado | Monitoreo | M | B | B | 4 Baja | PROP | OPS |
| INF-13 | A13 (parte) | Configuración de la aplicación y secretos de reto | Información | Repositorio | Implementado | Configuración | M | A | M | 7 Alta | PROP | DEV |
| INF-14 | nuevo | Registros de seguridad (WAF y SIEM) | Información | Local | Implementado | Detección y respuesta | M | A | M | 7 Alta | PROP | SEC |
| INF-15 | nuevo | Evidencias del proyecto y bitácora | Información | Repositorio | Implementado | Aseguramiento y entrega académica | M | A | M | 7 Alta | PROP | DOC |
| SW-01 | A13 (parte) | Código fuente de OWASP Juice Shop v20.3.0 | Software | Repositorio | Implementado | Desarrollo | B | A | M | 6 Media | PROP | DEV |
| SW-02 | nuevo | Frontend Angular (SPA) | Software | Local | Implementado | Interfaz de la tienda | B | M | A | 6 Media | PROP | DEV |
| SW-03 | A16 (parte) | API REST Express (backend Node.js) | Software | Local | Implementado | Lógica de negocio | M | A | A | 8 Alta | PROP | DEV |
| SW-04 | nuevo | Base de datos SQLite (motor embebido y archivo) | Software | Local | Implementado | Persistencia | A | A | A | 9 Crítica | PROP | OPS |
| SW-05 | nuevo | MarsDB (NoSQL en memoria) | Software | Local | Implementado | Persistencia de reseñas y pedidos | M | A | M | 7 Alta | PROP | DEV |
| SW-06 | A15 (parte) | Dependencias de terceros (npm) | Software | Repositorio | Implementado | Cadena de suministro | B | A | M | 6 Media | PROP | DEV |
| SW-07 | A14 (parte) | Imagen de contenedor de la aplicación | Software | Local | Implementado | Despliegue | B | A | A | 7 Alta | PROP | OPS |
| SW-08 | nuevo | WAF (Nginx + ModSecurity 3.0.17 + OWASP CRS 4.25.2) | Software | Local | Implementado | Protección perimetral | M | A | A | 8 Alta | PROP | SEC |
| SW-09 | nuevo | RASP (Aikido Zen 1.8.46 + integración rasp-guard) | Software | Local | Implementado | Protección en ejecución | B | A | A | 7 Alta | PROP | SEC |
| SW-10 | nuevo | SIEM (Alloy, Loki, Grafana) y proxy del socket de Docker | Software | Local | Implementado | Detección y monitoreo | M | A | M | 7 Alta | PROP | SEC |
| SW-11 | nuevo | Variante corregida de Juice Shop (parches v2) | Software | Local | Implementado sin publicar | Remediación | B | A | A | 7 Alta | PROP | DEV |
| SRV-01 | A16 | Servicio web de la tienda | Servicios | Local | Implementado | Venta en línea | B | M | A | 6 Media | PROP | OPS |
| SRV-02 | A15 (parte) | GitHub: repositorio y GitHub Actions | Servicios | Cloud | Implementado | Desarrollo y CI/CD | M | A | M | 7 Alta | PROP | DEV |
| SRV-03 | A14 (parte) | Motor de contenedores (Docker Desktop 29.9.2, WSL2) | Servicios | Local | Implementado | Ejecución | M | A | A | 8 Alta | PROP | OPS |
| SRV-04 | nuevo | Registros de imágenes (Docker Hub, gcr.io) | Servicios | Cloud | Implementado | Cadena de suministro | B | A | M | 6 Media | PROP | OPS |
| SRV-05 | nuevo | Infraestructura AWS (VPC, ALB, WAFv2, ECS, KMS, CloudWatch) | Servicios | Cloud | Propuesto, no desplegado | Alojamiento en la nube | A | A | A | 9 Crítica | PROP | OPS |
| HW-01 | nuevo | Estación de trabajo del laboratorio | Físico | Local | Implementado | Infraestructura | M | A | A | 8 Alta | PROP | OPS |
| PER-01 | nuevo | Equipo del proyecto | Personal | Local | Implementado | Gestión del proyecto | M | A | M | 7 Alta | PROP | PROP |
| PER-02 | nuevo | Usuarios finales (cuentas de prueba) | Personal | Local | Implementado | Uso de la tienda | M | M | B | 5 Media | PROP | DEV |
| EMP-01 | nuevo | Reputación y cumplimiento de la tienda (escenario simulado) | Empresa | Local | Implementado | Gobierno | B | A | M | 6 Media | PROP | PROP |

## 4. Descripción, justificación CIA, acceso real y relaciones
### INF-01 — Credenciales de usuario
- **Descripción:** Email, hash de contraseña y totpSecret en la tabla Users. Laboratorio: MD5 sin sal; variante corregida: scrypt con sal.
- **Justificación CIA (A/A/M):** Su robo permite suplantar a cualquier cliente o al administrador (C, I); sin ellas nadie inicia sesión, aunque la tienda sigue mostrando el catálogo (D media).
- **Usuarios con acceso (según configuración):** Proceso Node (uid 65532) del contenedor; cada usuario solo sus datos vía API (en la versión vulnerable, cualquiera mediante SQLi); operadores con acceso a Docker en el host
- **Relación:** Almacenado en SW-04

### INF-02 — Clave privada JWT y tokens de sesión
- **Descripción:** Clave RSA que firma los JWT. Laboratorio: embebida en lib/insecurity.ts. Variante corregida: secreto montado y rotado, fuera del repositorio.
- **Justificación CIA (A/A/M):** Quien la conoce forja sesiones de cualquier usuario (C, I); si falta, no se puede iniciar sesión (D media; en la variante corregida la app no arranca).
- **Usuarios con acceso (según configuración):** Laboratorio: cualquiera con el código fuente (público). Variante corregida: proceso Node vía archivo de secreto de solo lectura; operadores del host
- **Relación:** Usada por SW-03; afecta a INF-01

### INF-03 — Datos de tarjetas de pago (ficticios)
- **Descripción:** fullName, cardNum y fecha de expiración en la tabla Cards (datos de prueba).
- **Justificación CIA (A/A/B):** En un sistema real su divulgación o alteración causa fraude y sanción (C, I); no son necesarias para navegar (D baja).
- **Usuarios con acceso (según configuración):** Titular vía API; en la versión vulnerable, otros usuarios por IDOR de la API automática (no probado sobre Cards)
- **Relación:** Almacenado en SW-04

### INF-04 — Datos personales (direcciones, teléfono, IP, imagen de perfil)
- **Descripción:** Tablas Addresses y Users (lastLoginIp, profileImage).
- **Justificación CIA (A/M/B):** Datos personales protegidos por normativa (C alta); su alteración afecta entregas sin fraude directo (I media).
- **Usuarios con acceso (según configuración):** Titular vía API; proceso Node; operadores del host
- **Relación:** Almacenado en SW-04; base del riesgo R23

### INF-05 — Respuestas de seguridad
- **Descripción:** Tabla SecurityAnswers.
- **Justificación CIA (A/A/B):** Permiten tomar la cuenta mediante el restablecimiento (C, I).
- **Usuarios con acceso (según configuración):** Proceso Node; operadores del host
- **Relación:** Almacenado en SW-04

### INF-06 — Monedero y cupones
- **Descripción:** Saldo (Wallets) y cupones de la cesta.
- **Justificación CIA (M/A/M):** Alterarlos es fraude económico directo (I alta).
- **Usuarios con acceso (según configuración):** Titular vía API; proceso Node
- **Relación:** Almacenado en SW-04

### INF-07 — Pedidos y cestas de compra
- **Descripción:** Baskets y BasketItems (SQLite) y orders (MarsDB).
- **Justificación CIA (M/A/M):** Revelan hábitos de compra (C media); alterarlos es fraude (I alta). Objeto del BOLA (A12).
- **Usuarios con acceso (según configuración):** Titular vía API; en la versión vulnerable también otros usuarios (BOLA demostrado); proceso Node
- **Relación:** Almacenado en SW-04 y SW-05

### INF-08 — Contenido de usuarios (reseñas, feedback, quejas, memorias)
- **Descripción:** MarsDB posts y tablas Feedbacks, Complaints, Memories; archivos subidos.
- **Justificación CIA (B/M/B):** Mayormente público (C baja); su alteración afecta la confianza (I media).
- **Usuarios con acceso (según configuración):** Público en lectura; autores vía API
- **Relación:** Almacenado en SW-04, SW-05 y el sistema de archivos del contenedor

### INF-09 — Catálogo de productos y precios
- **Descripción:** Tablas Products y Deliveries.
- **Justificación CIA (B/A/A):** Público (C baja); alterar precios es fraude (I alta); sin catálogo no hay venta (D alta).
- **Usuarios con acceso (según configuración):** Público en lectura; administrador de la tienda
- **Relación:** Almacenado en SW-04

### INF-10 — Documentos internos en /ftp
- **Descripción:** Archivos de ftp/ (p. ej. acquisitions.md) servidos con listado.
- **Justificación CIA (A/B/B):** Información confidencial de la empresa (C alta).
- **Usuarios con acceso (según configuración):** Laboratorio: cualquiera (listado público); entorno endurecido: bloqueado en el WAF
- **Relación:** Servido por SW-03

### INF-11 — Registros de acceso de la aplicación
- **Descripción:** logs/ de Juice Shop (también expuestos en /support/logs).
- **Justificación CIA (M/A/M):** Contienen IP y rutas (C media); alterarlos borra rastros (I alta).
- **Usuarios con acceso (según configuración):** Proceso Node; laboratorio: cualquiera vía /support/logs; endurecido: tmpfs, bloqueado en el WAF
- **Relación:** Generado por SW-03

### INF-12 — Métricas Prometheus
- **Descripción:** Endpoint /metrics.
- **Justificación CIA (M/B/B):** Revelan detalles internos útiles para reconocimiento (C media).
- **Usuarios con acceso (según configuración):** Laboratorio: público; endurecido: bloqueado en el WAF
- **Relación:** Expuesto por SW-03

### INF-13 — Configuración de la aplicación y secretos de reto
- **Descripción:** config/*.yml, ctf.key y claves HMAC de reto incluidas en el código de Juice Shop.
- **Justificación CIA (M/A/M):** Alterar la configuración cambia el comportamiento de seguridad (I alta).
- **Usuarios con acceso (según configuración):** Público (código abierto de OWASP); proceso Node
- **Relación:** Parte de SW-01

### INF-14 — Registros de seguridad (WAF y SIEM)
- **Descripción:** Audit log y access log JSON del WAF; logs centralizados en Loki.
- **Justificación CIA (M/A/M):** Contienen IP, rutas y cargas de ataque (C media); alterarlos impide detectar incidentes (I alta).
- **Usuarios con acceso (según configuración):** Proceso del WAF (escritura); Alloy (lectura); Loki y Grafana en 127.0.0.1 (usuarios locales del host; Grafana solo lectura anónima)
- **Relación:** Generados por SW-08 y SW-09; centralizados en SW-10

### INF-15 — Evidencias del proyecto y bitácora
- **Descripción:** evidence/, MANIFEST.sha256 y bitacora.md.
- **Justificación CIA (M/A/M):** Su alteración invalida los resultados del proyecto (I alta); contienen datos de laboratorio redactados (C media).
- **Usuarios con acceso (según configuración):** Integrantes con permiso de escritura en GitHub (según configuración del repositorio, no verificada en esta auditoría); lectura según la visibilidad del repositorio
- **Relación:** Versionado en SRV-02

### SW-01 — Código fuente de OWASP Juice Shop v20.3.0
- **Descripción:** Submódulo app/ fijado en el commit f189f5212; no se modifica.
- **Justificación CIA (B/A/M):** Es público (C baja); su integridad define la reproducibilidad del laboratorio (I alta).
- **Usuarios con acceso (según configuración):** Público (OWASP); integrantes del equipo
- **Relación:** Base de SW-02, SW-03 y SW-11

### SW-02 — Frontend Angular (SPA)
- **Descripción:** frontend/dist servido por Express.
- **Justificación CIA (B/M/A):** Sin él los clientes no pueden comprar (D alta); su alteración permite XSS o phishing (I media).
- **Usuarios con acceso (según configuración):** Público en lectura
- **Relación:** Servido por SW-03

### SW-03 — API REST Express (backend Node.js)
- **Descripción:** 109 rutas declaradas en server.ts más la API CRUD automática de 14 modelos.
- **Justificación CIA (M/A/A):** Procesa todas las operaciones (I, D altas); expone información interna en errores (C media).
- **Usuarios con acceso (según configuración):** Público vía HTTP (en el laboratorio solo 127.0.0.1)
- **Relación:** Usa SW-04, SW-05 e INF-02

### SW-04 — Base de datos SQLite (motor embebido y archivo)
- **Descripción:** Motor embebido en el proceso Node; archivo data/juiceshop.sqlite sin cifrado en reposo.
- **Justificación CIA (A/A/A):** Contiene credenciales, datos personales y pedidos (C, I altas); sin ella no hay servicio (D alta).
- **Usuarios con acceso (según configuración):** Solo el proceso Node (no hay servicio de red de base de datos); operadores del host a través de Docker
- **Relación:** Almacena INF-01 a INF-09

### SW-05 — MarsDB (NoSQL en memoria)
- **Descripción:** Colecciones posts y orders en memoria del proceso.
- **Justificación CIA (M/A/M):** Vulnerable a inyección NoSQL (R08) (I alta).
- **Usuarios con acceso (según configuración):** Solo el proceso Node
- **Relación:** Almacena INF-07 e INF-08

### SW-06 — Dependencias de terceros (npm)
- **Descripción:** 2745 componentes en el SBOM; 7 críticas y 20 altas en npm audit (Fase 3).
- **Justificación CIA (B/A/M):** Un componente comprometido o vulnerable altera la aplicación (I alta).
- **Usuarios con acceso (según configuración):** Registro público de npm; build en CI y local
- **Relación:** Incluidas en SW-07; riesgos R04 y R20

### SW-07 — Imagen de contenedor de la aplicación
- **Descripción:** bkimminich/juice-shop:v20.3.0 fijada por digest (laboratorio) y juice-hardened-rasp:local (endurecido).
- **Justificación CIA (B/A/A):** Su alteración ejecuta código arbitrario (I alta); sin imagen no hay servicio (D alta).
- **Usuarios con acceso (según configuración):** Docker Hub (pública); motor Docker del host
- **Relación:** Ejecuta SW-02 a SW-05

### SW-08 — WAF (Nginx + ModSecurity 3.0.17 + OWASP CRS 4.25.2)
- **Descripción:** Único punto de entrada del entorno endurecido (127.0.0.1:8080, o 8088 en la validación).
- **Justificación CIA (M/A/A):** Si se altera o cae, el perímetro queda abierto o sin servicio (I, D altas).
- **Usuarios con acceso (según configuración):** Clientes por HTTP (solo 127.0.0.1); operadores del host
- **Relación:** Protege SW-03; genera INF-14

### SW-09 — RASP (Aikido Zen 1.8.46 + integración rasp-guard)
- **Descripción:** Agente en el proceso Node; sin token no reporta a terceros.
- **Justificación CIA (B/A/A):** Mal integrado provocaba la caída del servicio (R22) (D alta).
- **Usuarios con acceso (según configuración):** Proceso Node
- **Relación:** Protege SW-03 y SW-04

### SW-10 — SIEM (Alloy, Loki, Grafana) y proxy del socket de Docker
- **Descripción:** Un solo nodo; Loki y Grafana en 127.0.0.1; proxy de API de solo lectura.
- **Justificación CIA (M/A/M):** Comprometerlo permite ocultar incidentes (I alta) (R24).
- **Usuarios con acceso (según configuración):** Usuarios locales del host (Grafana anónimo solo lectura; Loki sin autenticación)
- **Relación:** Centraliza INF-14

### SW-11 — Variante corregida de Juice Shop (parches v2)
- **Descripción:** Código de app/ con los parches 02, 05-08 y las correcciones v2 01, 03, 04 y 09 (hito A).
- **Justificación CIA (B/A/A):** Es la versión que elimina causas raíz; su integridad es esencial (I alta).
- **Usuarios con acceso (según configuración):** Integrantes del equipo (local)
- **Relación:** Derivada de SW-01

### SRV-01 — Servicio web de la tienda
- **Descripción:** Disponibilidad del servicio HTTP de Juice Shop (solo 127.0.0.1).
- **Justificación CIA (B/M/A):** Su caída detiene la venta (D alta).
- **Usuarios con acceso (según configuración):** Clientes locales (no expuesto a Internet)
- **Relación:** Prestado por SW-03, SW-07 y SW-08

### SRV-02 — GitHub: repositorio y GitHub Actions
- **Descripción:** Repositorio jmolinap1-universidad/juice-shop-lab y pipeline devsecops.yml (7 jobs).
- **Justificación CIA (M/A/M):** Su alteración compromete código, evidencias y pipeline (I alta).
- **Usuarios con acceso (según configuración):** Cuenta propietaria e integrantes según la configuración de GitHub (no verificada en esta auditoría)
- **Relación:** Versiona SW-01, SW-11 e INF-15

### SRV-03 — Motor de contenedores (Docker Desktop 29.9.2, WSL2)
- **Descripción:** Ejecuta todos los contenedores del laboratorio.
- **Justificación CIA (M/A/A):** Controlarlo equivale a controlar todos los contenedores (I alta); si se detiene, cae todo (D alta).
- **Usuarios con acceso (según configuración):** Usuario del sistema operativo del host; proxy de solo lectura para Alloy
- **Relación:** Ejecuta SW-07 a SW-10

### SRV-04 — Registros de imágenes (Docker Hub, gcr.io)
- **Descripción:** Origen de las imágenes base, fijadas por digest.
- **Justificación CIA (B/A/M):** Una imagen manipulada compromete el entorno; el digest lo mitiga (I alta).
- **Usuarios con acceso (según configuración):** Público (descarga)
- **Relación:** Origen de SW-07 y SW-08

### SRV-05 — Infraestructura AWS (VPC, ALB, WAFv2, ECS, KMS, CloudWatch)
- **Descripción:** Diseño en Terraform validado de forma estática (plan sin conexión y Checkov 144/0).
- **Justificación CIA (A/A/A):** Si se desplegara, alojaría todos los activos (C, I, D altas). Hoy no existe.
- **Usuarios con acceso (según configuración):** Nadie (no desplegado; sin credenciales AWS en el entorno)
- **Relación:** Alojaría SW-03, SW-04 e INF-01 a INF-09

### HW-01 — Estación de trabajo del laboratorio
- **Descripción:** Windows 11 Pro, i3-10100F, 31.9 GB de RAM (evidence/fase-0/diagnostico.txt).
- **Justificación CIA (M/A/A):** Aloja todo el laboratorio y sus evidencias (I, D altas).
- **Usuarios con acceso (según configuración):** Usuario local del equipo
- **Relación:** Aloja SRV-03

### PER-01 — Equipo del proyecto
- **Descripción:** Cuatro integrantes con roles de desarrollo, operaciones, seguridad y documentación.
- **Justificación CIA (M/A/M):** Su conocimiento y sus credenciales sostienen el proyecto; un error humano altera evidencias o expone secretos (I alta).
- **Usuarios con acceso (según configuración):** No aplica
- **Relación:** Opera SRV-02 y SRV-03

### PER-02 — Usuarios finales (cuentas de prueba)
- **Descripción:** Clientes y administrador sembrados por Juice Shop y cuentas creadas en las pruebas, todas ficticias.
- **Justificación CIA (M/M/B):** Son los afectados por la exposición de INF-01 a INF-07.
- **Usuarios con acceso (según configuración):** No aplica
- **Relación:** Titulares de INF-01 a INF-07

### EMP-01 — Reputación y cumplimiento de la tienda (escenario simulado)
- **Descripción:** Confianza de los clientes y obligaciones de protección de datos del escenario.
- **Justificación CIA (B/A/M):** Una brecha afecta la confianza y genera obligaciones legales (I alta) (R23).
- **Usuarios con acceso (según configuración):** No aplica
- **Relación:** Afectado por INF-01 a INF-04

## 5. Resumen
- **35 activos** (los 16 de la Fase 1, todos con correspondencia, más los activos de infraestructura, servicio, personal y organización que la Fase 1 no individualizaba).
- **Por tipo:** Información: 15 · Software: 11 · Servicios: 5 · Personal: 2 · Físico: 1 · Empresa: 1.
- **Por criticidad:** Crítica: 2 · Alta: 22 · Media: 9 · Baja: 2.
- Activo de información frente a activo tecnológico: la información (INF-xx) se valora por sí misma y la columna *Relación* indica el activo tecnológico que la almacena o procesa (SW-xx, SRV-xx), para no contar dos veces el mismo riesgo.
- La nube (SRV-05) figura como **propuesta, no desplegada**: se valora por el impacto que tendría, pero hoy no existe.
