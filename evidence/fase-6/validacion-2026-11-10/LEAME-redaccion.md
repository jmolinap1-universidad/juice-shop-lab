# Redacción de credenciales en la validación

En la línea base y en el modo monitoreo del RASP, el bypass de autenticación (A1) tuvo éxito y la aplicación
emitió un JWT. Antes de versionar, cada token se reemplazó por `[JWT-REDACTADO]` (regla de no publicar
credenciales; Gitleaks). El resto de la respuesta se conserva como prueba del bypass.

| Archivo | SHA-256 antes de redactar |
|---|---|
| `01-linea-base-vulnerable/a1-sqli-login.json` | `8688f451fb6edfff257b001b276c8fb2e60dc07d21c96593fda0c3f62e1e7497` |
| `01-linea-base-vulnerable-intento1/a1-sqli-login.json` | `54beb3f49a191e1399e1310d015e58a9d7d898b1c8292ceab57da30016589c42` |
| `02a-rasp-monitoreo/a1-sqli-login.json` | `7ffeab3586c607b29b9ba5adbfb09ef703932ee360e594c89148eaab36145664` |
