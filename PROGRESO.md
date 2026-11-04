# Progreso del proyecto

## Etapa actual
Etapa 0 – Preparación del entorno (en curso)

## Completado
- 2026-11-03: carpeta `juice-shop-lab` creada con `CLAUDE.md` (contexto y reglas).
- 2026-11-03: diagnóstico parcial desde Cowork (solo listado de carpetas, sin ejecutar comandos):
  Windows x64, equipo "juanca"; existen las carpetas de programa Git, WSL, Java, Wireshark,
  Npcap, OWASP Threat Dragon y VirtualBox/VMware. **No existe** `C:\Program Files\Docker`
  (Docker Desktop no parece instalado). CPU, RAM, disco y versiones: **sin verificar**.

## Problemas / bloqueos
- Cowork no puede crear sesiones de Claude Code ni ejecutar comandos en este equipo
  (la terminal solo se permite en modo clic). La ejecución técnica la hará Claude Code.

## Siguiente tarea
1. Abrir Claude Code en esta carpeta y ejecutar `scripts/diagnostico.ps1`.
2. Instalar Docker Desktop con WSL2 (requiere administrador; autorización del equipo).
