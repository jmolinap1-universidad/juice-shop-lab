# Redacción de credenciales en esta carpeta

`a1-sqli-login.json` contenía el JWT que la aplicación emitió al iniciar sesión mediante la inyección SQL
(modo monitoreo del RASP: el ataque no se bloquea, solo se detecta). El token se reemplazó por
`[JWT-REDACTADO]` antes de versionar (regla de no publicar credenciales; Gitleaks). El resto de la respuesta
(`"authentication"`, `umail`, `bid`) se conserva: prueba que el bypass de autenticación tuvo éxito.

SHA-256 del archivo original antes de redactar: 9ae0c3c26bf9f2857781d585e5dc3581135ff6001f81e766f93c7497054c487f
