"""Soporte PBIR (Report/definition/...): conversión de visuales del formato Layout clásico
a visual.json y reemplazo de una página dentro de un .pbix guardado en PBIR."""
import json, zipfile

SCHEMA_VISUAL = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.13.0/schema.json'
DIR = {1: 'Ascending', 2: 'Descending'}

def es_pbir(z): return any(n.startswith('Report/definition/') for n in z.namelist())

def a_entidad(o, alias):
    """PBIR no tiene From: cada SourceRef debe nombrar la tabla (Entity), no un alias (Source)."""
    if isinstance(o, dict):
        if 'SourceRef' in o and 'Source' in o['SourceRef']:
            return {**{k: a_entidad(v, alias) for k, v in o.items() if k != 'SourceRef'},
                    'SourceRef': {'Entity': alias[o['SourceRef']['Source']]}}
        return {k: a_entidad(v, alias) for k, v in o.items()}
    if isinstance(o, list): return [a_entidad(v, alias) for v in o]
    return o

def visual_layout_a_pbir(cont):
    """cont = visualContainer del Layout clásico (con 'config' como texto JSON)."""
    cfg = json.loads(cont['config']); sv = cfg['singleVisual']; pos = cfg['layouts'][0]['position']
    v = {'visualType': sv['visualType']}
    pq = sv.get('prototypeQuery')
    if pq:
        alias = {f['Name']: f['Entity'] for f in pq.get('From', [])}
        sel = {s['Name']: a_entidad(s, alias) for s in pq['Select']}
        props = sv.get('columnProperties', {})
        qs = {}
        for rol, items in sv['projections'].items():
            proy = []
            for it in items:
                s = sel[it['queryRef']]
                campo = {k: val for k, val in s.items() if k not in ('Name', 'NativeReferenceName')}
                p = {'field': campo, 'queryRef': it['queryRef'],
                     'nativeQueryRef': s.get('NativeReferenceName') or it['queryRef'].split('.', 1)[-1]}
                if it.get('active'): p['active'] = True
                if it['queryRef'] in props and 'displayName' in props[it['queryRef']]:
                    p['displayName'] = props[it['queryRef']]['displayName']
                proy.append(p)
            qs[rol] = {'projections': proy}
        q = {'queryState': qs}
        if pq.get('OrderBy'):
            q['sortDefinition'] = {'sort': [{'field': a_entidad(o['Expression'], alias), 'direction': DIR[o['Direction']]}
                                            for o in pq['OrderBy']]}
        v['query'] = q
    if sv.get('objects'): v['objects'] = sv['objects']
    if sv.get('vcObjects'): v['visualContainerObjects'] = sv['vcObjects']
    v['drillFilterOtherVisuals'] = sv.get('drillFilterOtherVisuals', True)
    out = {'$schema': SCHEMA_VISUAL, 'name': cfg['name'],
           'position': {k: pos[k] for k in ('x', 'y', 'z', 'height', 'width')} | {'tabOrder': pos.get('tabOrder', pos['z'])},
           'visual': v}
    filtros = json.loads(cont.get('filters') or '[]')
    if filtros: out['filterConfig'] = {'filters': filtros}
    return out

def reemplazar_pagina(origen, destino, page_name, page_json, visuales, quitar_partes=('SecurityBindings',)):
    """Escribe 'destino' = 'origen' con la página page_name reemplazada (page.json + visuales nuevos)."""
    zin = zipfile.ZipFile(origen)
    base = f'Report/definition/pages/{page_name}/'
    with zipfile.ZipFile(destino, 'w') as zout:
        for info in zin.infolist():
            n = info.filename
            if n in quitar_partes or n.startswith(base): continue
            data = zin.read(n)
            if n == '[Content_Types].xml':
                t = data.decode('utf-8-sig')
                for q in quitar_partes: t = t.replace(f'<Override PartName="/{q}" ContentType="" />', '')
                data = t.encode('utf-8')
            zi = zipfile.ZipInfo(n, date_time=info.date_time); zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zout.writestr(zi, data)
        dt = zin.getinfo('Report/definition/report.json').date_time
        def put(n, obj):
            zi = zipfile.ZipInfo(n, date_time=dt); zi.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(zi, json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
        put(base + 'page.json', page_json)
        for vj in visuales: put(f'{base}visuals/{vj["name"]}/visual.json', vj)


def reemplazar_paginas(origen, destino, paginas, orden=None, activa=None, quitar_partes=('SecurityBindings',)):
    """Reemplaza varias páginas a la vez en un PBIR. paginas = {page_id: (page_json, [visual_json, ...])}.
    Las páginas no listadas se copian tal cual. orden = lista de page_id para pages.json (opcional)."""
    zin = zipfile.ZipFile(origen)
    bases = {f'Report/definition/pages/{pid}/': pid for pid in paginas}
    with zipfile.ZipFile(destino, 'w') as zout:
        for info in zin.infolist():
            n = info.filename
            if n in quitar_partes or any(n.startswith(b) for b in bases): continue
            data = zin.read(n)
            if n == '[Content_Types].xml':
                t = data.decode('utf-8-sig')
                for q in quitar_partes: t = t.replace(f'<Override PartName="/{q}" ContentType="" />', '')
                data = t.encode('utf-8')
            elif n == 'Report/definition/pages/pages.json' and (orden or activa):
                pj = json.loads(data)
                if orden: pj['pageOrder'] = orden
                if activa: pj['activePageName'] = activa
                data = json.dumps(pj, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
            zi = zipfile.ZipInfo(n, date_time=info.date_time); zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zout.writestr(zi, data)
        dt = zin.getinfo('Report/definition/report.json').date_time
        def put(n, obj):
            zi = zipfile.ZipInfo(n, date_time=dt); zi.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(zi, json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
        for pid, (pj, visuales) in paginas.items():
            base = f'Report/definition/pages/{pid}/'
            put(base + 'page.json', pj)
            for vj in visuales: put(f'{base}visuals/{vj["name"]}/visual.json', vj)

def page_json_desde_seccion(seccion, page_id, schema, nombre=None, oculta=False, vista='FitToPage'):
    """page.json PBIR a partir de una sección del Layout clásico construida con modificar_layout.
    vista: 'FitToPage' | 'FitToWidth' | 'ActualSize'. Página oculta: "visibility": "HiddenInViewMode" [probado: así la guarda Desktop]."""
    cfg = json.loads(seccion.get('config') or '{}')
    pj = {'$schema': schema, 'name': page_id, 'displayName': nombre or seccion['displayName'], 'displayOption': vista,
          'height': seccion['height'], 'width': seccion['width']}
    if cfg.get('objects'): pj['objects'] = cfg['objects']
    inter = [{'source': r['source'], 'target': r['target'], 'type': 'NoFilter'} for r in cfg.get('relationships', []) if r.get('type') == 3]
    if inter: pj['visualInteractions'] = inter
    if oculta: pj['visibility'] = 'HiddenInViewMode'
    return pj

if __name__ == '__main__':
    print(__doc__.strip()); print('\n(módulo: se importa desde Python; ver SKILL.md)')
