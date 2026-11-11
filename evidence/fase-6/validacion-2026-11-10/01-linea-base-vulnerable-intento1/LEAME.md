# Intento 1 de la línea base: resultados válidos, registro HTTP vacío

Los resultados de `consola.txt` y `resumen-ataques.md` son válidos (laboratorio vulnerable, 127.0.0.1:3000).
`http.tsv` quedó vacío por un fallo del propio arnés: en Git Bash la ruta `/c/...` no la entiende `curl.exe`
(nativo de Windows). Se corrigió `run.sh` (conversión con `cygpath -m`) y se repitió la corrida en
`../01-linea-base-vulnerable/`. Esta carpeta se conserva sin modificar como registro del intento.
