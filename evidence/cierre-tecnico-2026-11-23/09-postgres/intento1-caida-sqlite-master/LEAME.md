# Intento 1 — caída de la aplicación con PostgreSQL
La primera búsqueda ejecutó `SELECT sql FROM sqlite_master` (comprobación del reto dbSchema); en PostgreSQL la tabla no existe y la promesa sin `catch` terminó el proceso (exit 1). Todas las peticiones siguientes devolvieron 000: NO es una mitigación, es una caída. Corregido en el parche 13 (solo con SQLite y con catch).
