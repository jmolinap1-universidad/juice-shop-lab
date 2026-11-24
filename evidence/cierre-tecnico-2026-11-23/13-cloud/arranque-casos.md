# Casos de arranque del contenedor cloud — 2026-11-24T00:29:26-06:00
Imagen juice-cloud:local sha256:094b20b960bd0a2c203a3bbb180857a996c1535ccd22d327b8f4548adff4ab17. Solo se registran las líneas de diagnóstico (sin secretos).

## 1. Como Render ahora + JWT_CLAVE_EFIMERA=1 (clave inválida de 72 caracteres presente, 2 entradas)
- estado: running · /healthz: 200 · 14 s
- `acceso: 2 usuario(s) autorizado(s): verificador verificador`
- `AVISO clave JWT: JWT_CLAVE_EFIMERA=1; se ignoran JWT_PRIVATE_KEY_B64/JWT_PRIVATE_KEY`
- `clave JWT: generada en el arranque (efímera, RSA 2048, 1708 bytes, tipo PEM: PRIVATE KEY)`

## 2. Sin clave y sin JWT_CLAVE_EFIMERA (falla cerrada)
- estado: exited · /healthz: 000 · 5 s
- `acceso: 1 usuario(s) autorizado(s): verificador`
- `AVISO clave JWT: ni JWT_PRIVATE_KEY_B64 ni JWT_PRIVATE_KEY están definidas; la app no arrancará (falla cerrada)`
- `FALLO app: Juice Shop terminó (código 1); se detiene el contenedor`

## 3. Clave inválida sin JWT_CLAVE_EFIMERA (estado de Render a las 00:15)
- estado: exited · /healthz: 000 · 1 s
- `acceso: 1 usuario(s) autorizado(s): verificador`
- `FALLO clave JWT: JWT_PRIVATE_KEY_B64 no es base64 válido (72 caracteres)`

## 4. Puerta: una entrada válida y otra no válida
- estado: running · /healthz: 200 · 10 s
- `AVISO acceso: la entrada 2 de BASIC_AUTH_HTPASSWD no es usuario:hash-bcrypt (22 caracteres); se ignora`
- `acceso: 1 usuario(s) autorizado(s): verificador`
- `clave JWT: generada en el arranque (efímera, RSA 2048, 1704 bytes, tipo PEM: PRIVATE KEY)`

## 5. Puerta vacía
- estado: running · /healthz: 200 · 10 s
- `AVISO acceso: ninguna entrada válida en BASIC_AUTH_HTPASSWD; nadie puede entrar (falla cerrada)`
- `clave JWT: generada en el arranque (efímera, RSA 2048, 1704 bytes, tipo PEM: PRIVATE KEY)`

