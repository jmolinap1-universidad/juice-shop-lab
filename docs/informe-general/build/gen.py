"""Genera Informe_General_Opcion_B_UMG.docx a partir de las fuentes del repositorio.

Uso (dentro del contenedor python:3.12-slim con python-docx 1.1.2 y Pillow 10.4.0):
  python -I gen.py <raiz_repo> <plantilla_caratula.docx> <salida.docx> fuente1.txt [fuente2.txt ...]

- La carátula y los estilos base se toman del documento institucional de la Fase 6 (plantilla); solo cambia el título.
- Las tablas de datos (inventario, amenazas, riesgos, controles) se leen de los JSON/CSV del repositorio: no se reescriben a mano.
- Marcado de las fuentes: ver LEAME.md de esta carpeta.
"""
import copy
import csv
import json
import math
import re
import sys
from collections import Counter, OrderedDict

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Emu, Pt, RGBColor, Twips
from PIL import Image

RAIZ, PLANTILLA, SALIDA = sys.argv[1], sys.argv[2], sys.argv[3]
FUENTES = sys.argv[4:]
NEGRO = RGBColor(0, 0, 0)
ANCHO_V, ANCHO_H = 9360, 12960          # ancho útil en twips (carta, márgenes de 2,54 cm)
ALTO_V_CM, ALTO_H_CM = 19.0, 12.5        # alto máximo de una figura (deja sitio a número, título y nota)

doc = Document(PLANTILLA)
body = doc.element.body

# ---------------------------------------------------------------- 1. Carátula: se conserva; solo cambia el título
hijos = list(body)
fin_caratula = next(i for i, el in enumerate(hijos)
                    if el.tag == qn('w:p') and el.find(qn('w:pPr')) is not None
                    and el.find(qn('w:pPr')).find(qn('w:sectPr')) is not None)
for el in hijos[fin_caratula + 1:]:
    if el.tag != qn('w:sectPr'):
        body.remove(el)


def texto_parrafo(p):
    return ''.join(t.text or '' for t in p.iter(qn('w:t')))


def reemplazar_texto(p, nuevo):
    ts = list(p.iter(qn('w:t')))
    ts[0].text = nuevo
    for t in ts[1:]:
        t.text = ''


cambios = 0
for p in list(body)[:fin_caratula + 1]:
    if p.tag != qn('w:p'):
        continue
    t = texto_parrafo(p).strip()
    if t == 'FASE 6':
        reemplazar_texto(p, 'INFORME GENERAL – OPCIÓN B'); cambios += 1
    elif t == 'OPERACIONES, MONITOREO Y CIBERSEGURIDAD':
        reemplazar_texto(p, 'CMS / E-COMMERCE WEB ENTERPRISE CLOUD-NATIVE'); cambios += 1
assert cambios == 2, 'La carátula no tiene los textos esperados'

# Sección del cuerpo: carta, márgenes de 2,54 cm
sec = doc.sections[-1]
sec.page_width, sec.page_height = Twips(12240), Twips(15840)
for m in ('top_margin', 'bottom_margin', 'left_margin', 'right_margin'):
    setattr(sec, m, Twips(1440))
sec.header_distance = sec.footer_distance = Twips(708)

# ---------------------------------------------------------------- 2. Estilos (Arial 12, negro, 1.5, sangría 1,27 cm)
st = doc.styles


def fuente_arial(rpr_owner_el):
    rpr = rpr_owner_el.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rpr.insert(0, rf)
    for a in list(rf.attrib):
        del rf.attrib[a]
    for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
        rf.set(qn(a), 'Arial')


def ajustar(estilo, *, negrita=None, cursiva=None, alin=None, linea=1.5, primera=None, izq=None, colgante=None,
            antes=0, despues=0, sig=None, juntas=None, tam=12):
    estilo.font.size = Pt(tam)
    estilo.font.color.rgb = NEGRO
    if negrita is not None:
        estilo.font.bold = negrita
    if cursiva is not None:
        estilo.font.italic = cursiva
    fuente_arial(estilo.element)
    pf = estilo.paragraph_format
    pf.line_spacing = linea
    pf.space_before, pf.space_after = Pt(antes), Pt(despues)
    if alin is not None:
        pf.alignment = alin
    if primera is not None:
        pf.first_line_indent = primera
    if izq is not None:
        pf.left_indent = izq
    if colgante is not None:
        pf.first_line_indent = -colgante
    if sig is not None:
        pf.keep_with_next = sig
    if juntas is not None:
        pf.keep_together = juntas
    pf.widow_control = True


# valores por defecto del documento
rpr_def = doc.styles.element.find(qn('w:docDefaults')).find(qn('w:rPrDefault')).find(qn('w:rPr'))
rf = rpr_def.find(qn('w:rFonts'))
for a in list(rf.attrib):
    del rf.attrib[a]
for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
    rf.set(qn(a), 'Arial')
for tag in ('w:sz', 'w:szCs'):
    rpr_def.find(qn(tag)).set(qn('w:val'), '24')

J, I, C = WD_ALIGN_PARAGRAPH.JUSTIFY, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER
ajustar(st['Normal'], alin=J, primera=Cm(1.27))
for nombre in ('APA Body',):
    if nombre in [s.name for s in st]:
        ajustar(st[nombre], alin=J, primera=Cm(1.27))
ajustar(st['Heading 1'], negrita=True, cursiva=False, alin=C, primera=Cm(0), antes=12, despues=12, sig=True, juntas=True)
ajustar(st['Heading 2'], negrita=True, cursiva=False, alin=I, primera=Cm(0), antes=12, despues=6, sig=True, juntas=True)
ajustar(st['Heading 3'], negrita=True, cursiva=True, alin=I, primera=Cm(0), antes=6, despues=6, sig=True, juntas=True)
for h in ('Heading 1', 'Heading 2', 'Heading 3'):
    rpr = st[h].element.get_or_add_rPr()
    for tag in ('w:szCs',):
        e = rpr.find(qn(tag))
        if e is not None:
            e.set(qn('w:val'), '24')
    col = rpr.find(qn('w:color'))
    if col is not None:
        for a in ('w:themeColor', 'w:themeShade', 'w:themeTint'):
            col.attrib.pop(qn(a), None)
st['Heading 3'].element.get_or_add_pPr()   # el estilo 3 venía semioculto
for e in st['Heading 3'].element.findall(qn('w:semiHidden')):
    st['Heading 3'].element.remove(e)
if 'Hyperlink' in [s.name for s in st]:
    st['Hyperlink'].font.color.rgb = NEGRO


def estilo_toc(nombre, nivel):
    try:
        s = st[nombre]
    except KeyError:
        s = st.add_style(nombre, WD_STYLE_TYPE.PARAGRAPH)
        s.element.attrib.pop(qn('w:customStyle'), None)
        s.base_style = st['Normal']
    ajustar(s, alin=I, primera=Cm(0), izq=Cm(0.63 * (nivel - 1)), linea=1.15, despues=4)
    # tabulación derecha con puntos al margen
    pPr = s.element.get_or_add_pPr()
    for t in pPr.findall(qn('w:tabs')):
        pPr.remove(t)
    tabs = OxmlElement('w:tabs'); tab = OxmlElement('w:tab')
    tab.set(qn('w:val'), 'right'); tab.set(qn('w:leader'), 'dot'); tab.set(qn('w:pos'), str(ANCHO_V))
    tabs.append(tab); pPr.insert(0, tabs)
    orden_ppr(pPr)


ORDEN_PPR = ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl', 'numPr', 'suppressLineNumbers',
             'pBdr', 'shd', 'tabs', 'suppressAutoHyphens', 'kinsoku', 'wordWrap', 'overflowPunct', 'topLinePunct', 'autoSpaceDE',
             'autoSpaceDN', 'bidi', 'adjustRightInd', 'snapToGrid', 'spacing', 'ind', 'contextualSpacing', 'mirrorIndents',
             'suppressOverlap', 'jc', 'textDirection', 'textAlignment', 'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle',
             'rPr', 'sectPr', 'pPrChange']


def orden_ppr(pPr):
    hijos = list(pPr)
    hijos.sort(key=lambda e: ORDEN_PPR.index(e.tag.split('}')[1]) if e.tag.split('}')[1] in ORDEN_PPR else 99)
    for e in hijos:
        pPr.remove(e)
    for e in hijos:
        pPr.append(e)


for n, nombre in enumerate(('toc 1', 'toc 2', 'toc 3'), 1):
    estilo_toc(nombre, n)


def nuevo(nombre, **kw):
    s = st.add_style(nombre, WD_STYLE_TYPE.PARAGRAPH)
    s.base_style = st['Normal']
    ajustar(s, **kw)
    return s


nuevo('Celda', alin=I, primera=Cm(0), linea=1.0)
nuevo('CeldaEnc', alin=I, primera=Cm(0), linea=1.0, negrita=True)
nuevo('EtiquetaNum', alin=I, primera=Cm(0), negrita=True, sig=True, antes=6)
nuevo('TituloObjeto', alin=I, primera=Cm(0), cursiva=True, sig=True, despues=6)
nuevo('NotaObjeto', alin=J, primera=Cm(0), despues=10)
nuevo('Imagen', alin=C, primera=Cm(0), linea=1.0, sig=True)
nuevo('Vineta', alin=J, primera=Cm(0))
nuevo('Referencia', alin=I, izq=Cm(1.27), colgante=Cm(1.27))
nuevo('Codigo', alin=I, primera=Cm(0), linea=1.0, despues=6)
nuevo('TituloIndice', alin=C, primera=Cm(0), negrita=True, despues=12)

# ---------------------------------------------------------------- 3. Listas (viñetas y numeradas)
numbering = doc.part.numbering_part.element


def abstract(id_, fmt, texto):
    a = OxmlElement('w:abstractNum'); a.set(qn('w:abstractNumId'), str(id_))
    m = OxmlElement('w:multiLevelType'); m.set(qn('w:val'), 'singleLevel'); a.append(m)
    lvl = OxmlElement('w:lvl'); lvl.set(qn('w:ilvl'), '0')
    for tag, val in (('w:start', '1'), ('w:numFmt', fmt), ('w:lvlText', texto), ('w:lvlJc', 'left')):
        e = OxmlElement(tag); e.set(qn('w:val'), val); lvl.append(e)
    ppr = OxmlElement('w:pPr'); ind = OxmlElement('w:ind')
    ind.set(qn('w:left'), '720'); ind.set(qn('w:hanging'), '360'); ppr.append(ind); lvl.append(ppr)
    rpr = OxmlElement('w:rPr'); rfo = OxmlElement('w:rFonts')
    for at in ('w:ascii', 'w:hAnsi', 'w:cs'):
        rfo.set(qn(at), 'Arial')
    rpr.append(rfo); lvl.append(rpr)
    a.append(lvl)
    primero_num = numbering.find(qn('w:num'))
    if primero_num is not None:
        primero_num.addprevious(a)
    else:
        numbering.append(a)


abstract(901, 'bullet', '•')
abstract(902, 'decimal', '%1.')
_num_id = [900]


def nueva_lista(abs_id):
    _num_id[0] += 1
    n = OxmlElement('w:num'); n.set(qn('w:numId'), str(_num_id[0]))
    an = OxmlElement('w:abstractNumId'); an.set(qn('w:val'), str(abs_id)); n.append(an)
    lo = OxmlElement('w:lvlOverride'); lo.set(qn('w:ilvl'), '0')
    so = OxmlElement('w:startOverride'); so.set(qn('w:val'), '1'); lo.append(so); n.append(lo)
    numbering.append(n)
    return _num_id[0]


def aplicar_lista(p, num_id):
    pPr = p._p.get_or_add_pPr()
    numPr = OxmlElement('w:numPr')
    il = OxmlElement('w:ilvl'); il.set(qn('w:val'), '0')
    ni = OxmlElement('w:numId'); ni.set(qn('w:val'), str(num_id))
    numPr.append(il); numPr.append(ni); pPr.append(numPr)
    orden_ppr(pPr)


# ---------------------------------------------------------------- 4. Datos del repositorio
def leer_json(r):
    with open(f'{RAIZ}/{r}', encoding='utf-8') as f:
        return json.load(f)


RIESGOS = leer_json('docs/fase-6/riesgo-cierre-brechas/riesgos-calculados.json')
TRAZ = leer_json('docs/auditoria-final-2026-11-20/datos/trazabilidad.json')
with open(f'{RAIZ}/docs/auditoria-final-2026-11-20/INVENTARIO_ACTIVOS_ISO27001.csv', encoding='utf-8-sig') as f:
    INVENTARIO = list(csv.DictReader(f))
ROLES = OrderedDict([('Líder del proyecto', 'PROP'), ('Desarrollo backend', 'DEV'), ('Operaciones del laboratorio', 'OPS'),
                     ('Seguridad de aplicaciones', 'SEC'), ('Documentación y evidencias', 'DOC')])


def rol(t):
    for k, v in ROLES.items():
        if t.startswith(k):
            return v
    return t


NIVEL = {'A': 3, 'M': 2, 'B': 1}


def nivel(p, i):
    s = p * i
    return 'Crítico' if s >= 20 else 'Alto' if s >= 10 else 'Medio' if s >= 5 else 'Bajo'


def dread_prom(v):
    return round(sum(v) / 5, 1)


def dread_nivel(x):
    return 'Crítico' if x >= 8 else 'Alto' if x >= 6 else 'Medio' if x >= 4 else 'Bajo'


def leer_tablas_md(ruta):
    tablas, actual = [], []
    with open(f'{RAIZ}/{ruta}', encoding='utf-8') as f:
        for ln in f:
            if ln.startswith('|'):
                actual.append(ln.rstrip('\n'))
            elif actual:
                tablas.append(actual); actual = []
    if actual:
        tablas.append(actual)
    return [[celdas(l) for l in t if not re.match(r'^\|[\s:|-]+\|\s*$', l)] for t in tablas]


def celdas(linea):
    s = linea.strip()[1:-1] if linea.strip().endswith('|') else linea.strip()[1:]
    partes = re.split(r'(?<!\\)\|', s)
    return [p.strip().replace('\\|', '|') for p in partes]


def datos(nombre):
    """Devuelve (encabezados, filas, anchos) de una tabla de datos."""
    rs = RIESGOS['riesgos']
    if nombre == 'inventario':
        enc = ['ID', 'Activo', 'Tipo', 'Ubicación', 'C', 'I', 'D', 'Criticidad', 'Propietario', 'Custodio']
        filas = [[a['ID'], a['Nombre'], a['Tipo'], a['Ubicación'], a['C'], a['I'], a['D'],
                  f"{a['Criticidad']} ({a['Total']})", rol(a['Propietario (rol)']), rol(a['Custodio (rol)'])] for a in INVENTARIO]
        return enc, filas, [1.9, 5.3, 2.8, 2.8, 0.8, 0.8, 0.8, 2.9, 2.7, 2.2]
    if nombre == 'inventario_detalle':
        enc = ['ID', 'Estado', 'Proceso que soporta', 'Descripción', 'Usuarios con acceso (según configuración)', 'Relación']
        filas = [[a['ID'], a['Estado'], a['Proceso'], a['Descripción'], a['Usuarios con acceso'], a['Relación']] for a in INVENTARIO]
        return enc, filas, [1.9, 2.9, 3.0, 5.4, 5.6, 3.0]
    if nombre == 'inventario_cia':
        enc = ['ID', 'Activo', 'C-I-D', 'Justificación de la valoración CIA']
        filas = [[a['ID'], a['Nombre'], f"{a['C']}-{a['I']}-{a['D']} ({a['Total']})", a['Justificación CIA']] for a in INVENTARIO]
        return enc, filas, [1.9, 3.9, 1.6, 11.2]
    if nombre == 'inventario_resumen':
        tipos = Counter(a['Tipo'] for a in INVENTARIO)
        crit = Counter(a['Criticidad'] for a in INVENTARIO)
        enc = ['Tipo de activo', 'Activos', 'Crítica', 'Alta', 'Media', 'Baja']
        filas = []
        for t in tipos:
            c = Counter(a['Criticidad'] for a in INVENTARIO if a['Tipo'] == t)
            filas.append([t, str(tipos[t]), str(c['Crítica']), str(c['Alta']), str(c['Media']), str(c['Baja'])])
        filas.append(['**Total**', f"**{len(INVENTARIO)}**", f"**{crit['Crítica']}**", f"**{crit['Alta']}**",
                      f"**{crit['Media']}**", f"**{crit['Baja']}**"])
        return enc, filas, [5.0, 2.0, 2.0, 2.0, 2.0, 2.0]
    if nombre == 'stride_clases':
        tab = leer_tablas_md('docs/auditoria-final-2026-11-20/TRAZABILIDAD_STRIDE_DREAD_7_CAPAS.md')[0]
        nube = Counter()
        for tc in TRAZ['amenazas_cloud']:
            for l in tc['stride'].split(','):
                nube[l.strip()] += 1
        enc = ['Clase STRIDE', 'Amenazas de la aplicación (T01-T20)', 'N.º', 'Amenazas cloud (TC01-TC10)', 'N.º']
        filas = []
        for f in tab[1:]:
            letra = f[0].split('·')[0].strip()
            ids = [tc['id'] for tc in TRAZ['amenazas_cloud'] if letra in [x.strip() for x in tc['stride'].split(',')]]
            filas.append([f[0], f[1], f[2], ', '.join(ids), str(nube[letra])])
        return enc, filas, [3.6, 5.2, 1.1, 5.2, 1.2]
    if nombre == 'dread_app':
        tab = leer_tablas_md('docs/auditoria-final-2026-11-20/TRAZABILIDAD_STRIDE_DREAD_7_CAPAS.md')[1]
        enc = ['ID', 'Elemento', 'STRIDE', 'Amenaza (riesgo)', 'D', 'R', 'E', 'A', 'Di', 'Prom.', 'Nivel']
        filas = [f for f in tab[1:]]
        return enc, filas, [1.3, 3.4, 2.0, 7.6, 1.0, 1.0, 1.0, 1.0, 1.0, 1.5, 1.9]
    if nombre == 'dread_cloud':
        enc = ['ID', 'Elemento', 'STRIDE', 'Amenaza', 'D', 'R', 'E', 'A', 'Di', 'Prom.', 'Nivel', 'Riesgo']
        filas = []
        for tc in TRAZ['amenazas_cloud']:
            pr = dread_prom(tc['dread'])
            filas.append([tc['id'], tc['elemento'], tc['stride'], tc['amenaza'], *[str(x) for x in tc['dread']],
                          f'{pr:.1f}', dread_nivel(pr), tc['riesgo']])
        return enc, filas, [1.5, 3.6, 2.0, 6.4, 1.0, 1.0, 1.0, 1.0, 1.0, 1.5, 1.8, 1.9]
    if nombre == 'stride_cloud_control':
        enc = ['ID', 'Control aplicado', 'Evidencia']
        filas = [[tc['id'], tc['control'], f"`{tc['evidencia']}`"] for tc in TRAZ['amenazas_cloud']]
        return enc, filas, [1.3, 7.6, 7.6]
    if nombre == 'riesgo_registro':
        enc = ['ID', 'Riesgo', 'Origen', 'Tipo', 'Impactos (principal primero)', 'OWASP 2025', 'CWE']
        filas = [[r['id'], r['nombre'], r['origen'], r['tipo'], ', '.join(r['impactos']), r['owasp'], r['cwe']] for r in rs]
        return enc, filas, [1.3, 6.6, 2.6, 3.2, 3.7, 2.4, 2.4]
    if nombre == 'riesgo_inherente':
        enc = ['ID', 'Riesgo', 'Fuente', 'P', 'I', 'P×I', 'Nivel inherente']
        filas = [[r['id'], r['nombre'], r['fuente_pi'], str(r['P_inh']), str(r['I_inh']), str(r['S_inh']), r['N_inh']] for r in rs]
        return enc, filas, [1.3, 7.6, 2.4, 0.8, 0.8, 1.3, 2.4]
    if nombre == 'riesgo_decisiones':
        enc = ['ID', 'Inherente', 'Decisión principal (estado)', 'Complementaria (estado)', 'Residual', 'Responsable (rol)']
        filas = []
        for r in rs:
            comp = f"{r['decision_sec']} ({r['decision_sec_estado']})" if r['decision_sec'] else '—'
            filas.append([r['id'], f"{r['P_inh']}×{r['I_inh']}={r['S_inh']} {r['N_inh']}",
                          f"**{r['decision']}** ({r['estado_tratamiento']})", comp,
                          f"{r['P_res']}×{r['I_res']}={r['S_res']} **{r['N_res']}**", r['responsable']])
        return enc, filas, [1.1, 2.9, 3.6, 3.5, 2.9, 7.0]
    if nombre == 'riesgo_justificacion':
        enc = ['ID', 'Inherente y residual', 'Razón de la probabilidad (P)', 'Razón del impacto (I)', 'Actividad pendiente']
        filas = [[r['id'], f"{r['P_inh']}×{r['I_inh']} → {r['P_res']}×{r['I_res']}", r['razon_P'], r['razon_I'],
                  r['pendiente'] or '—'] for r in rs]
        return enc, filas, [1.3, 2.6, 6.4, 3.7, 4.6]
    if nombre == 'riesgo_distribucion':
        d = RIESGOS['distribucion']
        enc = ['Nivel', 'Inherente', 'Residual']
        filas = [[n, str(a), str(b)] for n, a, b in zip(d['niveles'], d['inherente'], d['residual'])]
        filas.append(['**Total**', f"**{sum(d['inherente'])}**", f"**{sum(d['residual'])}**"])
        return enc, filas, [5.0, 4.0, 4.0]
    if nombre == 'decisiones_resumen':
        enc = ['Decisión', 'Como principal', 'Como complementaria', 'Estados registrados']
        filas = []
        for d in ('Aceptar', 'Eliminar', 'Evitar', 'Mitigar', 'Transferir'):
            p = [r for r in rs if r['decision'] == d]
            c = [r for r in rs if r['decision_sec'] == d]
            est = Counter([r['estado_tratamiento'] for r in p] + [r['decision_sec_estado'] for r in c])
            filas.append([d, f"{len(p)} ({', '.join(r['id'] for r in p) or '—'})",
                          f"{len(c)} ({', '.join(r['id'] for r in c) or '—'})",
                          '; '.join(f'{k}: {v}' for k, v in est.items()) or '—'])
        return enc, filas, [2.4, 5.0, 5.0, 4.1]
    if nombre == 'tipos_impactos':
        tipos = Counter(r['tipo'] for r in rs)
        imp = Counter(i for r in rs for i in r['impactos'])
        enc = ['Tipo de riesgo', 'Riesgos', 'IDs']
        filas = [[t, str(n), ', '.join(r['id'] for r in rs if r['tipo'] == t)] for t, n in tipos.most_common()]
        enc2 = ['Impacto', 'Riesgos que lo incluyen', 'Como impacto principal']
        filas2 = [[i, str(n), str(sum(1 for r in rs if r['impactos'][0] == i))] for i, n in imp.most_common()]
        return enc, filas, [4.0, 2.0, 10.5], enc2, filas2
    if nombre == 'capas':
        capas = TRAZ['capas']; rc = TRAZ['riesgo_capa']
        porid = {r['id']: r for r in rs}
        enc = ['Capa', 'Riesgos asignados (principal o secundaria)', 'Máximo inherente', 'Máximo residual']
        filas = []
        for k, nombre_c in capas.items():
            ids = [rid for rid, cs in rc.items() if k in [c for c in cs if c]]
            if ids:
                mi = max(ids, key=lambda x: porid[x]['S_inh']); mr = max(ids, key=lambda x: porid[x]['S_res'])
                filas.append([f'{k} {nombre_c}', ', '.join(ids),
                              f"{porid[mi]['S_inh']} {porid[mi]['N_inh']} ({mi})", f"{porid[mr]['S_res']} {porid[mr]['N_res']} ({mr})"])
            else:
                filas.append([f'{k} {nombre_c}', '—', 'Sin riesgo del registro', 'Ver nota'])
        return enc, filas, [5.2, 5.6, 2.9, 2.8]
    if nombre == 'controles':
        enc = ['Riesgo', 'Control', 'Tipo', 'Verificación', 'Evidencia']
        filas = []
        for r in rs:
            for c in r['controles']:
                filas.append([r['id'], c['control'], c['tipo'], f"{c['estado']} / {c['verificacion']}",
                              f"`{c['evidencia']}`"])
        return enc, filas, [1.6, 8.0, 2.7, 3.0, 7.4]
    if nombre == 'controles_resumen':
        enc = ['Tipo de control', 'Probado', 'Inspeccionado', 'Propuesto / sin verificar', 'No efectivo', 'Total']
        cont = Counter((c['tipo'], c['verificacion']) for r in rs for c in r['controles'])
        filas = []
        for t in sorted({c['tipo'] for r in rs for c in r['controles']}):
            v = [cont[(t, x)] for x in ('probado', 'inspeccionado', 'sin_verificar', 'no_efectivo')]
            filas.append([t, *map(str, v), str(sum(v))])
        tot = [sum(cont[(t, x)] for t in {c['tipo'] for r in rs for c in r['controles']})
               for x in ('probado', 'inspeccionado', 'sin_verificar', 'no_efectivo')]
        filas.append(['**Total**', *[f'**{x}**' for x in tot], f'**{sum(tot)}**'])
        return enc, filas, [3.6, 2.4, 2.8, 3.6, 2.2, 1.9]
    if nombre == 'casos':
        tab = leer_tablas_md('docs/auditoria-final-2026-11-20/TRAZABILIDAD_STRIDE_DREAD_7_CAPAS.md')[2]
        enc = ['Caso', 'Prueba', 'Clase', 'Vulnerable', 'Vuln. + WAF/RASP', 'Corregida sin WAF', 'Corregida + WAF/RASP',
               'Imagen cloud (local)', 'Render']
        abrev = {'VULNERABLE': 'VULN.', 'MITIGADO': 'Mitig.'}
        filas = [[f[0], f[1], f[2], *[abrev.get(x, x) for x in (f[5], f[6], f[7], f[9], f[10], f[11])]] for f in tab[1:]]
        return enc, filas, [1.3, 5.0, 1.4, 2.5, 2.6, 2.5, 2.6, 2.4, 1.9]
    raise KeyError(nombre)


# ---------------------------------------------------------------- 5. Utilidades de escritura
INLINE = re.compile(r'(\*\*.+?\*\*|(?<![\w*])\*[^*\s][^*]*?\*(?![\w*])|`[^`]+`|\{[TF]:[\w-]+\})')
NUM = {}   # id -> 'Tabla n' / 'Figura n'


def escribir(p, texto, negrita=False, cursiva=False):
    for parte in INLINE.split(texto):
        if not parte:
            continue
        b, i, t = negrita, cursiva, parte
        if parte.startswith('**') and parte.endswith('**') and len(parte) > 4:
            b, t = True, parte[2:-2]
        elif parte.startswith('`') and parte.endswith('`'):
            t = parte[1:-1]
        elif re.fullmatch(r'\{[TF]:[\w-]+\}', parte):
            clave = parte[3:-1]
            if clave not in NUM:
                raise KeyError(f'Referencia sin destino: {parte}')
            t = NUM[clave]
        elif parte.startswith('*') and parte.endswith('*') and len(parte) > 2:
            i, t = True, parte[1:-1]
        r = p.add_run(t)
        r.bold = b or None
        r.italic = i or None


def parrafo(texto, estilo='Normal', **kw):
    p = doc.add_paragraph(style=estilo)
    escribir(p, texto, **kw)
    return p


def borde(tag, val='single', sz=8, color='000000'):
    e = OxmlElement(tag)
    e.set(qn('w:val'), val); e.set(qn('w:sz'), str(sz)); e.set(qn('w:space'), '0'); e.set(qn('w:color'), color)
    return e


def tabla(enc, filas, anchos, horizontal):
    total = ANCHO_H if horizontal else ANCHO_V
    s = sum(anchos)
    tw = [int(total * a / s) for a in anchos]
    tw[-1] += total - sum(tw)
    t = doc.add_table(rows=len(filas) + 1, cols=len(enc))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl = t._tbl
    tblPr = tbl.tblPr
    for e in tblPr.findall(qn('w:tblStyle')):
        tblPr.remove(e)
    w = OxmlElement('w:tblW'); w.set(qn('w:w'), str(total)); w.set(qn('w:type'), 'dxa'); tblPr.append(w)
    b = OxmlElement('w:tblBorders')
    b.append(borde('w:top', sz=12)); b.append(borde('w:left', 'nil', 0)); b.append(borde('w:bottom', sz=12))
    b.append(borde('w:right', 'nil', 0)); b.append(borde('w:insideH', sz=2, color='A6A6A6')); b.append(borde('w:insideV', 'nil', 0))
    tblPr.append(b)
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); tblPr.append(lay)
    mar = OxmlElement('w:tblCellMar')
    for lado, v in (('top', 30), ('left', 55), ('bottom', 30), ('right', 55)):
        e = OxmlElement(f'w:{lado}'); e.set(qn('w:w'), str(v)); e.set(qn('w:type'), 'dxa'); mar.append(e)
    tblPr.append(mar)
    orden = ['tblStyle', 'tblpPr', 'tblOverlap', 'bidiVisual', 'tblStyleRowBandSize', 'tblStyleColBandSize', 'tblW', 'jc',
             'tblCellSpacing', 'tblInd', 'tblBorders', 'shd', 'tblLayout', 'tblCellMar', 'tblLook']
    hijos = sorted(list(tblPr), key=lambda e: orden.index(e.tag.split('}')[1]) if e.tag.split('}')[1] in orden else 99)
    for e in hijos:
        tblPr.remove(e)
    for e in hijos:
        tblPr.append(e)
    grid = tbl.tblGrid
    for gc, ancho in zip(grid.findall(qn('w:gridCol')), tw):
        gc.set(qn('w:w'), str(ancho))
    for ri, row in enumerate(t.rows):
        trPr = row._tr.get_or_add_trPr()
        cs = OxmlElement('w:cantSplit'); trPr.append(cs)
        if ri == 0:
            th = OxmlElement('w:tblHeader'); trPr.append(th)
        valores = enc if ri == 0 else filas[ri - 1]
        for ci, cell in enumerate(row.cells):
            cell.width = Twips(tw[ci])
            tcPr = cell._tc.get_or_add_tcPr()
            if ri == 0:
                tb = OxmlElement('w:tcBorders'); tb.append(borde('w:bottom', sz=8)); tcPr.append(tb)
            p = cell.paragraphs[0]
            p.style = st['CeldaEnc' if ri == 0 else 'Celda']
            # espacio de ancho cero tras «_» y «/» para que rutas y nombres de reglas largos puedan partirse
            lineas = re.sub(r'([_/])(?=\w)', lambda m: m.group(1) + '​', str(valores[ci])).split('<br>')
            escribir(p, lineas[0])
            for extra in lineas[1:]:
                p2 = cell.add_paragraph(style='Celda'); escribir(p2, extra)
    return t


def leyenda(tipo, clave, titulo):
    parrafo(NUM[clave], 'EtiquetaNum')
    parrafo(titulo, 'TituloObjeto')


def nota(texto):
    p = doc.add_paragraph(style='NotaObjeto')
    r = p.add_run('Nota. '); r.italic = True
    escribir(p, texto)


def figura(ruta, ancho_cm, horizontal):
    im = Image.open(f'{RAIZ}/{ruta}')
    w, h = im.size
    max_w = 22.8 if horizontal else 16.5
    max_h = ALTO_H_CM if horizontal else ALTO_V_CM
    ancho = min(float(ancho_cm), max_w)
    if ancho * h / w > max_h:
        ancho = max_h * w / h
    p = doc.add_paragraph(style='Imagen')
    p.add_run().add_picture(f'{RAIZ}/{ruta}', width=Cm(ancho))


def toc():
    p = doc.add_paragraph(style='Normal')
    p.paragraph_format.first_line_indent = Cm(0)
    for tipo, texto in (('begin', None), (None, 'TOC \\o "1-3" \\h \\z \\u'), ('separate', None)):
        r = p.add_run()
        if tipo:
            fc = OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'), tipo); r._r.append(fc)
        else:
            it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = texto; r._r.append(it)
    p.add_run('Actualice el índice (F9) para ver su contenido.')
    r = p.add_run(); fc = OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'), 'end'); r._r.append(fc)


def nueva_seccion(horizontal):
    s = doc.add_section(WD_SECTION.NEW_PAGE)
    if horizontal:
        s.orientation = WD_ORIENT.LANDSCAPE
        s.page_width, s.page_height = Twips(15840), Twips(12240)
    else:
        s.orientation = WD_ORIENT.PORTRAIT
        s.page_width, s.page_height = Twips(12240), Twips(15840)
    for m in ('top_margin', 'bottom_margin', 'left_margin', 'right_margin'):
        setattr(s, m, Twips(1440))
    s.header.is_linked_to_previous = True


# ---------------------------------------------------------------- 6. Lectura del marcado
lineas = []
for f in FUENTES:
    with open(f, encoding='utf-8') as fh:
        lineas += [l.rstrip('\n') for l in fh]

ct = cf = 0
for l in lineas:
    m = re.match(r'@(TABLA|DATOS|TABLAMD|FIGURA)\s+([\w-]+)', l)
    if m:
        if m.group(2) in NUM:
            raise SystemExit(f'Clave duplicada: {m.group(2)}')
        if m.group(1) == 'FIGURA':
            cf += 1; NUM[m.group(2)] = f'Figura {cf}'
        else:
            ct += 1; NUM[m.group(2)] = f'Tabla {ct}'
            if m.group(1) == 'DATOS' and m.group(2) == 'tipos-impactos':
                ct += 1; NUM[m.group(2) + '2'] = f'Tabla {ct}'

horizontal = False
pagina_nueva = True       # tras la carátula comienza una página nueva
lista_actual = None
i = 0
while i < len(lineas):
    l = lineas[i]
    s = l.strip()
    if not s.startswith('- ') and not re.match(r'^\d+\)\s', s):
        lista_actual = None
    if not s or s.startswith('%%'):
        i += 1; continue
    if s.startswith('# '):
        p = parrafo(s[2:], 'Heading 1')
        if not pagina_nueva:
            p.paragraph_format.page_break_before = True
        pagina_nueva = False
    elif s.startswith('## '):
        parrafo(s[3:], 'Heading 2'); pagina_nueva = False
    elif s.startswith('### '):
        parrafo(s[4:], 'Heading 3'); pagina_nueva = False
    elif s == '@INDICE':
        p = parrafo('Índice General', 'TituloIndice')
        if not pagina_nueva:
            p.paragraph_format.page_break_before = True
        toc()
        pagina_nueva = False      # el siguiente título 1 abrirá página con «salto de página anterior»
    elif s in ('@HORIZONTAL', '@VERTICAL'):
        horizontal = s == '@HORIZONTAL'
        nueva_seccion(horizontal); pagina_nueva = True
    elif s.startswith('@TABLA '):
        clave, titulo = [x.strip() for x in s[7:].split('|', 1)]
        anchos = None
        i += 1
        if lineas[i].strip().startswith('@ANCHOS'):
            anchos = [float(x) for x in lineas[i].strip()[7:].split(',')]; i += 1
        filas = []
        while i < len(lineas) and lineas[i].strip().startswith('|'):
            if not re.match(r'^\|[\s:|-]+\|\s*$', lineas[i].strip()):
                filas.append(celdas(lineas[i]))
            i += 1
        leyenda('Tabla', clave, titulo)
        tabla(filas[0], filas[1:], anchos or [1] * len(filas[0]), horizontal)
        pagina_nueva = False
        continue
    elif s.startswith('@DATOS '):
        clave, titulo = [x.strip() for x in s[7:].split('|', 1)]
        nombre = clave.replace('-tipos', '_tipos') if False else clave
        res = datos(clave.replace('-', '_'))
        leyenda('Tabla', clave, titulo)
        tabla(res[0], res[1], res[2], horizontal)
        if len(res) > 3:      # segunda tabla asociada (tipos e impactos)
            i += 1
            titulo2 = lineas[i].strip()[len('@SEGUNDA'):].strip()
            nota_pend = None
            leyenda('Tabla', clave + '2', titulo2)
            tabla(res[3], res[4], [5.0, 4.0, 4.0], horizontal)
        pagina_nueva = False
    elif s.startswith('@TABLAMD '):
        partes = [x.strip() for x in s[9:].split('|')]
        clave, titulo, ruta, idx, cols, anchos = partes[:6]
        t = leer_tablas_md(ruta)[int(idx)]
        if len(partes) > 6:
            excl = re.compile(partes[6])
            t = [t[0]] + [f for f in t[1:] if not excl.search(' '.join(f))]
        sel = list(range(len(t[0]))) if cols == '*' else [int(c) for c in cols.split(',')]
        t = [[f[c] if c < len(f) else '' for c in sel] for f in t]
        leyenda('Tabla', clave, titulo)
        tabla(t[0], t[1:], [float(a) for a in anchos.split(',')], horizontal)
        pagina_nueva = False
    elif s.startswith('@FIGURA '):
        clave, ruta, titulo, ancho = [x.strip() for x in s[8:].split('|')]
        leyenda('Figura', clave, titulo)
        figura(ruta, ancho, horizontal)
        pagina_nueva = False
    elif s.startswith('@NOTA '):
        nota(s[6:])
    elif s.startswith('@REF '):
        parrafo(s[5:], 'Referencia')
    elif s == '@CODIGO':
        i += 1
        while lineas[i].strip() != '@FINCODIGO':
            parrafo(lineas[i].replace('`', '`'), 'Codigo') if False else doc.add_paragraph(lineas[i], style='Codigo')
            i += 1
    elif s.startswith('- '):
        if lista_actual is None or lista_actual[0] != 'v':
            lista_actual = ('v', nueva_lista(901))
        p = parrafo(s[2:], 'Vineta'); aplicar_lista(p, lista_actual[1])
    elif re.match(r'^\d+\)\s', s):
        if lista_actual is None or lista_actual[0] != 'n':
            lista_actual = ('n', nueva_lista(902))
        p = parrafo(re.sub(r'^\d+\)\s', '', s), 'Vineta'); aplicar_lista(p, lista_actual[1])
    else:
        parrafo(s)
        pagina_nueva = False
    i += 1

# idioma español en todo el documento
for rpr in doc.styles.element.iter(qn('w:rPr')):
    pass
lang = rpr_def.find(qn('w:lang'))
if lang is not None:
    lang.set(qn('w:val'), 'es-GT')

# comprobación final: el informe no debe mencionar las herramientas usadas para redactarlo
_texto = '\n'.join(p.text for p in doc.paragraphs) + '\n'.join(c.text for t in doc.tables for r in t.rows for c in r.cells)
_mal = re.findall(r'Claude|Cowork|asistente|inteligencia artificial', _texto, re.I)
if _mal:
    raise SystemExit(f'Términos no permitidos en el informe: {set(_mal)}')
doc.core_properties.title = 'Informe general – Opción B (CMS / E-Commerce Web)'
doc.core_properties.subject = 'Seguridad en Aplicaciones – MASI – UMG 2026'
doc.core_properties.author = 'Equipo del proyecto'
doc.core_properties.comments = ''
doc.save(SALIDA)
print('ok', SALIDA, 'tablas', ct, 'figuras', cf)
