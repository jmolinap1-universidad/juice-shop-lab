# socket.io en la imagen cloud ALPINE — 2026-11-24T23:40:55-06:00
Imagen sha256:272c0dea15a753ed94532e457d0124ded63ea372ffc0a97f79274ea1df63b4ea

| Petición | Esperado | Obtenido |
|---|---|---|
| POST text/plain '40' (legítimo) | 200 | 200 |
| POST text/plain a /api/Feedbacks | 403 | 403 |
| GET /socket.io/ con SQLi en la query | 403 | 403 |
