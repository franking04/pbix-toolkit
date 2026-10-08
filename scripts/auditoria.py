"""Auditoría [P] automática de un .pbix (guia_diseno.md §10): lo que se puede medir desde el archivo, en 3 fases.
Funciona igual con Layout clásico y PBIR. No reemplaza la revisión de la captura [C].
Uso: python auditoria.py archivo.pbix [--direccion=moderno] [--pagina=Nombre]
  Crítico       unidad o periodo ausente en el título de un visual de datos · solapes entre visuales de datos ·
                contraste < 4.5 (texto de textbox sobre el fondo de la página, si ambos son colores fijos)
  Refinamiento  posiciones fuera de la rejilla de 8 px · márgenes izquierdo/derecho desiguales · > 6 tamaños o > 3 pesos de
                letra · colores fuera de los tokens (dirección o tema del archivo) · cajas con radios de borde distintos
  Pulido        visuales de datos sin texto alternativo · orden de tabulación distinto del de lectura · botones sin estado hover
Devuelve avisos (no errores): son criterios de diseño, no defectos que impidan abrir el archivo."""
import json, re, sys, os, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DECORATIVOS = {'textbox', 'shape', 'basicShape', 'image', 'actionButton', 'pageNavigator', 'bookmarkNavigator'}
FILTROS = {'slicer', 'advancedSlicerVisual', 'listSlicer', 'textSlicer', 'filterSlicer'}
UNIDAD = re.compile(r'(\$|USD|MXN|COP|EUR|%|\bpp\b|\bund\b|unidades|días|\bkg\b|\bmil\b|millones|\bM\b|\bK\b|cajas|toneladas|horas)', re.I)
PERIODO = re.compile(r'(mes|meses|año|años|anual|trimestre|semana|día|periodo|período|acumulad|YTD|MTD|20\d\d|ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic|último|actual)', re.I)
HEX = re.compile(r"'(#[0-9A-Fa-f]{6})'")

def _lit(v):
    try: return v['expr']['Literal']['Value']
    except (KeyError, TypeError): return None

def _txt(v):
    s = _lit(v); return s[1:-1].replace("''", "'") if isinstance(s, str) and s.startswith("'") else None

def visuales(ruta):
    """[(pagina, ancho, alto, fondo_pagina_hex|None, tiene_imagen_fondo, v)], v = dict(id, tipo, x, y, w, h, z, tab, objects, vco, runs)."""
    z = zipfile.ZipFile(ruta); n = z.namelist(); out = []
    def fondo(objs):
        bg = ((objs or {}).get('background') or [{}])[0].get('properties', {})
        col = _txt((bg.get('color') or {}).get('solid', {}).get('color')) if bg.get('color') else None
        return col, 'image' in bg
    if 'Report/Layout' in n:
        L = json.loads(z.read('Report/Layout').decode('utf-16-le').lstrip('﻿'))
        for s in L['sections']:
            cfg = json.loads(s.get('config') or '{}')
            if cfg.get('visibility') == 1: continue
            col, img = fondo(cfg.get('objects'))
            for c in s['visualContainers']:
                vc = json.loads(c.get('config') or '{}'); sv = vc.get('singleVisual')
                if not sv: continue
                out.append((s['displayName'], s['width'], s['height'], col, img,
                            dict(id=vc.get('name'), tipo=sv.get('visualType'), x=c['x'], y=c['y'], w=c['width'], h=c['height'],
                                 z=c.get('z', 0), tab=c.get('tabOrder', vc.get('layouts', [{}])[0].get('position', {}).get('tabOrder')),
                                 objects=sv.get('objects', {}), vco=sv.get('vcObjects', {}),
                                 campos=[x['queryRef'] for r_ in sv.get('projections', {}).values() for x in r_],
                                 columnas=[x['Name'] for x in sv.get('prototypeQuery', {}).get('Select', []) if 'Column' in x],
                                 filtros=json.loads(c.get('filters') or '[]'))))
    else:
        pj = json.loads(z.read('Report/definition/pages/pages.json'))
        for pid in pj['pageOrder']:
            pg = json.loads(z.read(f'Report/definition/pages/{pid}/page.json'))
            if pg.get('visibility') == 'HiddenInViewMode': continue
            col, img = fondo(pg.get('objects'))
            for x in n:
                if x.startswith(f'Report/definition/pages/{pid}/visuals/') and x.endswith('visual.json'):
                    j = json.loads(z.read(x)); v = j.get('visual', {}); p = j['position']
                    out.append((pg['displayName'], pg['width'], pg['height'], col, img,
                                dict(id=j['name'], tipo=v.get('visualType'), x=p['x'], y=p['y'], w=p['width'], h=p['height'],
                                     z=p.get('z', 0), tab=p.get('tabOrder'), objects=v.get('objects', {}), vco=v.get('visualContainerObjects', {}),
                                     campos=[x.get('queryRef') for r_ in v.get('query', {}).get('queryState', {}).values() for x in r_.get('projections', [])],
                                     columnas=[x.get('queryRef') for r_ in v.get('query', {}).get('queryState', {}).values() for x in r_.get('projections', [])
                                               if 'Column' in x.get('field', {})],
                                     filtros=j.get('filterConfig', {}).get('filters', []))))
    return out

def _runs(v):
    """Textos de textbox: [(texto, pt, color, familia)]."""
    r = []
    for par in ((v['objects'].get('general') or [{}])[0].get('properties', {}).get('paragraphs') or []):
        for t in par.get('textRuns', []):
            st = t.get('textStyle', {}); fs = str(st.get('fontSize') or '')
            pt = float(fs[:-2]) * .75 if fs.endswith('px') else float(fs[:-2]) if fs.endswith('pt') else float(fs) if fs else None   # el Desktop escribe pt o px
            r.append((t.get('value', ''), pt, st.get('color'), st.get('fontFamily', '')))
    return r

def _lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]

def _contraste(a, b):
    la, lb = _lum(a), _lum(b); return (max(la, lb) + .05) / (min(la, lb) + .05)

def paleta(ruta, direccion=None):
    """Hex permitidos: tokens de la dirección (o de todas) + colores del tema personalizado del archivo + blanco/negro."""
    ruta_tok = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'references', 'tokens.json')
    try:   # direcciones a la medida (PBIX_TOKENS_EXTRA) igual que las fijas, como deneb._c
        from estilo_a_medida import cargar_tokens
        tk = cargar_tokens(ruta_tok)
    except ImportError:
        tk = json.load(open(ruta_tok, encoding='utf-8'))
    dirs = [tk['direcciones'][direccion]] if direccion else list(tk['direcciones'].values())
    ok = {'#FFFFFF', '#000000'}
    for d in dirs:
        for v in d.values():
            if isinstance(v, str) and re.fullmatch(r'#[0-9A-Fa-f]{6}', v): ok.add(v.upper())
            if isinstance(v, list): ok |= {x.upper() for x in v if isinstance(x, str) and x.startswith('#')}
    z = zipfile.ZipFile(ruta)
    for x in z.namelist():
        if x.startswith('Report/StaticResources/RegisteredResources/') and x.endswith('.json'):
            ok |= {h.upper() for h in re.findall(r'#[0-9A-Fa-f]{6}', z.read(x).decode('utf-8', 'ignore'))}
    return ok

def auditar(ruta, direccion=None, pagina=None):
    """{'critico': [...], 'refinamiento': [...], 'pulido': [...]} (cada ítem es texto con página y visual)."""
    res = {'critico': [], 'refinamiento': [], 'pulido': []}
    ok_hex = paleta(ruta, direccion)
    por_pag = collections.defaultdict(list); meta = {}
    for pg, W, H, col, img, v in visuales(ruta):
        if pagina and pg != pagina: continue
        por_pag[pg].append(v); meta[pg] = (W, H, col, img)
    for pg, vs in por_pag.items():
        W, H, col, img = meta[pg]
        datos = [v for v in vs if v['tipo'] not in DECORATIVOS and v['tipo'] not in FILTROS]
        # --- crítico
        for v in datos:
            t = _txt(((v['vco'].get('title') or [{}])[0].get('properties', {})).get('text'))
            sub = _txt(((v['vco'].get('subTitle') or [{}])[0].get('properties', {})).get('text')) or ''
            if t and v['tipo'] not in ('card', 'cardVisual', 'multiRowCard', 'kpi'):
                if not UNIDAD.search(t + ' ' + sub) or not PERIODO.search(t + ' ' + sub):
                    fase = 'refinamiento' if v['tipo'] in ('tableEx', 'pivotTable', 'table', 'matrix') else 'critico'   # en tablas la unidad suele ir en los encabezados
                    res[fase].append(f'{pg} · {v["tipo"]} «{t[:40]}»: título sin {"unidad" if not UNIDAD.search(t + " " + sub) else "periodo"} (título o subtítulo)')
        for i, a in enumerate(datos):
            for b in datos[i + 1:]:
                ix = min(a['x'] + a['w'], b['x'] + b['w']) - max(a['x'], b['x']); iy = min(a['y'] + a['h'], b['y'] + b['h']) - max(a['y'], b['y'])
                if ix > 2 and iy > 2: res['critico'].append(f'{pg} · solape {a["tipo"]} / {b["tipo"]} ({ix:.0f}×{iy:.0f} px)')
        def fondo_de(v):
            """Color de fondo real: el propio, o el de la caja con fondo sólido más alta (z) que contiene el centro del texto."""
            cx, cy = v['x'] + v['w'] / 2, v['y'] + v['h'] / 2; mejor = None
            for u in vs:
                bg = (u['vco'].get('background') or [{}])[0].get('properties', {})
                c = _txt((bg.get('color') or {}).get('solid', {}).get('color')) if _lit(bg.get('show')) == 'true' else None
                if c and re.fullmatch(r'#[0-9A-Fa-f]{6}', c) and u['x'] <= cx <= u['x'] + u['w'] and u['y'] <= cy <= u['y'] + u['h']                         and (u is v or u['z'] <= v['z']) and (mejor is None or u is v or u['z'] > mejor[0]):
                    mejor = (u['z'] if u is not v else 10**9, c)
            return mejor[1] if mejor else None
        if not img:
            for v in vs:
                if v['tipo'] != 'textbox': continue
                fondo_v = fondo_de(v)
                if not (fondo_v or col): continue
                for texto, pt, c, _ in _runs(v):
                    if texto.strip() and c and re.fullmatch(r'#[0-9A-Fa-f]{6}', c):
                        r = _contraste(c, fondo_v or col); minimo = 3 if (pt or 0) >= 18 else 4.5
                        if r < minimo - .05: res['critico'].append(f'{pg} · contraste {r:.2f} < {minimo}: «{texto[:30]}»')
        # tablas que pueden tener barra de desplazamiento: sin top N (filtro del visual o medida «top») y con caja para pocas filas
        for v in vs:
            if v['tipo'] in ('tableEx', 'table'):
                top = any(f.get('type') == 'TopN' for f in v.get('filtros', [])) or any('top' in (q or '').lower() for q in v.get('campos', []))
                cat = v.get('columnas', [])   # columnas sin agregar = categorías (filas)
                if not top and cat:
                    from componentes import LienzoV2
                    n = LienzoV2.filas_que_caben(v['h'], con_titulo=bool((v['vco'].get('title') or [{}])[0].get('properties', {}).get('show')))
                    res['refinamiento'].append(f'{pg} · tableEx sin top N: caben ~{n} filas; si la categoría tiene más, habrá barra '
                                               f'(componentes.LienzoV2.tabla_top)')
        # --- refinamiento
        fuera = [v for v in vs if any(abs(q - round(q / 8) * 8) > 1 for q in (v['x'], v['y'], v['w'], v['h']))]
        if fuera: res['refinamiento'].append(f'{pg} · {len(fuera)} de {len(vs)} visuales fuera de la rejilla de 8 px (p. ej. {fuera[0]["tipo"]} en {fuera[0]["x"]:.0f},{fuera[0]["y"]:.0f})')
        if vs:
            izq = min(v['x'] for v in vs); der = W - max(v['x'] + v['w'] for v in vs)
            if abs(izq - der) > 8: res['refinamiento'].append(f'{pg} · márgenes desiguales: izquierdo {izq:.0f} px, derecho {der:.0f} px')
        tam, pesos = set(), set()
        for v in vs:
            for _, pt, _, fam in _runs(v):
                if pt: tam.add(round(pt * 2) / 2)
                pesos.add('bold' if 'Bold' in fam else 'semibold' if 'Semibold' in fam else 'light' if 'Light' in fam else 'regular')
            for o in ('labels', 'value', 'columnHeaders', 'values', 'categoryAxis', 'valueAxis'):
                fs = _lit(((v['objects'].get(o) or [{}])[0].get('properties', {})).get('fontSize'))
                if fs: tam.add(round(float(str(fs).rstrip('DL')) * 2) / 2)
        if len(tam) > 6: res['refinamiento'].append(f'{pg} · {len(tam)} tamaños de letra (máx. 6): {sorted(tam)}')
        if len(pesos) > 3: res['refinamiento'].append(f'{pg} · {len(pesos)} pesos de letra (máx. 3): {sorted(pesos)}')
        hexes = collections.Counter(h.upper() for v in vs for h in HEX.findall(json.dumps([v['objects'], v['vco']])))
        hexes.update(c.upper() for v in vs for _, _, c, _ in _runs(v) if c and c.startswith('#'))
        raros = {h: k for h, k in hexes.items() if h not in ok_hex}
        if raros: res['refinamiento'].append(f'{pg} · {len(raros)} colores fuera de los tokens/tema: {", ".join(list(raros)[:6])}')
        radios = {_lit(((v['vco'].get('border') or [{}])[0].get('properties', {})).get('radius')) for v in vs
                  if _lit(((v['vco'].get('border') or [{}])[0].get('properties', {})).get('show')) == 'true'}
        radios.discard(None)
        if len(radios) > 1: res['refinamiento'].append(f'{pg} · cajas con radios distintos: {sorted(radios)}')
        # --- pulido
        sin_alt = [v for v in datos if not ((v['vco'].get('general') or [{}])[0].get('properties', {})).get('altText')]
        if sin_alt: res['pulido'].append(f'{pg} · {len(sin_alt)} de {len(datos)} visuales de datos sin texto alternativo')
        orden = [v for v in vs if v['tipo'] not in ('textbox', 'shape', 'basicShape', 'image') and v['tab'] is not None]
        lectura = sorted(orden, key=lambda v: (round(v['y'] / 40), v['x'])); tab = sorted(orden, key=lambda v: v['tab'])
        inv = sum(1 for a, b in zip(lectura, tab) if a['id'] != b['id'])
        if inv: res['pulido'].append(f'{pg} · orden de tabulación distinto del de lectura en {inv} de {len(orden)} visuales')
        for v in vs:
            if v['tipo'] == 'actionButton' and not any((it.get('selector') or {}).get('id') == 'hover'
                                                      for o in v['objects'].values() for it in o):
                res['pulido'].append(f'{pg} · botón sin estado «al pasar el mouse» (selector id hover)'); break
    return res

if __name__ == '__main__':
    from comun import ayuda; ayuda(__doc__, 1)
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    op = dict(x[2:].split('=', 1) for x in sys.argv[1:] if x.startswith('--') and '=' in x)
    r = auditar(a[0], op.get('direccion'), op.get('pagina'))
    for fase in ('critico', 'refinamiento', 'pulido'):
        print(f'== {fase}: {len(r[fase])}'); [print('  ' + x) for x in r[fase]]
