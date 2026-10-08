"""Catálogo de visuales nativos (references/catalogo/, generado del CLI oficial de Microsoft
@microsoft/powerbi-report-authoring-cli + evidencia propia). Consulta y validación sin red ni Node.
Uso:
  python catalogo.py buscar <tipo> <regex>          propiedades cuyo objeto/nombre/displayName coincide
  python catalogo.py propiedades <tipo> [objeto]    objetos o propiedades de un objeto (con tipo y valores de enum)
  python catalogo.py plantilla <tipo>               esqueleto visual.json PBIR con sus roles
  python catalogo.py validar <archivo.pbix> [--destino=rs:2026.05|servicio]   valida todos los visuales y el tema
El catálogo describe la nube/PBIR: para Report Server (Layout clásico) es referencia [probado: el Desktop para RS 2026.05
guarda los mismos nombres de objetos y propiedades en los visuales observados]; lo que decide es un archivo guardado por el
Desktop para RS."""
import json, re, sys, zipfile, functools
from pathlib import Path
DIR = Path(__file__).resolve().parents[1] / 'references' / 'catalogo'

@functools.lru_cache(None)
def indice(): return json.load(open(DIR / '_indice.json', encoding='utf-8'))
@functools.lru_cache(None)
def vcos(): return json.load(open(DIR / '_vcos.json', encoding='utf-8'))
@functools.lru_cache(None)
def evidencia(): return json.load(open(DIR / '_evidencia.json', encoding='utf-8'))['tipos']

@functools.lru_cache(None)
def cargar(tipo):
    """Entrada del catálogo del tipo (None si no existe: visual personalizado o tipo desconocido)."""
    f = DIR / f'{tipo}.json'
    return json.load(open(f, encoding='utf-8')) if f.exists() else None

def propiedades(tipo, objeto=None):
    c = cargar(tipo)
    if c is None: raise KeyError(f'{tipo} no está en el catálogo')
    if objeto is None: return {'objetos': {o: list(p) for o, p in c['objetos'].items()}, 'vcos': {o: list(p) for o, p in vcos().items()}}
    return c['objetos'].get(objeto) or vcos().get(objeto) or {}

def buscar(tipo, patron):
    rx = re.compile(patron, re.I); c = cargar(tipo); out = []
    for zona, objs in (('objects', c['objetos']), ('visualContainerObjects', vcos())):
        for o, ps in objs.items():
            for p, d in ps.items():
                if rx.search(o) or rx.search(p) or rx.search(d.get('displayName', '')): out.append((zona, o, p, d))
    return out

def plantilla(tipo):
    c = cargar(tipo)
    return {'$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.13.0/schema.json',
            'name': '<id de 20 hex>', 'position': {'x': 0, 'y': 0, 'z': 0, 'height': 200, 'width': 300, 'tabOrder': 0},
            'visual': {'visualType': indice()['tipos'][tipo]['nombre_desktop'],
                       'query': {'queryState': {r: {'projections': []} for r in c['roles']}},
                       'objects': {}, 'visualContainerObjects': {}, 'drillFilterOtherVisuals': True},
            '_roles': c['roles'], '_objetos': list(c['objetos'])}

# ---------------------------------------------------------------- validación
def _literal(v):
    """('bool'|'num'|'str'|'null'|'expr'|'fill'|'otro', valor_texto) de una propiedad de formato."""
    if isinstance(v, dict):
        if 'solid' in v: return 'fill', None
        e = v.get('expr')
        if isinstance(e, dict) and 'Literal' in e:
            s = str(e['Literal'].get('Value'))
            if s in ('true', 'false'): return 'bool', s
            if s == 'null': return 'null', s
            if s.startswith("'") and s.endswith("'"): return 'str', s[1:-1].replace("''", "'")
            m = re.fullmatch(r'(-?[\d.]+(?:E[-+]?\d+)?)([DLM])', s)
            if m: return 'num', m.group(1)
            return 'otro', s
        return 'expr', None
    if isinstance(v, (list, str)): return 'otro', None       # p. ej. paragraphs de textbox
    return 'otro', None

def revisar_propiedad(tipo, zona, objeto, prop, valor, d):
    """Errores/avisos de UNA propiedad contra su definición d del catálogo."""
    err, avi = [], []
    clase, txt = _literal(valor)
    t = d.get('tipo')
    if clase in ('expr', 'null', 'otro') or t in ('formatting', 'unknown', 'image', None): return err, avi
    ruta = f'{tipo}.{objeto}.{prop}'
    if t == 'enum':
        vals = [str(x) for x in d.get('valores', [])]
        if txt is not None and txt not in vals:
            if txt.lower() in (x.lower() for x in vals): avi.append(f'{ruta}: enum "{txt}" difiere en mayúsculas de {vals}')
            else: err.append(f'{ruta}: enum inválido "{txt}" (válidos: {", ".join(vals[:12])})')
    elif t == 'bool' and clase != 'bool': err.append(f'{ruta}: se esperaba bool y hay {clase} "{txt}"')
    elif t in ('numeric', 'integer') and clase != 'num': err.append(f'{ruta}: se esperaba número y hay {clase} "{txt}"')
    elif t == 'integer' and txt and '.' in txt: avi.append(f'{ruta}: entero escrito con decimales "{txt}" (usa dint/lit(int))')
    elif t == 'fill' and clase != 'fill': err.append(f'{ruta}: se esperaba color ({{"solid": ...}}) y hay {clase}')
    elif t == 'text' and clase not in ('str',): err.append(f'{ruta}: se esperaba texto y hay {clase} "{txt}"')
    return err, avi

def _ev(tipo, objeto, prop):
    e = evidencia()
    return e.get(tipo, {}).get(objeto, {}).get(prop) or e.get('*', {}).get(objeto, {}).get(prop) or {}

def _plataforma_tipo(tipo, destino):
    err, avi = [], []
    info = indice()['tipos'].get(tipo)
    if not info: return err, avi
    if info.get('deprecado'): avi.append(f"{tipo}: deprecado ({info.get('motivo', '')}; alternativa {info.get('alternativa', '-')})")
    if destino and destino.startswith('rs'):
        rs = info['report_server']; rel = destino.split(':', 1)[1] if ':' in destino else None
        if rs == 'no': err.append(f'{tipo}: no soportado en Report Server')
        elif rs.startswith('desde') and rel and rel < rs.split()[1]: err.append(f'{tipo}: en Report Server solo desde {rs.split()[1]} (destino {rel})')
    return err, avi

def _desempacar(obj):
    """Normaliza un visual PBIR (visual.json), un contenedor clásico ({'config': '...'}) o un config/singleVisual clásico."""
    if 'visual' in obj:
        v = obj['visual']; roles = list(v.get('query', {}).get('queryState', {}))
        return v.get('visualType'), v.get('objects', {}), v.get('visualContainerObjects', {}), roles
    if 'config' in obj and isinstance(obj['config'], str): obj = json.loads(obj['config'])
    sv = obj.get('singleVisual', obj)
    return sv.get('visualType'), sv.get('objects', {}), sv.get('vcObjects', {}), list(sv.get('projections', {}))

def validar_visual(obj, destino=None):
    """Devuelve (errores, avisos) de un visual en cualquiera de los dos formatos. destino: 'rs:2026.05' | 'servicio' | None."""
    tipo, objs, vco, roles = _desempacar(obj)
    err, avi = _plataforma_tipo(tipo, destino)
    c = cargar(tipo)
    if c is None:
        avi.append(f'{tipo}: no está en el catálogo (¿visual personalizado?): sin validar')
        return err, avi
    if destino and destino.startswith('rs'): pass   # el catálogo es de la nube: los errores siguen valiendo como referencia
    for r in roles:
        if r not in c['roles']: err.append(f'{tipo}: rol inexistente "{r}" (roles: {", ".join(c["roles"])})')
    for zona, d_objs, ref in (('objects', objs, c['objetos']), ('vcObjects', vco, vcos())):
        for o, items in d_objs.items():
            if o not in ref:
                err.append(f'{tipo}: objeto inexistente {zona}.{o}'); continue
            for it in items if isinstance(items, list) else []:
                for p, val in (it.get('properties') or {}).items():
                    if p not in ref[o]:
                        err.append(f'{tipo}: propiedad inexistente {zona}.{o}.{p} (el Desktop la borra al guardar: nube y RS)'); continue
                    e, a = revisar_propiedad(tipo, zona, o, p, val, ref[o][p]); err += e; avi += a
                    ev = _ev(tipo, o, p)
                    if ev.get('ignorado') and ev.get('ignorado_si', _literal(val)[1]) == _literal(val)[1]: avi.append(f'{tipo}.{o}.{p}: Power BI lo ignora en pantalla ({ev["ignorado"]})')
    return err, avi

def validar_tema(tema):
    """Valida visualStyles de un tema (JSON de tema del reporte) contra el catálogo: tipo, objeto, propiedad y enums.
    '*' (todos los visuales) solo admite VCOs u objetos comunes; 'page' no está en el catálogo (se omite)."""
    err, avi = [], []
    for tipo, sel in tema.get('visualStyles', {}).items():
        if tipo == 'page': continue
        c = cargar(tipo) if tipo != '*' else {'objetos': {}}
        if c is None: err.append(f'tema: tipo desconocido "{tipo}"'); continue
        for objetos in sel.values():
            for o, items in objetos.items():
                ref = c['objetos'].get(o) or vcos().get(o)
                if ref is None:
                    (avi if tipo == '*' else err).append(f'tema: objeto "{o}" no existe para "{tipo}"'); continue
                for it in items:
                    for p, val in it.items():
                        if p not in ref: err.append(f'tema: propiedad "{o}.{p}" no existe para "{tipo}"'); continue
                        d = ref[p]
                        if d.get('tipo') == 'enum' and not isinstance(val, (dict, list)) and str(val) not in map(str, d.get('valores', [])):
                            err.append(f'tema: {tipo}.{o}.{p} = {val!r} no es un valor válido {d.get("valores")}')
    return err, avi

def validar_pbix(ruta, destino=None):
    """Valida todos los visuales (clásico o PBIR) y el tema personalizado de un .pbix."""
    z = zipfile.ZipFile(ruta); n = z.namelist(); err, avi = [], []
    def agregar(donde, e, a):
        err.extend(f'{donde}: {x}' for x in e); avi.extend(f'{donde}: {x}' for x in a)
    if 'Report/Layout' in n:
        L = json.loads(z.read('Report/Layout').decode('utf-16-le').lstrip('﻿'))
        for s in L['sections']:
            for cont in s['visualContainers']:
                cfg = json.loads(cont.get('config') or '{}')
                if 'singleVisual' in cfg: agregar(f"{s['displayName']}/{cfg.get('name')}", *validar_visual(cfg, destino))
    else:
        for x in n:
            if x.endswith('/visual.json'):
                agregar(x.split('/')[3] + '/' + x.split('/')[5], *validar_visual(json.loads(z.read(x)), destino))
    for x in n:
        if x.startswith('Report/StaticResources/RegisteredResources/') and x.endswith('.json'):
            try: t = json.loads(z.read(x).decode('utf-8-sig'))
            except ValueError: continue
            if 'visualStyles' in t or 'dataColors' in t: agregar(x.rsplit('/', 1)[1], *validar_tema(t))
    return err, sorted(set(avi), key=avi.index)

if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    destino = next((x.split('=', 1)[1] for x in sys.argv[1:] if x.startswith('--destino=')), None)
    if not a: print(__doc__); sys.exit()
    cmd = a[0]
    if cmd == 'buscar':
        for z_, o, p, d in buscar(a[1], a[2]): print(f'{z_}.{o}.{p}', json.dumps(d, ensure_ascii=False))
    elif cmd == 'propiedades':
        print(json.dumps(propiedades(a[1], a[2] if len(a) > 2 else None), ensure_ascii=False, indent=1))
    elif cmd == 'plantilla':
        print(json.dumps(plantilla(a[1]), ensure_ascii=False, indent=1))
    elif cmd == 'validar':
        e, w = validar_pbix(a[1], destino)
        print('\n'.join('AVISO ' + x for x in w)); print('\n'.join('ERROR ' + x for x in e))
        print(f'errores: {len(e)} · avisos: {len(w)}')
