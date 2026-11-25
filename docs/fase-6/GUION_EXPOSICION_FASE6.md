# Guion de exposición — Fase 6: Operaciones, Monitoreo y Ciberseguridad

**Duración:** unos 21 minutos de exposición, más 5 de demostración opcional y preguntas.
**Presentación:** 25 diapositivas (cada una lleva este mismo texto en sus notas del orador).
**Reparto sugerido:** 4 expositores; el equipo decide quién toma cada bloque.

| Bloque | Expositor | Diapositivas | Tiempo |
|---|---|---|---|
| 1. Introducción, reglas y arquitectura | Expositor 1 | 1-6 | 4 min 20 s |
| 2. Código corregido, pruebas, WAF y BOLA | Expositor 2 | 7-12 | 5 min 40 s |
| 3. RASP y SIEM | Expositor 3 | 13-17 | 5 min |
| 4. Riesgo, resultados y conclusión | Expositor 4 | 18-24 | 6 min |
| Demostración y preguntas | Todos | 25 | 5-10 min |

**Consejo general:** hablar de resultados, no de herramientas. Cada número que se diga está en la diapositiva y tiene
evidencia en `evidence/fase-6/cierre-final-2026-11-21/`. Si alguien pregunta «¿cómo lo saben?», señalar la ruta al pie de
la diapositiva.

---

## Bloque 1 — Expositor 1 (4 min 20 s)

### Diapositiva 1 · Portada (30 s)
> «Buenos días. Presentamos la Fase 6 del proyecto: Operaciones, Monitoreo y Ciberseguridad. En las fases anteriores
> identificamos y atacamos las vulnerabilidades de OWASP Juice Shop, una tienda en línea vulnerable a propósito. En esta
> fase respondemos tres preguntas: cómo nos defendemos, cómo vemos lo que ocurre y cuánto riesgo queda después de
> defendernos. Todo lo que vamos a mostrar se ejecutó en nuestro laboratorio local y tiene evidencia guardada en el
> repositorio.»

### Diapositiva 2 · Qué pide la rúbrica (40 s)
> «La rúbrica tiene dos partes. La 6.1 pide una estrategia de mitigación: controles para cada riesgo, un WAF probado contra
> casos del OWASP Top 10, un RASP o monitoreo de API que detecte y responda mientras la aplicación corre, y un SIEM que
> centralice registros, los correlacione y genere alertas. La 6.2 pide el tratamiento formal del riesgo: decidir para cada
> uno de los 24 riesgos si se acepta, elimina, evita, mitiga o transfiere; clasificarlo por tipo e impacto, y mostrar mapas
> de calor antes y después.»

### Diapositiva 3 · Reglas del laboratorio (40 s)
> «Tres reglas guiaron todo. Primera, aislamiento: todo corre en 127.0.0.1 o en redes internas de Docker; nunca publicamos
> la aplicación vulnerable. Segunda, cero resultados inventados: cada número tiene un archivo de evidencia con su hash en un
> manifiesto verificado de 509 archivos. Tercera: si una prueba devuelve un error del servidor, un tiempo agotado o ninguna
> respuesta, no lo contamos como bloqueo. Un servidor caído no es un servidor protegido.»

### Diapositiva 4 · Arquitectura (60 s)
> «Esta es la arquitectura. El usuario, legítimo o atacante, solo puede entrar por el WAF; la aplicación no tiene puerto
> publicado. Detrás está Juice Shop con nuestras correcciones de código y, dentro del mismo proceso, el RASP Aikido Zen. Las
> flechas naranjas indican que el WAF y la aplicación envían sus registros al SIEM: Alloy los recoge, Loki los guarda y
> evalúa las reglas, y Grafana los muestra. La idea es la defensa en profundidad: ninguna capa es perfecta, así que si el
> atacante evade una, la siguiente lo detiene, y todo queda registrado.»

### Diapositiva 5 · Dos configuraciones (45 s)
> «Un hallazgo de esta fase fue que teníamos dos configuraciones fáciles de confundir. La histórica protege la imagen
> oficial vulnerable con WAF y RASP: el código sigue vulnerable. La vigente usa nuestro código corregido. Las separamos por
> completo: comandos, proyecto, volúmenes y registros distintos, y cada script se niega a arrancar si el otro está activo.
> El riesgo residual de 1 crítico solo vale con el código corregido; la histórica conserva sus 4 críticos.»

### Diapositiva 6 · Cómo se levanta (45 s)
> «Primero, `make corregida-build` construye la variante corregida y comprueba que el código es exactamente el diff que
> auditamos; si no coincide, se detiene. Después, `make ops-corregido-up` levanta seis contenedores. En la captura real se
> ve que la aplicación y el WAF están sanos, con cero reinicios, la variante es la corregida y solo hay puertos en
> 127.0.0.1. Usamos el 8088 porque el 8080 estaba ocupado en el equipo.»

**Transición:** «Con la arquitectura clara, pasamos a la primera y más importante capa: el código.»

---

## Bloque 2 — Expositor 2 (5 min 40 s)

### Diapositiva 7 · Diez parches (60 s)
> «Corregir el código elimina la causa. Aplicamos diez parches. El 01 y el 02 hacen las consultas SQL parametrizadas. El 03
> guarda las contraseñas con scrypt y sal en vez de MD5. El 04 saca la clave que firma las sesiones del código: ahora es un
> secreto montado y, si falta, la aplicación no arranca. El 05 elimina `eval`, el 06 impide registrarse como administrador,
> el 07 restringe CORS, el 08 hace que cada usuario solo vea su cesta y el 09 evita mostrar trazas internas en los errores.
> El 10 lo creamos en este cierre, al descubrir que otros objetos seguían expuestos. El código original no se toca:
> trabajamos sobre una copia.»

### Diapositiva 8 · Cuatro escenarios (60 s)
> «Usamos el mismo arnés de doce ataques en cuatro escenarios. A, la imagen original: todos con éxito o expuestos. B, solo
> el código corregido: funciones normales 16 de 16 y solo quedan seis casos, todos de configuración. C añade el RASP
> atacando por dentro de la red: el RASP bloquea la inyección con un 403. D, la defensa completa: cero abiertos. Conclusión:
> el código elimina las vulnerabilidades de lógica y el WAF cierra las de configuración.»

### Diapositiva 9 · Antes y después (40 s)
> «Esta es la salida real del arnés: arriba los doce casos vulnerables, abajo los doce mitigados. Una aclaración de rigor:
> A11, la clave pública JWT servida, es informativo; publicar una clave pública no es una vulnerabilidad. El riesgo real era
> la clave privada en el código, y eso lo eliminó el parche 04.»

### Diapositiva 10 · WAF (50 s)
> «La segunda capa es el WAF: Nginx con ModSecurity y OWASP CRS. Reconoce firmas de ataque —inyección SQL, XSS y rutas de
> archivos—, bloquea rutas sensibles como /ftp o /metrics, limita el login a cinco intentos por minuto y endurece las
> respuestas con cabeceras de seguridad. En la captura, cada familia devuelve 403 y la búsqueda legítima devuelve 200, con
> las reglas exactas registradas. La familia de ejecución de comandos solo la observamos; no la declaramos probada.»

### Diapositiva 11 · Falsos positivos (60 s)
> «También medimos si el WAF bloquea a los clientes. Reprodujimos 35 llamadas de la interfaz real. Con la configuración
> histórica, el WAF bloqueaba 7: cambiar la cantidad en la cesta, quitar un producto, editar una dirección, borrar una
> tarjeta, escribir una reseña y consultar la sesión. Las causas eran dos reglas: una que solo permite GET y POST y otra que
> confunde la palabra *whoami* de la ruta con un comando de Linux. Las corregimos de forma acotada y comprobamos que la
> inyección de comandos en otras rutas se sigue bloqueando. Resultado: 0 de 35.»

### Diapositiva 12 · BOLA (70 s)
> «BOLA es la vulnerabilidad número uno de las API: acceder a un objeto ajeno cambiando un número en la URL. El WAF no puede
> detenerlo, porque la petición es válida; solo el código sabe quién es el dueño. Al ampliar la prueba encontramos que otra
> cuenta aún podía apropiarse de direcciones, cambiar artículos de cestas ajenas y borrar opiniones: seis accesos ajenos.
> Con el parche 10, cero de diez. Y lo más importante: el dueño sigue pudiendo operar sus objetos, siete de siete. Otros
> objetos de la API quedan pendientes de auditar.»

**Transición:** «El código y el WAF protegen la entrada. ¿Y si alguien ya está dentro? Para eso está el RASP.»

---

## Bloque 3 — Expositor 3 (5 min)

### Diapositiva 13 · RASP (60 s)
> «El RASP vive dentro del proceso de Node y ve la consulta SQL real. Lo atacamos desde dentro de la red, saltándonos el WAF.
> En modo monitoreo detectó cinco de cinco inyecciones; la aplicación respondió 401 porque el código ya no es vulnerable. En
> modo bloqueo frenó cinco de cinco con un 403 controlado en unos dos centésimos de segundo; el tráfico legítimo siguió
> respondiendo 200 y el contenedor no se reinició. Lo probamos en la base de datos; sus otras protecciones quedan pendientes.»

### Diapositiva 14 · SIEM (60 s)
> «Proteger no basta: hay que ver lo que ocurre. Alloy recoge tres fuentes: la auditoría del WAF, los accesos y la salida de
> la aplicación con el RASP. Loki guarda y evalúa nueve reglas cada 15 segundos, y Grafana muestra el panel. Esta captura es
> real: peticiones bloqueadas, inyecciones SQL, detecciones del RASP, reglas por familia y respuestas por código HTTP.»

### Diapositiva 15 · Nueve reglas (60 s)
> «Probamos cada regla con un disparador real y seguro: inyección vía WAF, registro con rol de administrador, ocho logins
> seguidos, rutas sensibles, dos usuarios leyendo sus cestas, la cesta de otro, inyección directa a la aplicación y seis
> inserciones rechazadas para provocar errores 500 sin dañar nada. Tras los disparadores, las ocho reglas de ataque pasan a
> *firing*. La novena la probamos aparte.»

### Diapositiva 16 · Indicio frente a prueba (50 s)
> «Aquí fuimos autocríticos. La regla original de BOLA contaba cuántas cestas distintas se leían, y dos clientes normales la
> disparan: falso positivo. No la borramos; la reclasificamos como indicio. Creamos una regla de alta confianza que cuenta
> los 403 a objetos ajenos. La validamos en los dos sentidos: con tráfico legítimo queda inactiva y con el intento cruzado se
> activa.»

### Diapositiva 17 · El monitoreo también se audita (70 s)
> «Auditamos el propio SIEM y encontramos tres problemas. Primero, el token de sesión llegaba a Loki y se veía en Grafana;
> ahora Alloy lo redacta antes de guardarlo: cero visibles. Segundo, al reiniciar la aplicación se perdían eventos; bajamos
> el descubrimiento de 60 a 5 segundos y ahora llegan cinco de cinco. Tercero, no sabíamos si el SIEM dejaba de recibir
> datos: añadimos un latido y una alerta. En la captura, al apagar el colector la alerta pasa a pendiente a los dos minutos,
> se dispara al siguiente y se resuelve al reanudar, sin perder líneas.»

**Transición:** «Con todo esto medido, veamos cuánto riesgo queda y cómo lo tratamos.»

---

## Bloque 4 — Expositor 4 (6 min)

### Diapositiva 18 · Lo que descubrió la validación (40 s)
> «Validar no es solo confirmar que todo funciona. Al probar en serio encontramos cinco problemas reales: accesos a objetos
> ajenos más allá de las cestas, el WAF bloqueando a los clientes, tokens en el SIEM, eventos perdidos y configuraciones
> mezcladas. Los cinco están corregidos y verificados.»

### Diapositiva 19 · Cinco opciones y una regla de oro (60 s)
> «Seguimos ISO/IEC 27005. Para cada uno de los 24 riesgos elegimos una decisión: eliminar, mitigar, evitar, transferir o
> aceptar. Cada riesgo tiene tipo, impacto y responsable. La regla de oro: el riesgo solo baja con un control probado.
> Detectar un ataque no reduce su daño y una póliza solo propuesta no cuenta como transferencia. Un programa lo valida: 324
> comprobaciones, cero fallas.»

### Diapositiva 20 · Mapa de calor (60 s)
> «El mapa se genera desde los datos. A la izquierda, sin controles: 8 críticos y 16 altos. A la derecha, la configuración
> vigente. Las inyecciones SQL, las contraseñas MD5 y el registro como administrador bajaron a probabilidad rara porque
> eliminamos la causa. Fíjense en que el impacto casi no cambia: lo que baja es la probabilidad. Queda un solo crítico: R20,
> las dependencias con vulnerabilidades conocidas.»

### Diapositiva 21 · Tres fotografías (60 s)
> «No mezclamos configuraciones. La histórica llegó a 4 críticos, 12 altos, 7 medios y 1 bajo. El hito A, con el código
> corregido, a 2 críticos. La vigente queda en 1 crítico, 11 altos, 9 medios y 3 bajos. En el cierre solo movimos tres
> riesgos, cada uno con su prueba: BOLA, XSS y datos personales. R20 no lo bajamos.»

### Diapositiva 22 · Riesgos abiertos (50 s)
> «R20 es el único crítico: bibliotecas antiguas con vulnerabilidades conocidas. Actualizarlas sin probar podría romper la
> autenticación, así que lo aceptamos temporalmente con un plan por paquete. Entre los altos están datos personales, que
> requiere probar XXE, NoSQL y SSRF; las bibliotecas JWT; XXE, y la clave JWT, que aún no está en un gestor de secretos.»

### Diapositiva 23 · Lo que no afirmamos (50 s)
> «Nuestro SIEM es de laboratorio: un nodo, sin avisos por correo ni contraseña, aceptable solo porque no sale de
> 127.0.0.1. El RASP está probado en la base de datos. Loki aún guarda tokens antiguos de cuentas de prueba, y borrarlos
> requiere autorización. La nube está preparada pero no desplegada: antes hace falta autorización, OAuth y publicar solo la
> versión corregida con HTTPS y autenticación.»

### Diapositiva 24 · Conclusión (40 s)
> «No decimos que la aplicación sea cien por ciento segura, porque eso no existe. Decimos que cada control está probado y
> cada cifra tiene evidencia. El código elimina la causa, el WAF filtra la entrada, el RASP frena por dentro y el SIEM ve y
> alerta. Pasamos de 8 riesgos críticos a 1, documentado y con plan. Gracias.»

---

## Diapositiva 25 · Demostración y preguntas (todos)

**Demostración de 5 minutos** (`docs/fase-6/GUIA_DEMOSTRACION_FASE6.md`), con el entorno ya levantado antes de empezar:
1. `make ops-corregido-ps`: todo sano, solo 127.0.0.1.
2. Búsqueda legítima → 200; `/ftp` → 403; inyección SQL → 403.
3. `bola-recursos.sh` → 0 vulnerables, 7/7 del propietario.
4. Inyección directa a la app → 403 del RASP, 0 reinicios.
5. Grafana en http://127.0.0.1:3001 y estado de las alertas.

**Plan B si algo falla en vivo:** mostrar la evidencia guardada (las capturas de la presentación son las mismas
salidas). Un 429 en el login es el control de fuerza bruta funcionando: esperar 60 s.

### Preguntas probables y respuesta corta
| Pregunta | Respuesta |
|---|---|
| ¿Por qué no eliminaron R20? | Algunas bibliotecas no tienen versión corregida y otras cambian la autenticación; actualizar sin pruebas rompería la app. Está aceptado temporalmente con plan por paquete. |
| ¿Por qué el WAF no detiene BOLA? | La petición es válida; solo el código sabe quién es el dueño del objeto. Por eso el parche 08/10 está en el código. |
| ¿Qué pasa si evaden el WAF? | El código corregido ya no es vulnerable y el RASP bloquea la inyección dentro del proceso (escenario C). |
| ¿Cómo saben que no hay falsos positivos? | Medimos 35 llamadas legítimas de la interfaz: 0 bloqueadas con la configuración vigente. |
| ¿El SIEM es apto para producción? | No: un nodo, sin autenticación ni avisos. Es de laboratorio y solo escucha en 127.0.0.1. |
| ¿Por qué el impacto no baja en el mapa? | Detectar o filtrar no reduce el daño si el ataque prospera; solo baja la probabilidad. |
| ¿Se puede publicar ya? | Todavía no: falta el hito C (autorización, HTTPS, autenticación, BD administrada) y revisar R20. |

## Cifras clave (chuleta)
- Escenarios: A 12/12 vulnerables o expuestos · B 16/16 funciones, 6 abiertos de configuración · C 15/15 y RASP 403 · D 15/15, **0 abiertos**.
- BOLA fuera de las cestas: **6 → 0** accesos ajenos; **7/7** del propietario.
- WAF: **7/35 → 0/35** falsos positivos; XSS, LFI y SQLi con 403.
- RASP: **5/5** detectados (monitoreo); **5/5** bloqueados con 403 en ~0,02 s; **0** reinicios.
- SIEM: **3** fuentes, **9** reglas, **8** en *firing* con disparadores; alerta de ingesta pending → firing → resuelta.
- Riesgo: **8C/16A → 1C/11A/9M/3B**; **324** comprobaciones, 0 fallas; único crítico **R20**.
- Imagen: CRITICAL 11 → 9, HIGH 33 → 27; clave privada embebida eliminada.
