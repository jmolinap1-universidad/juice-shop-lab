# Parcheo y regresión de la variante corregida (hito A)

**Fecha:** 2026-11-21 · **Rama:** `cierre/hito-a-local` · **Base:** `app/` = OWASP Juice Shop v20.3.0 (`f189f5212`),
que **no se modifica**. La variante corregida se construye a partir de una copia exportada (`app-hardened/build/`,
ignorada por git) y se ejecuta solo en redes Docker internas o en 127.0.0.1.

## 1. Revisión de los parches de diseño (v1) antes de aplicarlos
Los ocho parches de la Fase 6 estaban validados solo con `git apply --check`. Al revisarlos para aplicarlos de verdad
se encontraron defectos que **habrían roto la aplicación o creado una vulnerabilidad nueva**:

| Parche v1 | Defecto encontrado | Consecuencia si se hubiera aplicado tal cual | Tratamiento |
|---|---|---|---|
| 01 (login parametrizado) + 03 (bcrypt) | 03 cambia `hash()` a bcrypt (sal aleatoria), pero 01 sigue comparando `password = :password` en SQL con un hash recién calculado | **Nadie podría iniciar sesión** (el hash nunca coincide) | 01 v2 y 03 v2 |
| 03 (bcrypt) | Usa `bcrypt` sin importarlo; `bcrypt`/`bcryptjs` no están en `package.json` | Error de compilación o en tiempo de ejecución | 03 v2 con `scrypt` nativo de Node (sin dependencias nuevas) |
| 03 (bcrypt) | Cambia `hash()` globalmente, pero `hash()` (MD5) también genera ids de pedido, el hash de correo para Gravatar (que exige MD5) y valores B2B | Rotura de pedidos y avatares | 03 v2 separa `hashPassword`/`verifyPassword` (solo contraseñas) y conserva `hash()` para lo demás |
| 03 (bcrypt) | `changePassword.ts` y `2fa.ts` comparan `security.hash(password)` con el hash guardado | Cambio de contraseña y 2FA rotos | Actualizados para usar `verifyPassword` |
| 04 (clave a variable) | Si no hay variable de entorno, recurre a `encryptionkeys/jwt.key`, un directorio que la app **sirve con listado** | **La clave privada quedaría pública** si se dejaba ese archivo | 04 v2: secreto montado (`JWT_PRIVATE_KEY_FILE`) o variable; si falta, la app **no arranca**; la clave pública se deriva del par rotado |
| 02, 05, 06, 07, 08 | Sin conflictos | — | Aplicados sin cambios |
| (nuevo) 09 | El manejador de errores de Juice Shop devuelve trazas de pila al cliente (también en el 403 del RASP) | Divulgación de información interna (A10:2025) | Manejador sanitizado: estado y mensaje genérico, detalle solo en el log del servidor |

Además, al aplicar los parches se detectó un **éxito falso de la herramienta**: dentro del repositorio del proyecto,
`git apply` interpretaba las rutas del parche 08 (formato `diff --git`) respecto a la raíz del proyecto, **lo omitía
en silencio y devolvía éxito**. Se aisló git de la carpeta superior (`GIT_CEILING_DIRECTORIES`) y se verificó que
cada parche cambiara su archivo. La validación anterior de la Fase 6 no estaba afectada: se hizo desde la raíz del
submódulo `app/`.

## 2. Cómo se aplica (reproducible)
```bash
# 1) exportar app/ con finales LF a dos copias (prístina y de trabajo)
git -c core.autocrlf=false -C app archive --format=tar HEAD | tar -x -C app-hardened/build/orig
git -c core.autocrlf=false -C app archive --format=tar HEAD | tar -x -C app-hardened/build/src
# 2) parches sin conflicto (aislando git del repositorio superior)
export GIT_CEILING_DIRECTORIES="$PWD/app-hardened/build"
cd app-hardened/build/src
for p in 02-sqli-search 05-eval-userprofile 06-asignacion-masiva-registro 07-cors-restringido 08-bola-cesta-propietario; do
  git -c core.autocrlf=false apply -v "../../patches/$p.patch"; done
# 3) correcciones v2 (01, 03, 04) y parche 09: reemplazos literales comprobados (falla si el texto no coincide)
python -I app-hardened/aplicar_v2.py app-hardened/build/src
# 4) construir y generar la clave efímera
docker build -f app-hardened/Dockerfile -t juice-corregida:local app-hardened/build/src
bash security/ops/generar-clave-jwt.sh
```
Diff completo de la variante (9 archivos, clave original redactada): `app-hardened/patches/v2/correcciones-hito-a.patch`.

## 3. Dockerfile de la Fase 5: no construía
El Dockerfile «endurecido» propuesto en la Fase 5 (`app-hardened/Dockerfile`, Hadolint 11→0) **nunca se había
construido**. Construido sin cambios, falla:
`chgrp: cannot access 'frontend/dist/': No such file or directory`
(`evidence/cierre-2026-11-20/01-build/build-dockerfile-fase5-sin-cambios.log`). La causa es `npm install
--ignore-scripts`: Juice Shop compila el frontend y el servidor en el script `postinstall`. Se corrigió quitando
`--ignore-scripts` (los scripts solo corren en la etapa de compilación; la imagen final distroless no ejecuta npm).
Hadolint tras la corrección: 0 avisos (`evidence/cierre-2026-11-20/02-escaneos/hadolint.txt`).

## 4. Resultados

### 4.1 Construcción y arranque
| Prueba | Resultado | Evidencia (`evidence/cierre-2026-11-20/`) |
|---|---|---|
| Construir la variante (`juice-corregida:local`) | Éxito. 158 avisos de tipos de TypeScript, normales en una compilación `--omit=dev`; en los archivos modificados solo `routes/search.ts` TS2339 (`QueryTypes`, del parche 02 original) y avisos previos de `server.ts`. La búsqueda funciona en ejecución (abajo) | `01-build/build-variante-corregida.log` |
| Arrancar SIN el secreto JWT | La app **no arranca** (código 1, «JWT_PRIVATE_KEY_FILE o JWT_PRIVATE_KEY no configurada») | `03-corregida-sin-waf/arranque-sin-secreto.txt` |
| Arrancar con el secreto efímero | `healthy`, 0 reinicios, red interna sin puertos publicados | `03-corregida-sin-waf/regresion-funcional.md` |

### 4.2 Regresión funcional (las funciones legítimas siguen funcionando)
`security/ops/regresion-corregida.sh`, con el código HTTP real de cada paso y los tokens redactados.

| Escenario | Resultado | Notas |
|---|---|---|
| Sin WAF (red Docker interna) | **16 OK / 0 fallas** | Búsqueda con productos, registro, login, cesta propia 200, cesta ajena 403, cambio de contraseña (nueva sí, antigua 401), login del administrador sembrado, token de la clave antigua → **401** (control: 200 en la imagen oficial), error sin traza de pila |
| Con WAF + RASP + SIEM (127.0.0.1:8088) | **15 OK / 0 fallas** (con 13 s entre logins) | La primera ejecución sin pausa dio 3 «fallas» que eran controles del WAF (403 de la regla de asignación masiva; 429 del límite de 5 logins/min); se conserva como `regresion-funcional-sin-pausa.md` |

Almacenamiento de contraseñas (copia de solo lectura de la base del contenedor): **27/27 usuarios con scrypt**, 0 MD5.

### 4.3 Casos de ataque A1-A12 (mismo arnés que las Fases 4 y 6)
| Escenario | Abiertos (VULNERABLE) | Mitigados | Códigos HTTP | Evidencia |
|---|---|---|---|---|
| Corregida sin WAF ni RASP | 6: A4, A5, A6, A9, A10, A11 | A1, A2, A3, A7, A8 y **A12 (403)** | 200, 201, 400, 401; sin 000 ni 5xx | `03-corregida-sin-waf/` |
| Corregida + RASP, saltando el WAF | Los mismos 6 | Los mismos; el RASP bloqueó además el payload de A1 (`sql_injection` en `sqlite3.all`, 403 controlado, sin reinicio) | sin 000 ni 5xx | `05-corregida-rasp-sin-waf/` |
| Corregida + WAF + RASP + SIEM | **0** | **11/11 + A12** | 200, 201, 400, 403; sin 000 ni 5xx | `04-corregida-con-waf/` |

Lectura: el **código corregido** elimina las inyecciones, la asignación masiva, el CORS abierto y el BOLA de cestas
(este último el WAF solo no lo detenía). Los casos A4-A6 y A9-A11 son de **configuración y exposición** de Juice Shop
(listados, `/metrics`, cabeceras, límite de intentos): se cierran en la capa del proxy/WAF, no con estos parches.
Comparativa de los cinco escenarios: `TRAZABILIDAD_STRIDE_DREAD_7_CAPAS.md` §3.

### 4.4 Escaneo de la imagen
Trivy 0.75.0, misma base de datos para ambas imágenes (`02-escaneos/resumen-trivy.md`): CRITICAL 11 → 9, HIGH 33 → 27,
vulnerabilidades únicas 150 → 135; secretos 5 → 3 (desaparece la clave privada de `lib/insecurity.ts` y su compilado; quedan
dos tokens de ejemplo en pruebas del frontend y una clave de ejemplo en `infrastructure/terraform`). Quedan 8 CRITICAL en
dependencias no actualizadas (crypto-js, decompress, jsonwebtoken 0.1.0, lodash 2.4.2, marsdb, tar): R20 sigue aceptado temporalmente.

### 4.5 Efecto en el riesgo
`RIESGO_RESIDUAL_HITO_A.md`: con la variante corregida + defensa, el residual pasa de 4C/12A/7M/1B (v2) a **2C/11A/8M/3B**,
validado por el mismo `riesgo.py` (307 comprobaciones, 0 fallas). El residual del hito A vale **solo para esa
configuración**; la de por defecto (`make ops-up`) conserva el de la Fase 6.

### 4.6 Limitaciones
- **Parche 05 (eval):** aplicado y revisado en el diff, pero no ejercitable en Docker (Juice Shop desactiva esa rama con `safetyMode: auto`).
- **2FA:** usa la nueva verificación de contraseñas, pero no se ejercitó.
- **Error con JSON malformado:** sin WAF la app responde 500 (genérico, sin traza); lo correcto sería 400. Con WAF, ModSecurity responde 400 antes de llegar a la app.
- **Detalle de A1 en el resumen del arnés:** la columna «Detalle» muestra el cuerpo de la respuesta en lugar del código; el código real (401/403) está en `http.tsv`.
- **Imagen con RASP:** se escaneó la variante base (`juice-corregida:local`); la imagen con RASP añade solo el agente Aikido Zen.
- El token de control de la clave antigua se emitió en una instancia temporal de la imagen oficial **solo en la red interna** (sin puertos), detenida al terminar.
