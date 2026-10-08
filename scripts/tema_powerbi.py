"""Genera temas de Power BI (JSON de tema del reporte) para las direcciones visuales de references/diseno_reportes.md
y, opcionalmente, los inyecta en un .pbix PBIR.
Uso:
  python tema_powerbi.py moderno|minimalista|oscuro|corporativo salida.json   (moderno = por defecto; corporativo retirado)
  python tema_powerbi.py marca salida.json --colores "#hex,#hex,..." [--fondo "#F5F5F5"] [--texto "#222222"]
  python tema_powerbi.py corporativo tema.json --aplicar entrada_pbir.pbix salida.pbix
Importación manual (siempre funciona): Power BI Desktop → Vista → Temas → Examinar temas → elegir el JSON.
Las paletas de las direcciones se validaron con el validador de la skill `dataviz` (CVD y contraste); una paleta de marca
debe validarse igual antes de usarla."""
import json, sys, zipfile, argparse, re, unicodedata, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ESTADO = {'good': '#0ca30c', 'neutral': '#fab219', 'bad': '#d03b3b'}
F_REG = "'Segoe UI', wf_segoe-ui_normal, helvetica, arial, sans-serif"
F_SEMI = "'Segoe UI Semibold', wf_segoe-ui_semibold, helvetica, arial, sans-serif"
F_BOLD = "'Segoe UI Bold', wf_segoe-ui_bold, helvetica, arial, sans-serif"

DIRECCIONES = {
    'moderno': dict(  # POR DEFECTO. Tokens de references/disenos/README.md; categóricos = referencia dataviz (CVD ≥ 9.1)
        colores=['#2A78D6', '#EB6834', '#1BAF7A', '#EDA100', '#E87BA4', '#008300', '#4A3AA7', '#E34948'],
        pagina='#F5F6F8', superficie='#FFFFFF', texto='#101828', texto2='#475467', linea='#E4E7EC',
        acento='#2A78D6', radio=8, sombra=False,
        enc_fondo='#F5F6F8', enc_texto='#101828', enc_sub='#475467', enc_kicker='#8A94A6', enc_linea='#E4E7EC',
        enfasis='#2A78D6', mejor='#2A78D6', contexto='#B8C0CC', sube='#12805C', baja='#C4320A'),
    'corporativo': dict(  # validada (light, superficie #FFFFFF): CVD ≥ 9.2, normal ≥ 19.3; oro y rosa < 3:1 → etiquetas visibles
        colores=['#2F5D9E', '#D4A72C', '#D77FA3', '#5E9A35', '#8466B8', '#E08A2E', '#1F8A70', '#C2553A'],
        pagina='#F2F4F8', superficie='#FFFFFF', texto='#13315C', texto2='#5B6B82', linea='#DDE3EC',
        acento='#13315C', radio=8, sombra=False,
        enc_fondo='#0B2545', enc_texto='#FFFFFF', enc_sub='#B9C6D8', enc_kicker='#C9A227', enc_linea='#C9A227',
        enfasis='#13315C', mejor='#C9A227', contexto='#B7BDC7', sube='#1E7A3C', baja='#C0392B'),
    'minimalista': dict(  # paleta de referencia de dataviz (light): CVD ≥ 9.1, normal ≥ 19.6
        colores=['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948'],
        pagina='#FFFFFF', superficie='#FFFFFF', texto='#0b0b0b', texto2='#52514e', linea='#E6E5E1',
        acento='#2a78d6', radio=4, sombra=False,
        enc_fondo='#FFFFFF', enc_texto='#0b0b0b', enc_sub='#52514e', enc_kicker='#2a78d6', enc_linea='#E6E5E1',
        enfasis='#2a78d6', mejor='#eb6834', contexto='#c3c2b7', sube='#1E7A3C', baja='#C0392B'),
    'oscuro': dict(  # variante oscura de dataviz (superficie #1a1a19): CVD ≥ 8.4, todas ≥ 3:1
        colores=['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#008300', '#9085e9', '#e66767'],
        pagina='#111110', superficie='#1a1a19', texto='#FFFFFF', texto2='#c3c2b7', linea='#383835',
        acento='#3987e5', radio=8, sombra=False,
        enc_fondo='#1a1a19', enc_texto='#FFFFFF', enc_sub='#c3c2b7', enc_kicker='#3987e5', enc_linea='#383835',
        enfasis='#3987e5', mejor='#c98500', contexto='#55554f', sube='#3fbf6a', baja='#e66767'),
}

def solid(c): return {'solid': {'color': c}}

def _desde_tokens():
    """Direcciones vigentes (moderno, editorial, suizo, grafito; aurora y vidrio = 2 capas) desde references/tokens.json: misma fuente que los
    diseños HTML de referencia. Sin tarjetas → visuales sin borde y con el fondo de la página."""
    import os
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'references', 'tokens.json')
    if not os.path.exists(ruta): return {}
    try:   # tokens fijos + direcciones a la medida (PBIX_TOKENS_EXTRA, ver estilo_a_medida.py)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from estilo_a_medida import cargar_tokens
        tk = cargar_tokens(ruta)
    except ImportError:
        tk = json.load(open(ruta, encoding='utf-8'))
    out = {}
    for n, d in tk['direcciones'].items():
        sup = d['superficie'] if d['tarjetas'] else d['pagina']
        out[n] = dict(colores=d['categoricos'], pagina=d['pagina'], superficie=sup, texto=d['tinta'], texto2=d['tinta2'],
                      texto3=d['tinta3'], linea=d['linea'], acento=d['acento'], radio=d.get('radio', tk['radio']), sombra=False,
                      tarjetas=d['tarjetas'], fuente_titulo=d['fuente_titulo'], fuente_kpi=d['fuente_kpi'],
                      enc_fondo=d['pagina'], enc_texto=d['tinta'], enc_sub=d['tinta3'], enc_kicker=d['tinta2'], enc_linea=d['linea'],
                      enfasis=d['acento'], mejor=d['acento'], contexto=d['contexto'], contexto_suave=d['contexto_suave'],
                      sube=d['bien'], baja=d['mal'], alerta=d['alerta'], escala=tk['escala_pt'], capas=d.get('capas', 1))
    return out

HISTORICAS = dict(DIRECCIONES)            # corporativo (no por defecto: tiende a verse anticuada), minimalista, oscuro
DIRECCIONES.update(_desde_tokens())       # vigentes: moderno (por defecto), editorial, suizo, grafito, aurora, vidrio

def tema(nombre, d):
    t, t2, sup, lin = d['texto'], d['texto2'], d['superficie'], d['linea']
    dos = d.get('capas', 1) == 2   # 2 capas: la caja del visual está pintada en la imagen de fondo → visual transparente
    ejes = {'categoryAxis': [{'showAxisTitle': False, 'labelColor': solid(t2), 'fontSize': 9}],
            'valueAxis': [{'showAxisTitle': False, 'labelColor': solid(t2), 'fontSize': 9, 'gridlineColor': solid(lin)}],
            'legend': [{'labelColor': solid(t2), 'fontSize': 9}],
            'labels': [{'color': solid(t), 'fontSize': 9}]}
    # scatterChart no tiene 'labels' (catálogo del CLI de Microsoft): sus etiquetas son 'categoryLabels'
    ejes_disp = {k: v for k, v in ejes.items() if k != 'labels'} | {'categoryLabels': [{'color': solid(t), 'fontSize': 9}]}
    tabla = {'grid': [{'gridVertical': False, 'gridHorizontal': True, 'gridHorizontalColor': solid(lin), 'rowPadding': 5,
                       'outlineColor': solid(sup)}],
             # 'outline' (Bottom/None) no existe en el esquema de tableEx/pivotTable: la propiedad es 'outlineStyle'
             # (número de banderas, valores por validar), así que solo se fija el color.
             'columnHeaders': [{'fontColor': solid(t2), 'backColor': solid(sup), 'fontFamily': F_SEMI, 'fontSize': 9,
                                'outlineColor': solid(lin)}],
             'values': [{'fontColor': solid(t), 'backColorPrimary': solid(sup), 'backColorSecondary': solid(sup), 'fontSize': 10}],
             'total': [{'fontColor': solid(t), 'backColor': solid(d['pagina']), 'fontFamily': F_BOLD}]}
    if dos:
        tabla['columnHeaders'][0].pop('backColor', None); tabla['values'][0].pop('backColorPrimary', None)
        tabla['values'][0].pop('backColorSecondary', None); tabla['total'][0].pop('backColor', None)
        tabla['grid'][0].pop('outlineColor', None)
    return {
        'name': nombre,
        'dataColors': d['colores'],
        'background': sup, 'foreground': t, 'tableAccent': d['acento'],
        **ESTADO,
        'maximum': d['colores'][0], 'center': lin, 'minimum': '#FFFFFF' if sup != '#1a1a19' else '#383835',
        'textClasses': {
            'callout': {'fontSize': d.get('escala', {}).get('kpi', 24), 'fontFace': F_BOLD, 'color': t},
            'title': {'fontSize': d.get('escala', {}).get('titulo_visual', 12), 'fontFace': F_SEMI, 'color': t},
            'header': {'fontSize': 11, 'fontFace': F_SEMI, 'color': t},
            'label': {'fontSize': 9, 'fontFace': F_REG, 'color': t2}},
        'visualStyles': {
            # OJO [probado]: no definir 'padding' ni 'title.show' en '*': el relleno global reduce el área útil de
            # textbox y tarjetas y Power BI les pone barra de desplazamiento ("cuadritos" a la derecha del texto).
            '*': {'*': {
                'background': [{'show': not dos, 'color': solid(sup), 'transparency': 0}],
                'border': [{'show': (not dos) and d.get('tarjetas', True) and lin != sup, 'color': solid(lin), 'radius': d['radio']}],
                'dropShadow': [{'show': d['sombra']}],
                'title': [{'fontColor': solid(t), 'fontSize': d.get('escala', {}).get('titulo_visual', 12), 'fontFamily': F_SEMI}]}},
            'page': {'*': {'background': [{'color': solid(d['pagina']), 'transparency': 0}],
                           'outspace': [{'color': solid(d['pagina']), 'transparency': 0}]}},
            'textbox': {'*': {'background': [{'show': False}], 'border': [{'show': False}], 'title': [{'show': False}]}},
            'image': {'*': {'background': [{'show': False}], 'border': [{'show': False}], 'title': [{'show': False}]}},
            'basicShape': {'*': {'background': [{'show': False}], 'border': [{'show': False}], 'title': [{'show': False}]}},
            'actionButton': {'*': {'background': [{'show': False}], 'border': [{'show': False}], 'title': [{'show': False}]}},
            'card': {'*': {'labels': [{'color': solid(t), 'fontSize': d.get('escala', {}).get('kpi', 24), 'fontFamily': F_BOLD}],
                           'categoryLabels': [{'color': solid(t2), 'fontSize': 10}]}},
            'tableEx': {'*': tabla}, 'pivotTable': {'*': tabla},
            'slicer': {'*': {'header': [{'fontColor': solid(t), 'fontFamily': F_SEMI}], 'items': [{'fontColor': solid(t)}]}},
            **{v: {'*': ejes} for v in ('lineChart', 'clusteredColumnChart', 'clusteredBarChart', 'columnChart', 'barChart',
                                         'areaChart', 'lineClusteredColumnComboChart', 'waterfallChart')},
            'scatterChart': {'*': ejes_disp}}}

def nombre_archivo_tema(nombre):
    """Nombre del archivo del tema derivado de su 'name' (sin espacios ni acentos): 'Tema Marca Demo' -> 'TemaMarcaDemo.json'.
    El Desktop, al importar, nombra el archivo como el tema; el CLI de Microsoft marca error si no coinciden
    (PBIR_THEME_FILE_NAME_MISMATCH: compara el "name" del JSON con customTheme.name, que debe llevar ".json"). Con nombres
    distintos el tema igual se aplicó [probado], pero aplicar_tema_pbir/tema_personalizado los igualan."""
    base = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode()
    return re.sub(r'[^A-Za-z0-9_-]', '', base) + '.json'

def validar(tema_json):
    """Valida visualStyles contra references/catalogo (objeto y propiedad existen, enum válido). Devuelve (errores, avisos)."""
    import catalogo
    return catalogo.validar_tema(tema_json)

def aplicar_tema_pbir(entrada, salida, tema_json, nombre_archivo=None):
    """[probado: Power BI abrió el archivo y lo volvió a guardar conservando el tema] Registra el tema como recurso
    del reporte PBIR y lo marca como tema personalizado. nombre_archivo por defecto = nombre_archivo_tema(tema['name'])."""
    nombre_archivo = nombre_archivo or nombre_archivo_tema(tema_json['name'])
    # El CLI exige name del JSON == customTheme.name == item de resourcePackages, con ".json" (PBIR_THEME_FILE_NAME_MISMATCH)
    tema_json = dict(tema_json, name=nombre_archivo)
    zin = zipfile.ZipFile(entrada)
    if not any(n.startswith('Report/definition/') for n in zin.namelist()):
        raise SystemExit('Solo PBIR. En formato clásico importa el JSON desde Vista → Temas → Examinar temas.')
    rep = json.loads(zin.read('Report/definition/report.json'))
    base = rep['themeCollection']['baseTheme']
    rep['themeCollection']['customTheme'] = {'name': nombre_archivo, 'reportVersionAtImport': base.get('reportVersionAtImport'),
                                             'type': 'RegisteredResources'}
    pk = next((p for p in rep.setdefault('resourcePackages', []) if p['name'] == 'RegisteredResources'), None)
    if pk is None:
        pk = {'name': 'RegisteredResources', 'type': 'RegisteredResources', 'items': []}; rep['resourcePackages'].append(pk)
    viejos = {i.get('path') for i in pk['items'] if i.get('type') == 'CustomTheme'}     # un solo tema personalizado
    pk['items'] = [i for i in pk['items'] if i.get('type') != 'CustomTheme'] + \
                  [{'name': nombre_archivo, 'path': nombre_archivo, 'type': 'CustomTheme'}]
    destino_tema = 'Report/StaticResources/RegisteredResources/' + nombre_archivo
    descartar = {'Report/StaticResources/RegisteredResources/' + v for v in viejos} | {destino_tema}
    with zipfile.ZipFile(salida, 'w') as zout:
        for info in zin.infolist():
            n = info.filename
            if n == 'SecurityBindings' or n in descartar: continue
            data = zin.read(n)
            if n == 'Report/definition/report.json':
                data = json.dumps(rep, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
            elif n == '[Content_Types].xml':
                data = data.decode('utf-8-sig').replace('<Override PartName="/SecurityBindings" ContentType="" />', '').encode('utf-8')
            zi = zipfile.ZipInfo(n, date_time=info.date_time); zi.compress_type = info.compress_type
            zout.writestr(zi, data)
        zi = zipfile.ZipInfo(destino_tema, date_time=zin.getinfo('Report/definition/report.json').date_time)
        zi.compress_type = zipfile.ZIP_DEFLATED
        zout.writestr(zi, json.dumps(tema_json, ensure_ascii=False, indent=1).encode('utf-8'))

if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('direccion', choices=list(DIRECCIONES) + ['marca']); a.add_argument('salida')
    a.add_argument('--colores'); a.add_argument('--fondo', default='#F5F6F8'); a.add_argument('--texto', default='#1F2A37')
    a.add_argument('--aplicar', nargs=2, metavar=('ENTRADA_PBIR', 'SALIDA_PBIX'))
    x = a.parse_args()
    if x.direccion == 'marca':
        if not x.colores: raise SystemExit('--colores es obligatorio para "marca" (valídalos antes con dataviz)')
        d = dict(DIRECCIONES['corporativo'], colores=[c.strip() for c in x.colores.split(',')], pagina=x.fondo,
                 texto=x.texto, acento=x.colores.split(',')[0].strip())
    else:
        d = DIRECCIONES[x.direccion]
    nombre = f'Tema {x.direccion}'
    t = tema(nombre, d)
    e, w = validar(t)
    if e: raise SystemExit('tema con errores frente al catálogo: ' + '; '.join(e))
    open(x.salida, 'w', encoding='utf-8').write(json.dumps(t, ensure_ascii=False, indent=1))
    print('tema escrito:', x.salida, '| colores:', ', '.join(t['dataColors']))
    if x.aplicar:
        aplicar_tema_pbir(x.aplicar[0], x.aplicar[1], t)
        print('tema inyectado en', x.aplicar[1])
