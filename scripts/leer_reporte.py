"""Lee el reporte de un .pbix en cualquiera de sus dos formatos (Layout clásico o PBIR) y produce la misma
salida: paginas, objetos, referencias (campo -> visual), campos, filtros, formato (campos usados solo en
formato condicional / títulos dinámicos) y estados de slicer. Solo metadatos; nunca filas de datos.
Uso: python leer_reporte.py archivo.pbix carpeta_salida"""
import json, sys, os, csv, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import (formato_reporte, leer_json, leer_layout, jload, resolver, condicion, leer_filtros, DESCONOCIDOS)

# ---------------- normalización: cada formato -> la misma lista de páginas y visuales ----------------
def _titulo(vco):
    try: return vco['title'][0]['properties']['text']['expr']['Literal']['Value'].strip("'")
    except Exception: return ''

def normalizar_layout(z):
    L = leer_layout(z)
    rep = {'filtros': L.get('filters'), 'paginas': []}
    for s in L['sections']:
        scfg = jload(s.get('config'), {}) or {}
        pag = {'id': s.get('name'), 'nombre': s.get('displayName'), 'ordinal': s.get('ordinal'),
               'ancho': s.get('width'), 'alto': s.get('height'), 'oculta': scfg.get('visibility') == 1,
               'filtros': s.get('filters'), 'interacciones': scfg.get('relationships', []), 'visuales': []}
        for v in s.get('visualContainers', []):
            c = jload(v.get('config'), {}) or {}
            sv = c.get('singleVisual') or {}
            grupo = c.get('singleVisualGroup')
            pq = sv.get('prototypeQuery') or {}
            alias = {x['Name']: x.get('Entity', '?') for x in pq.get('From', [])}
            sel = {x.get('Name'): x for x in pq.get('Select', [])}
            proy, usados = [], set()
            for rol, items in (sv.get('projections') or {}).items():
                for it in items:
                    qr = it.get('queryRef'); usados.add(qr)
                    if qr in sel: proy.append((rol, sel[qr], qr, sel[qr].get('NativeReferenceName')))
                    else: DESCONOCIDOS['projection sin Select'] += 1
            for qr, e in sel.items():                     # Select fuera de projections (orden)
                if qr not in usados: proy.append(('(solo Select: orden)', e, qr, e.get('NativeReferenceName')))
            pag['visuales'].append({
                'id': c.get('name'), 'tipo': sv.get('visualType') or ('grupo' if grupo is not None else 'desconocido'),
                'titulo': _titulo(sv.get('vcObjects', {})) or (grupo or {}).get('displayName', ''),
                'x': v.get('x'), 'y': v.get('y'), 'ancho': v.get('width'), 'alto': v.get('height'),
                'grupo_padre': c.get('parentGroupName', ''), 'con_datos': bool(pq), 'alias': alias,
                'proyecciones': proy, 'filtros': v.get('filters'),
                'objects': sv.get('objects', {}), 'vcObjects': sv.get('vcObjects', {})})
        rep['paginas'].append(pag)
    return rep

def normalizar_pbir(z):
    base = 'Report/definition/'
    reporte = leer_json(z, base + 'report.json')
    orden = leer_json(z, base + 'pages/pages.json').get('pageOrder', [])
    rep = {'filtros': reporte.get('filterConfig', {}).get('filters', []), 'paginas': []}
    for i, pid in enumerate(orden):
        p = leer_json(z, f'{base}pages/{pid}/page.json')
        pag = {'id': pid, 'nombre': p.get('displayName'), 'ordinal': i, 'ancho': p.get('width'), 'alto': p.get('height'),
               'oculta': p.get('visibility') == 'HiddenInViewMode',
               'filtros': p.get('filterConfig', {}).get('filters', []),
               'interacciones': p.get('visualInteractions', []), 'visuales': []}
        pref = f'{base}pages/{pid}/visuals/'
        for n in sorted(x for x in z.namelist() if x.startswith(pref) and x.endswith('/visual.json')):
            vj = leer_json(z, n)
            vis = vj.get('visual') or {}
            grupo = vj.get('visualGroup')
            proy = []
            for rol, r in (vis.get('query', {}).get('queryState', {}) or {}).items():
                for pr in r.get('projections', []):
                    proy.append((rol, pr['field'], pr.get('queryRef'), pr.get('nativeQueryRef')))
            pos = vj.get('position', {})
            pag['visuales'].append({
                'id': vj.get('name'), 'tipo': vis.get('visualType') or ('grupo' if grupo is not None else 'desconocido'),
                'titulo': _titulo(vis.get('visualContainerObjects', {})) or (grupo or {}).get('displayName', ''),
                'x': pos.get('x'), 'y': pos.get('y'), 'ancho': pos.get('width'), 'alto': pos.get('height'),
                'grupo_padre': vj.get('parentGroupName', ''), 'con_datos': bool(proy), 'alias': {},
                'proyecciones': proy, 'filtros': vj.get('filterConfig', {}).get('filters', []),
                'objects': vis.get('objects', {}), 'vcObjects': vis.get('visualContainerObjects', {})})
        rep['paginas'].append(pag)
    return rep

# ---------------- campos usados en formato (fuera de las proyecciones) ----------------
EXPR_CAMPO = ('Measure', 'Column', 'Aggregation', 'HierarchyLevel', 'GroupRef')
def _campos_en(o, ruta, out):
    if isinstance(o, dict):
        if any(k in o and isinstance(o[k], dict) for k in EXPR_CAMPO):
            out.append((ruta, o)); return
        for k, v in o.items():
            if k in ('selector', 'filter'): continue        # selectores y estado de slicer se tratan aparte
            _campos_en(v, ruta + [k], out)
    elif isinstance(o, list):
        for v in o: _campos_en(v, ruta, out)

# ---------------- proceso común ----------------
def procesar(ruta, out):
    z = zipfile.ZipFile(ruta)
    fmt = formato_reporte(z)
    if fmt is None: raise SystemExit('El archivo no contiene reporte (ni Report/Layout ni Report/definition).')
    rep = normalizar_layout(z) if fmt == 'Layout' else normalizar_pbir(z)
    paginas, objetos, refs, filtros, formato, slicers = [], [], [], [], [], []
    leer_filtros(rep['filtros'], 'reporte', '', '', filtros)
    for pg in rep['paginas']:
        pag = pg['nombre']
        paginas.append(dict(ordinal=pg['ordinal'], nombre_interno=pg['id'], pagina=pag, ancho=pg['ancho'], alto=pg['alto'],
                            objetos=len(pg['visuales']), oculta=pg['oculta'],
                            filtros=len(jload(pg['filtros'], []) if isinstance(pg['filtros'], str) else pg['filtros'] or []),
                            interacciones=len(pg['interacciones'])))
        leer_filtros(pg['filtros'], 'pagina', pag, '', filtros)
        for v in pg['visuales']:
            n_refs, propios = 0, set()
            for rol, expr, qr, nat in v['proyecciones']:
                txt, base = resolver(expr, v['alias'])
                vistos = set()
                for b in base:                     # una referencia por campo base distinto en cada proyección
                    k = (b['tabla'], b['campo'], b['tipo'])
                    if k in vistos: continue
                    vistos.add(k); propios.add((b['tabla'], b['campo']))
                    refs.append(dict(pagina=pag, visual_id=v['id'], tipo_visual=v['tipo'], titulo=v['titulo'], rol=rol,
                                     tabla=b['tabla'], campo=b['campo'], tipo_campo=b['tipo'], detalle=b.get('extra', ''),
                                     expresion=txt, query_ref=qr, nombre_visible=nat or '',
                                     query_ref_difiere=bool(qr) and f"{b['tabla']}.{b['campo']}" not in qr))
                    n_refs += 1
            objetos.append(dict(pagina=pag, visual_id=v['id'], tipo_visual=v['tipo'], titulo=v['titulo'], x=v['x'], y=v['y'],
                                ancho=v['ancho'], alto=v['alto'], con_datos=v['con_datos'], referencias=n_refs,
                                grupo_padre=v['grupo_padre'],
                                filtros=len(jload(v['filtros'], []) if isinstance(v['filtros'], str) else v['filtros'] or [])))
            leer_filtros(v['filtros'], 'visual', pag, v['id'], filtros)
            for zona in ('objects', 'vcObjects'):
                for obj, items in (v[zona] or {}).items():
                    for it in items:
                        props = it.get('properties', {})
                        if 'filter' in props and isinstance(props['filter'], dict):        # estado guardado del slicer
                            q = props['filter'].get('filter', {})
                            al = {x['Name']: x.get('Entity', '?') for x in q.get('From', [])}
                            slicers.append(dict(pagina=pag, visual_id=v['id'], tipo_visual=v['tipo'],
                                                condicion=' AND '.join(condicion(w.get('Condition'), al) for w in q.get('Where', []))))
                        enc = []; _campos_en(props, [zona, obj], enc)
                        for rz, e in enc:
                            for b in resolver(e, v['alias'])[1]:
                                formato.append(dict(pagina=pag, visual_id=v['id'], tipo_visual=v['tipo'], zona='/'.join(rz[:2]),
                                                    propiedad='/'.join(rz[2:4]), tabla=b['tabla'], campo=b['campo'],
                                                    tipo_campo=b['tipo'], tambien_en_proyecciones=(b['tabla'], b['campo']) in propios))
    campos = {}
    for r in refs:
        k = (r['tabla'], r['campo'], r['tipo_campo'])
        d = campos.setdefault(k, dict(tabla=k[0], campo=k[1], tipo_campo=k[2], referencias=0, visuales=set(), paginas=set()))
        d['referencias'] += 1; d['visuales'].add(r['visual_id']); d['paginas'].add(r['pagina'])
    campos = [dict(c, visuales=len(c['visuales']), paginas=len(c['paginas'])) for c in campos.values()]
    os.makedirs(out, exist_ok=True)
    for nombre, filas in [('paginas', paginas), ('objetos', objetos), ('referencias', refs), ('campos', campos),
                          ('filtros', filtros), ('formato', formato), ('estados_slicer', slicers)]:
        with open(os.path.join(out, nombre + '.csv'), 'w', newline='', encoding='utf-8-sig') as h:
            if filas:
                w = csv.DictWriter(h, fieldnames=list(filas[0].keys())); w.writeheader(); w.writerows(filas)
    pares = {(r['tabla'], r['campo']) for r in refs}
    solo_formato = {(f['tabla'], f['campo']) for f in formato} - pares
    try:
        from plataforma import detectar as _plat
        plat = {k: v for k, v in _plat(ruta).items() if k != 'archivo'}
    except Exception as e:
        plat = {'error': str(e)}
    resumen = dict(archivo=os.path.basename(ruta), formato_reporte=fmt, plataforma=plat, paginas=len(paginas),
                   paginas_ocultas=sum(p['oculta'] for p in paginas), objetos=len(objetos),
                   objetos_con_datos=sum(o['con_datos'] for o in objetos), referencias=len(refs),
                   campos_distintos=len(pares),
                   medidas=len({(r['tabla'], r['campo']) for r in refs if r['tipo_campo'] == 'Measure'}),
                   tablas=len({r['tabla'] for r in refs}), filtros=len(filtros),
                   filtros_por_ambito=dict(collections.Counter(f['ambito'] for f in filtros)),
                   filtros_con_condicion=sum(f['activo'] for f in filtros), estados_slicer=len(slicers),
                   campos_solo_en_formato=sorted(f'{t}[{c}]' for t, c in solo_formato),
                   tipos_visual=dict(collections.Counter(o['tipo_visual'] for o in objetos).most_common()),
                   query_ref_engañoso=len({(r['query_ref'], r['tabla'], r['campo']) for r in refs if r['query_ref_difiere']}),
                   nodos_no_reconocidos=dict(DESCONOCIDOS))
    with open(os.path.join(out, 'resumen.json'), 'w', encoding='utf-8') as h:
        json.dump(resumen, h, ensure_ascii=False, indent=1)
    return resumen

if __name__ == '__main__':
    from comun import ayuda; ayuda(__doc__, 2)
    print(json.dumps(procesar(sys.argv[1], sys.argv[2]), ensure_ascii=False, indent=1))
