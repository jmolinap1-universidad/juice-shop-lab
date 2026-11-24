# Intento 1 — arnés defectuoso (no es un resultado de la imagen)
Con MSYS_NO_PATHCONV=1, curl.exe de Git Bash no podía usar rutas /tmp/... (cabeceras, credenciales, .curlrc con la cookie):
las baterías corrieron SIN la cookie de acceso y todas recibieron 302 de la puerta. Corregido en validar-cloud.sh (rutas con cygpath -m).
