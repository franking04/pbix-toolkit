"""Verificación previa a entregar un .pbix modificado, en Layout clásico o PBIR, con reglas de la plataforma de destino.
Uso: python verificar_pbix.py nuevo.pbix referencia.pbix [modelo_<archivo>.json] [--destino=rs:2026.05|servicio] [--cli]
  Siempre: validación por catálogo (catalogo.py: objetos, propiedades, enums, tipos de literal, tema, soporte en RS) y
  resumen de la auditoría [P] de diseño (auditoria.py; avisos, no errores).
  --cli: además `powerbi-report-author validate` del CLI de Microsoft (solo PBIR; se omite con aviso si no está instalado).
  referencia = el archivo del que partiste, guardado por Power BI Desktop (para Report Server: el guardado por el Desktop para RS).
  destino por defecto = la plataforma y release que guardaron la referencia.
PBIR: delega en verificar_pbir.py. Layout clásico: ZIP íntegro, DataModel/Version/Metadata iguales a la referencia, sin partes PBIR,
z únicos, visuales dentro de la página, interacciones y navegación válidas, campos existentes en el modelo, selectores huérfanos,
alturas mínimas de texto, tema registrado y rutas de config que Desktop no escribe. Ambos: compatibilidad con la plataforma."""
import zipfile, json, sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plataforma
from componentes import alto_min, piso_cli, _padding

PATRON = r'"(Measure|Column)":\s*\{"Expression":\s*\{"SourceRef":\s*\{"(?:Source|Entity)":\s*"([^"]+)"\}\},\s*"Property":\s*"([^"]+)"'

def _layout(z): return json.loads(z.read('Report/Layout').decode('utf-16-le').lstrip('﻿'))

def _rutas(o, p='', out=None):
    out = set() if out is None else out
    if isinstance(o, dict):
        for k, v in o.items():
            kk = '*' if p.endswith(('properties', 'objects', 'vcObjects', 'projections')) else k
            out.add((p + '/' + kk, type(v).__name__)); _rutas(v, p + '/' + kk, out)
    elif isinstance(o, list):
        for v in o: _rutas(v, p + '[]', out)
    return out

def _visuales(L):
    for s in L['sections']:
        for c in s['visualContainers']:
            yield s, c, json.loads(c.get('config') or '{}')

def verificar_layout(nuevo, referencia, modelo=None):
    B, z = zipfile.ZipFile(referencia), zipfile.ZipFile(nuevo)
    err, info = [], []
    if z.testzip(): err.append(('zip dañado', z.testzip()))
    for parte in ('DataModel', 'Version', 'Metadata'):
        if parte in B.namelist() and (parte not in z.namelist() or z.read(parte) != B.read(parte)):
            (info if parte == 'DataModel' else err).append(f'{parte} distinto de la referencia')
    if any(n.startswith('Report/definition/') for n in z.namelist()): err.append(('partes PBIR dentro de un archivo clásico',))
    cols = meds = None
    if modelo:
        d = json.load(open(modelo, encoding='utf-8')); sq = d.get('modelo') or d['sqlite']   # TMDL o pbixray
        cols = {(c['tabla'], c['columna']) for c in sq.get('columnas', [])}; meds = {(m['tabla'], m['medida']) for m in sq.get('medidas', [])}
    L, LB = _layout(z), _layout(B)
    ref = collections.defaultdict(set)
    for _, _, c in _visuales(LB):
        sv = c.get('singleVisual', {}); ref[sv.get('visualType')] |= _rutas(sv)
    cfg = json.loads(L.get('config') or '{}')
    ct = cfg.get('themeCollection', {}).get('customTheme')
    if ct and not any(n.endswith('/' + ct['name']) for n in z.namelist()): err.append(('tema sin archivo', ct['name']))
    nombres = {s['name'] for s in L['sections']}
    for s in L['sections']:
        sc = json.loads(s.get('config') or '{}'); conts = s['visualContainers']
        vis = [json.loads(c.get('config') or '{}') for c in conts]; vids = {v.get('name') for v in vis}
        info.append(f"{s['displayName']}: {s['width']}x{s['height']} vista={s.get('displayOption')} "
                    f"{'oculta' if sc.get('visibility') == 1 else 'visible'} "
                    f"{dict(collections.Counter(v.get('singleVisual', {}).get('visualType', 'grupo') for v in vis))}")
        if any(n > 1 for n in collections.Counter(c.get('z') for c in conts).values()): err.append(('z repetido', s['displayName']))
        for r in sc.get('relationships', []):
            if r.get('source') not in vids or r.get('target') not in vids: err.append(('interacción rota', s['displayName'], r))
        for c, v in zip(conts, vis):
            sv = v.get('singleVisual'); 
            if not sv: continue
            t = sv.get('visualType')
            if c['x'] + c['width'] > s['width'] + 0.5 or c['y'] + c['height'] > s['height'] + 0.5:
                err.append(('fuera de página', s['displayName'], t, v.get('name')))
            alias = {f['Name']: f['Entity'] for f in sv.get('prototypeQuery', {}).get('From', [])}
            txt = json.dumps(sv, ensure_ascii=False)
            if cols is not None:
                for k, e, pr in re.findall(PATRON, txt):
                    e = alias.get(e, e)
                    if (e, pr) not in (meds if k == 'Measure' else cols): err.append(('campo inexistente', k, f'{e}[{pr}]', s['displayName']))
            refs = {p_['queryRef'] for r_ in sv.get('projections', {}).values() for p_ in r_}
            for obj in sv.get('objects', {}).values():
                for it in obj:
                    m = (it.get('selector') or {}).get('metadata')
                    if m and m not in refs: err.append(('selector huérfano', v.get('name'), m))
            vl = sv.get('vcObjects', {}).get('visualLink')
            if vl:
                sec = vl[0].get('properties', {}).get('navigationSection', {}).get('expr', {}).get('Literal', {}).get('Value', '').strip("'")
                if sec and sec not in nombres: err.append(('navegación a página inexistente', v.get('name'), sec))
            if t in ref:
                nuevas = {x for x in _rutas(sv) if x not in ref[t] and not re.search(r'/expr|/solid|paragraphs|prototypeQuery|/query|/columnProperties', x[0])}
                if nuevas: info.append(f'{t}: rutas sin ejemplo en la referencia {sorted(nuevas)[:2]} (revisar en pantalla)')
            else:
                info.append(f'tipo {t} sin ejemplo en la referencia: revisar en pantalla')
            if t == 'textbox':
                for par in sv.get('objects', {}).get('general', [{}])[0].get('properties', {}).get('paragraphs', []):
                    for tr in par.get('textRuns', []):
                        fs = tr.get('textStyle', {}).get('fontSize')
                        if fs and tr.get('value') and str(fs).endswith('pt'):
                            px = float(fs[:-2]) / 0.75
                            if c['height'] < alto_min(px) - 0.5: err.append(('texto con poca altura (tendrá scroll)', tr['value'][:30]))
                            elif c['height'] < piso_cli(float(fs[:-2]), *_padding(sv.get('vcObjects'))) - 0.5:
                                info.append(f"aviso: textbox de {c['height']:.0f} px bajo el piso del CLI ({piso_cli(float(fs[:-2]), *_padding(sv.get('vcObjects'))):.0f} px) — conservador, revisar en pantalla")
    return err, sorted(set(info), key=info.index)

def tipos_y_extras(ruta):
    z = zipfile.ZipFile(ruta); n = z.namelist()
    if 'Report/Layout' in n:
        L = _layout(z); cfg = json.loads(L.get('config') or '{}')
        tipos = [c.get('singleVisual', {}).get('visualType') for _, _, c in _visuales(L)]
        marcadores = bool(cfg.get('bookmarks'))
    else:
        tipos = [json.loads(z.read(x))['visual'].get('visualType') for x in n if x.endswith('visual.json')]
        marcadores = any('/bookmarks/' in x for x in n)
    cv = {x.split('/')[2] for x in n if x.startswith('Report/CustomVisuals/')}
    return [t for t in tipos if t], marcadores, cv

# Diagnósticos del CLI que en pantalla resultaron inofensivos [probado: capturas]: se reportan como aviso.
CLI_AVISO = {'PBIR_THEME_FILE_NAME_MISMATCH', 'PBIR_TEXTBOX_HEIGHT_BELOW_FLOOR', 'PBIR_SCHEMA_UNREACHABLE'}

def validar_cli(nuevo):
    """Corre `powerbi-report-author validate` sobre el PBIR del .pbix. validate solo acepta PBIP: se extrae
    Report/definition + Report/StaticResources a una carpeta temporal X.Report con definition.pbir y .platform mínimos
    (equivale a Guardar como .pbip en el Desktop [probado: mismos diagnósticos]). Devuelve (errores, avisos)."""
    import shutil, subprocess, tempfile, uuid
    exe = shutil.which('powerbi-report-author')
    if not exe: return [], ['--cli: powerbi-report-author no está instalado (npm install -g @microsoft/powerbi-report-authoring-cli): omitido']
    z = zipfile.ZipFile(nuevo)
    if not any(n.startswith('Report/definition/') for n in z.namelist()): return [], ['--cli: solo aplica a PBIR (archivo clásico): omitido']
    nombre = re.sub(r'[^A-Za-z0-9_-]', '_', os.path.splitext(os.path.basename(nuevo))[0])
    with tempfile.TemporaryDirectory() as tmp:
        rep = os.path.join(tmp, nombre + '.Report')
        for i in z.infolist():
            partes = i.filename.split('/')
            if '..' in partes or i.filename.startswith('/'): continue          # nunca escribir fuera de la carpeta temporal
            if i.filename.startswith(('Report/definition/', 'Report/StaticResources/')) and not i.filename.endswith('/'):
                d = os.path.join(rep, *i.filename.split('/')[1:]); os.makedirs(os.path.dirname(d), exist_ok=True)
                open(d, 'wb').write(z.read(i))
        json.dump({'$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json',
                   'version': '4.0', 'datasetReference': {'byPath': {'path': f'../{nombre}.SemanticModel'}}},
                  open(os.path.join(rep, 'definition.pbir'), 'w', encoding='utf-8'))
        json.dump({'$schema': 'https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json',
                   'metadata': {'type': 'Report', 'displayName': nombre}, 'config': {'version': '2.0', 'logicalId': str(uuid.uuid4())}},
                  open(os.path.join(rep, '.platform'), 'w', encoding='utf-8'))
        out = os.path.join(tmp, 'validate.json')
        subprocess.run([exe, 'validate', rep, '--out', out], capture_output=True, text=True)
        if not os.path.exists(out): return [], ['--cli: validate no produjo salida']
        diag = json.load(open(out, encoding='utf-8')).get('data', {}).get('diagnostics', {})
    err, avi = [], []
    for cod, d in diag.items():
        for it in d.get('items', []):
            msg = re.sub(r':\s*[A-Za-z]:\\.*$', '', it.get('message', ''))[:200]
            dest = avi if (d.get('severity') != 'error' or cod in CLI_AVISO) else err
            dest.append(f'CLI {cod}: {msg}')
    return err, sorted(set(avi), key=avi.index)

def medidas_incrustadas(ruta):
    """{(tabla, medida)} que crean las pestañas TMDL incrustadas (scripts_modelo.incrustar) y que aún no están en el modelo
    hasta que el usuario pulse Aplicar."""
    z = zipfile.ZipFile(ruta); out = set()
    for n in z.namelist():
        if n.startswith('TMDLScripts/') and n.endswith('.tmdl'):
            raw = z.read(n); txt = raw.decode('utf-16-le' if raw[1:2] == b'\x00' else 'utf-8-sig', errors='ignore')
            tabla = None
            for l in txt.splitlines():
                m = re.match(r"\s*ref table ('(?:[^']|'')*'|\S+)", l) or re.match(r"\s*table ('(?:[^']|'')*'|\S+)", l)
                if m: tabla = m.group(1).strip("'").replace("''", "'"); continue
                m = re.match(r"\s*measure ('(?:[^']|'')*'|[^\s=]+)", l)
                if m and tabla: out.add((tabla, m.group(1).strip("'").replace("''", "'")))
    return out

def verificar(nuevo, referencia, modelo=None, destino=None, cli=False):
    n = zipfile.ZipFile(nuevo).namelist()
    if any(x.startswith('Report/definition/') for x in n):
        from verificar_pbir import verificar as v_pbir
        err, info = v_pbir(nuevo, referencia, modelo)
    else:
        err, info = verificar_layout(nuevo, referencia, modelo)
    pend = medidas_incrustadas(nuevo)   # medidas de la pestaña TMDL incrustada: pendientes de Aplicar, no inexistentes
    if pend:
        ya = [e for e in err if e[0] == 'campo inexistente' and e[1] == 'Measure' and tuple(re.match(r'(.+)\[(.+)\]$', e[2]).groups()) in pend]
        err = [e for e in err if e not in ya]
        if ya: info.append(f"{len({e[2] for e in ya})} medidas usadas en visuales se crean con la pestaña TMDL incrustada (pendientes de Aplicar): "
                           + ', '.join(sorted({e[2] for e in ya})))
    pi = plataforma.detectar(nuevo)
    destino = destino or plataforma.destino_por_defecto(plataforma.detectar(referencia))
    tipos, marc, cv = tipos_y_extras(nuevo)
    e2, a2 = plataforma.revisar(pi, destino, tipos, marc, cv)
    info.insert(0, f"plataforma: {pi['guardado_por']} {pi['release']} · archivo {pi['version_archivo']} · {pi['formato_reporte']} · destino {destino}")
    import catalogo
    e3, a3 = catalogo.validar_pbix(nuevo, destino)
    e3 = [('catálogo', x) for x in e3]; a3 = ['catálogo: ' + x for x in a3]
    if destino and destino.startswith('rs'):
        a3.insert(0, 'catálogo: describe la nube/PBIR; para Report Server es referencia (el Desktop para RS 2026.05 dio 0 errores con él)')
    import auditoria   # guia_diseno §10, fase [P]: avisos de diseño (no bloquean)
    au = auditoria.auditar(nuevo)
    a3.append(f"auditoría [P]: crítico {len(au['critico'])} · refinamiento {len(au['refinamiento'])} · pulido {len(au['pulido'])} "
              f"(detalle: python scripts/auditoria.py {os.path.basename(nuevo)})")
    a3 += ['auditoría crítico: ' + x for x in au['critico']]
    e4, a4 = validar_cli(nuevo) if cli else ([], [])
    return err + e2 + e3 + [('CLI', x) for x in e4], info + a2 + a3 + a4

if __name__ == '__main__':
    from comun import ayuda; ayuda(__doc__, 2)
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    d = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--destino=')), None)
    e, i = verificar(*args[:3], destino=d, cli='--cli' in sys.argv)
    print('\n'.join(i)); print('ERRORES:', e if e else 'ninguno')
