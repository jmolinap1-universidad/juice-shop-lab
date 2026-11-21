"""Parche 10 (cierre de la Fase 6): control de acceso a nivel de objeto fuera de las cestas.

Uso: python -I aplicar_fase6.py <directorio con el código exportado y ya corregido por aplicar_v2.py>
Motivo: security/ops/bola-recursos.sh encontró BOLA/IDOR en la variante corregida del hito A (el parche 08 solo cubría
/rest/basket/:id): otra cuenta podía apropiarse de una dirección (PUT /api/Addresss/:id), leer, modificar y borrar
artículos de cestas ajenas (/api/BasketItems/:id), listar los artículos de todas las cestas (GET /api/BasketItems) y
borrar opiniones ajenas (DELETE /api/Feedbacks/:id). Las tarjetas ya filtraban por propietario.
Cada reemplazo es literal y se comprueba: si el texto original no aparece exactamente una vez, el script falla.
"""
import os
import sys

SRC = sys.argv[1]
RUTA = os.path.join(SRC, "server.ts")

ANCLA = "  app.use('/api/Feedbacks/:id', security.isAuthorized())\n"
NUEVO = ANCLA + """  /* Parche 10 (cierre Fase 6): control de acceso a nivel de objeto (BOLA/IDOR, CWE-639 / OWASP API1:2023) en
     articulos de cesta, direcciones y opiniones. Hallado con security/ops/bola-recursos.sh en la variante corregida. */
  const objetoAjeno = (res: Response) => res.status(403).json({ status: 'error', message: 'No autorizado para este recurso' })
  const articuloDeCestaPropia = () => async (req: Request, res: Response, next: NextFunction) => {
    try {
      const usuario = security.authenticatedUsers.from(req)
      const item = await BasketItemModel.findOne({ where: { id: req.params.id } })
      const cambiaDeCesta = req.body?.BasketId !== undefined && Number(req.body.BasketId) !== Number(usuario?.bid)
      if (!usuario?.bid || !item || Number(item.BasketId) !== Number(usuario.bid) || cambiaDeCesta) { objetoAjeno(res); return }
      next()
    } catch (error) { next(error) }
  }
  app.get('/api/BasketItems/:id', articuloDeCestaPropia())
  app.put('/api/BasketItems/:id', articuloDeCestaPropia())
  app.delete('/api/BasketItems/:id', articuloDeCestaPropia())
  app.get('/api/BasketItems', (req: Request, res: Response, next: NextFunction) => {
    const usuario = security.authenticatedUsers.from(req)
    if (usuario?.data?.role !== 'admin') { objetoAjeno(res); return }
    next()
  })
  app.put('/api/Addresss/:id', async (req: Request, res: Response, next: NextFunction) => {
    try {
      const usuario = security.authenticatedUsers.from(req)
      const propia = usuario ? await AddressModel.findOne({ where: { id: req.params.id, UserId: usuario.data.id } }) : null
      if (!propia) { objetoAjeno(res); return }
      next()
    } catch (error) { next(error) }
  })
  app.delete('/api/Feedbacks/:id', async (req: Request, res: Response, next: NextFunction) => {
    try {
      const usuario = security.authenticatedUsers.from(req)
      if (usuario?.data?.role === 'admin') { next(); return }
      const propia = usuario ? await FeedbackModel.findOne({ where: { id: req.params.id, UserId: usuario.data.id } }) : null
      if (!propia) { objetoAjeno(res); return }
      next()
    } catch (error) { next(error) }
  })
"""

texto = open(RUTA, encoding="utf-8").read()
for buscado in (ANCLA, "import type { Request, Response, NextFunction } from 'express'",
                "import { AddressModel } from './models/address'", "import { FeedbackModel } from './models/feedback'",
                "import { BasketItemModel } from './models/basketitem'"):
    n = texto.count(buscado)
    if n != 1:
        raise SystemExit(f"FALLO server.ts: el texto esperado aparece {n} veces: {buscado[:70]!r}")
if "Parche 10 (cierre Fase 6)" in texto:
    raise SystemExit("FALLO server.ts: el parche 10 ya estaba aplicado")
texto = texto.replace(ANCLA, NUEVO)
open(RUTA, "w", encoding="utf-8", newline="\n").write(texto)
print("ok  server.ts (parche 10: BasketItems GET/PUT/DELETE y lista, Addresss PUT, Feedbacks DELETE)")
