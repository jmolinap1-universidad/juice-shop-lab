'use strict'
/*
 * Integración del RASP (Aikido Zen) con la capa de datos — Fase 6, hallazgo R22.
 *
 * Problema verificado: Sequelize ejecuta las consultas SQLite dentro de `conn.serialize(async () => ...)`
 * (node_modules/sequelize/lib/dialects/sqlite/query.js:183). Cuando Zen bloquea, LANZA el error de forma
 * síncrona desde sqlite3.Database#all; esa excepción rechaza la promesa de la función async que
 * `serialize` ignora, de modo que la promesa de la consulta nunca se resuelve: la petición queda colgada y,
 * con la configuración por defecto de Node, el proceso termina por rechazo no manejado.
 *
 * Corrección (sin modificar Juice Shop ni Sequelize): se carga DESPUÉS de @aikidosec/firewall y envuelve los
 * métodos de sqlite3.Database. Solo si el error es un bloqueo de Zen (mensaje "Zen has blocked"):
 *   1. lo entrega por el callback de sqlite3 (la vía de error que Sequelize sí propaga a la ruta);
 *   2. fija HTTP 403 en la respuesta de ESA petición (contexto por AsyncLocalStorage).
 * Cualquier otro error se relanza sin cambios: no se ocultan fallos genéricos.
 */
const { AsyncLocalStorage } = require('node:async_hooks')
const http = require('node:http')

const contexto = new AsyncLocalStorage()
const emitOriginal = http.Server.prototype.emit
http.Server.prototype.emit = function (evento, req, res) {
  if (evento === 'request' && res) {
    return contexto.run({ res }, () => emitOriginal.apply(this, arguments))
  }
  return emitOriginal.apply(this, arguments)
}

const esBloqueoRasp = (e) => e instanceof Error && typeof e.message === 'string' && e.message.startsWith('Zen has blocked')

let sqlite3
try {
  sqlite3 = require('sqlite3')
} catch (e) {
  console.warn('rasp-guard: sqlite3 no disponible; integración no aplicada')
}

if (sqlite3 && sqlite3.Database) {
  let envueltos = 0
  for (const metodo of ['all', 'get', 'run', 'each', 'exec', 'prepare']) {
    const original = sqlite3.Database.prototype[metodo]
    if (typeof original !== 'function') continue
    sqlite3.Database.prototype[metodo] = function (...args) {
      try {
        return original.apply(this, args)
      } catch (err) {
        if (!esBloqueoRasp(err)) throw err
        const ctx = contexto.getStore()
        if (ctx && ctx.res && !ctx.res.headersSent) ctx.res.statusCode = 403
        const controlado = new Error('Solicitud bloqueada por la protección en tiempo de ejecución (RASP)')
        controlado.status = 403
        controlado.code = 'RASP_BLOCKED'
        console.warn(`rasp-guard: bloqueo del RASP en sqlite3.${metodo} entregado como error controlado (HTTP 403)`)
        const callback = args.slice().reverse().find((a) => typeof a === 'function')
        if (callback) {
          process.nextTick(() => callback.call(this, controlado))
          return this
        }
        throw controlado
      }
    }
    envueltos++
  }
  console.log(`rasp-guard: integración activa en ${envueltos} métodos de sqlite3.Database`)
}
