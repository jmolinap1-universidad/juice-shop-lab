# Laboratorio AppSec – OWASP Juice Shop

Proyecto final del curso **Seguridad en Aplicaciones** (Maestría en Seguridad Informática, UMG, 2026).

Equipo: Molina Pérez Juan Carlos · Sánchez Flores Juan Walter Ernesto · García Gonzalez Leopoldo Emanuel ·
Cambara Castillo Vanessa Odeth. Catedrático: Matthew Alexander Seigne Samayoa.

> ⚠️ `app/` es **OWASP Juice Shop v20.3.0**, una aplicación **intencionalmente vulnerable**. Solo se ejecuta en
> `127.0.0.1` o dentro del job efímero de GitHub Actions. No la exponga a Internet.

## Uso rápido
```bash
git clone --recurse-submodules https://github.com/jmolinap1-universidad/juice-shop-lab.git
make lab-up        # laboratorio vulnerable en http://127.0.0.1:3000
make scan          # SAST/SCA/contenedores/IaC locales vía Docker → evidence/
make attack        # casos de ataque automatizados (Fase 4) → evidence/fase-4/run-<fecha>/
make lab-down
```

Ver `CLAUDE.md` (reglas), `PROGRESO.md`, `DECISIONES.md` y `docs/` (entregables por fase).
