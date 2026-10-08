"""Verificación previa a entregar un .pbix PBIR modificado.
Uso: python verificar_pbir.py nuevo.pbix referencia_guardada_por_desktop.pbix [modelo_<archivo>.json]
Comprueba: ZIP íntegro, DataModel idéntico a la referencia, tema personalizado registrado, orden y visibilidad de páginas,
z únicos, visuales dentro de la página, interacciones y navegación a ids existentes, ningún alias (Source) en consultas,
selectores con queryRef presente, alturas mínimas de texto, rutas JSON que Desktop nunca escribe (comparando con la
referencia) y, si se da el modelo (salida de leer_modelo.py), que cada Measure/Column exista."""
import zipfile, json, sys, collections, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from componentes import alto_min, piso_cli, _padding

def rutas(o, p='', out=None):
    out = set() if out is None else out
    if isinstance(o, dict):
        for k, v in o.items():
            kk = '*' if p.endswith(('properties', 'objects', 'visualContainerObjects', 'queryState')) else k
            out.add((p + '/' + kk, type(v).__name__)); rutas(v, p + '/' + kk, out)
    elif isinstance(o, list):
        for v in o: rutas(v, p + '[]', out)
    return out

def verificar(nuevo, referencia, modelo=None):
    B, z = zipfile.ZipFile(referencia), zipfile.ZipFile(nuevo)
    err, info = [], []
    if z.testzip(): err.append(('zip dañado', z.testzip()))
    if z.read('DataModel') != B.read('DataModel'): info.append('DataModel distinto de la referencia (¿se esperaba?)')
    cols = meds = None
    if modelo:
        s = (lambda d: d.get('modelo') or d['sqlite'])(json.load(open(modelo, encoding='utf-8')))
        cols = {(c['tabla'], c['columna']) for c in s.get('columnas', [])}; meds = {(m['tabla'], m['medida']) for m in s.get('medidas', [])}
    ref = set().union(*[rutas(json.loads(B.read(n))) for n in B.namelist() if n.endswith('visual.json')])
    tipos_ref = {json.loads(B.read(n))['visual'].get('visualType') for n in B.namelist() if n.endswith('visual.json')}
    r = json.loads(z.read('Report/definition/report.json'))
    ct = r.get('themeCollection', {}).get('customTheme')
    if ct and f"Report/StaticResources/RegisteredResources/{ct['name']}" not in z.namelist(): err.append(('tema sin archivo', ct['name']))
    pj = json.loads(z.read('Report/definition/pages/pages.json')); ids = pj['pageOrder']
    for pid in ids:
        pg = json.loads(z.read(f'Report/definition/pages/{pid}/page.json'))
        vis = [json.loads(z.read(n)) for n in z.namelist() if n.startswith(f'Report/definition/pages/{pid}/visuals/')]
        vids = {v['name'] for v in vis}
        info.append(f"{pg['displayName']}: {pg['width']}x{pg['height']} {pg.get('displayOption')} {pg.get('visibility', 'visible')} "
                    f"{dict(collections.Counter(v['visual']['visualType'] for v in vis))}")
        if any(n > 1 for n in collections.Counter(v['position']['z'] for v in vis).values()): err.append(('z repetido', pg['displayName']))
        for i in pg.get('visualInteractions', []):
            if i['source'] not in vids or i['target'] not in vids: err.append(('interacción rota', pg['displayName'], i))
        for v in vis:
            pos, vv, t = v['position'], v['visual'], v['visual']['visualType']
            if pos['x'] + pos['width'] > pg['width'] + 0.5 or pos['y'] + pos['height'] > pg['height'] + 0.5:
                err.append(('fuera de página', pg['displayName'], t, v['name']))
            q = vv.get('query', {}); refs = {x['queryRef'] for r_ in q.get('queryState', {}).values() for x in r_['projections']}
            if '"Source"' in json.dumps(q): err.append(('alias Source en la consulta (PBIR no abre)', v['name']))
            if cols is not None:
                for k, e, pr in re.findall(r'"(Measure|Column)": \{"Expression": \{"SourceRef": \{"Entity": "([^"]+)"\}\}, "Property": "([^"]+)"',
                                           json.dumps(vv, ensure_ascii=False)):
                    if (e, pr) not in (meds if k == 'Measure' else cols): err.append(('campo inexistente', k, f'{e}[{pr}]', pg['displayName']))
            for obj in vv.get('objects', {}).values():
                for it in obj:
                    m = (it.get('selector') or {}).get('metadata')
                    if m and m not in refs: err.append(('selector huérfano', v['name'], m))
            vl = vv.get('visualContainerObjects', {}).get('visualLink')
            if vl:
                sec = vl[0]['properties'].get('navigationSection', {}).get('expr', {}).get('Literal', {}).get('Value', '').strip("'")
                if sec and sec not in ids: err.append(('navegación a página inexistente', v['name'], sec))
            if t in tipos_ref:
                nuevas = {x for x in rutas(v) if x not in ref and '/expr' not in x[0] and '/solid' not in x[0] and 'paragraphs' not in x[0]}
                if nuevas: err.append(('ruta JSON que Desktop no escribe', t, sorted(nuevas)[:3]))
            else:
                info.append(f'tipo {t} sin ejemplo en la referencia: revisar en pantalla')
            if t == 'textbox':
                for par in vv.get('objects', {}).get('general', [{}])[0].get('properties', {}).get('paragraphs', []):
                    for tr in par.get('textRuns', []):
                        fs = tr.get('textStyle', {}).get('fontSize')
                        if fs and tr.get('value') and fs.endswith('pt'):
                            px = float(fs[:-2]) / 0.75
                            if pos['height'] < alto_min(px) - 0.5: err.append(('texto con poca altura (tendrá scroll)', tr['value'][:30]))
                            elif pos['height'] < piso_cli(float(fs[:-2]), *_padding(vv.get('visualContainerObjects'))) - 0.5:
                                info.append(f"aviso: textbox de {pos['height']:.0f} px bajo el piso del CLI ({piso_cli(float(fs[:-2]), *_padding(vv.get('visualContainerObjects'))):.0f} px) — conservador, revisar en pantalla")
    return err, sorted(set(info), key=info.index)

if __name__ == '__main__':
    from comun import ayuda; ayuda(__doc__, 2)
    e, i = verificar(*sys.argv[1:4])
    print('\n'.join(i)); print('ERRORES:', e if e else 'ninguno')
