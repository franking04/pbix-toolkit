"""Plantillas Vega-Lite para el visual Deneb (certificado, AppSource): 1–2 «visuales firma» por página en los niveles
realzado e impactante, cuando lo nativo no alcanza (área con degradado, anillo, bullet por categoría, mancuerna).
Colores y tipografía desde references/tokens.json (misma dirección que el tema y el fondo).

Cómo se usa (manual; se dibuja en RS 2026.05 con el .pbiviz importado y en la nube [probado]):
  1. Insertar Deneb (servicio: AppSource; Report Server: importar el .pbiviz desde archivo, viaja dentro del .pbix).
  2. Arrastrar los campos a «Values» y renombrarlos EN EL VISUAL exactamente como los pide la plantilla
     (p. ej. Mes, Orden, Valor, Comparación). 'Orden' = columna numérica para ordenar el eje (AñoMes, n.º de mes).
  3. Editar → proveedor Vega-Lite → pegar el JSON → Aplicar. En 2 capas: Formato → Fondo del visual desactivado.
  4. Formato de números: por defecto formatType "pbiFormat" (cadena de Power BI), que sigue la cultura como el resto del reporte
     (en el Desktop en español sale «37.600,6» [probado]). Con --formato d3 se fija
     estilo US ('$,.1f', ',.0f', '.0%'), solo si el usuario pide un locale fijo.
Regla: Deneb no hereda el tema; si cambias de dirección vuelve a generar la plantilla.
Compilación [probado: vega-lite 6.4.3 + vega 6.4.0]: las 12 plantillas pasan el
esquema de Vega-Lite, compilan sin avisos y se dibujan con datos ficticios. Corregido: config.background null → 'transparent',
config.customFormatTypes: true (sin él Vega-Lite descarta pbiFormat), sort con op min/max en capas (sum se descarta), y el arco
del anillo con theta (theta2 solo no compila). En el visual Deneb se ven en RS 2026.05 y nube [probado]; pbiFormat
usa la cultura del modelo (p. ej. «37.600,6» en un modelo en español). Se guarda como visualType deneb7E15AEF80B9E4D4F8E12924291ECE89A
con objects.vega[0].properties.jsonSpec (la plantilla como texto) y el paquete en Report/CustomVisuals/.
Uso: python deneb.py aurora carpeta_salida [--formato d3]   → escribe area_degradado.json, anillo.json, bullet.json, mancuerna.json"""
import json, os, sys

_TOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'references', 'tokens.json')
VL = 'https://vega.github.io/schema/vega-lite/v5.json'


MODO_FORMATO = 'pbi'         # 'pbi' (por defecto: pbiFormat, sigue la cultura como el resto del reporte) | 'd3' (estilo US fijo)
FORMATOS = {'moneda': ('$,.1f', '$#,0.0'), 'moneda0': ('$,.0f', '$#,0'), 'entero': (',.0f', '#,0'), 'pct': ('.0%', '0 %')}


def _fmt(formato):
    """formato = clave de FORMATOS o una cadena propia (d3 en modo d3, formato de Power BI en modo pbi)."""
    d3, pbi = FORMATOS.get(formato, (formato, formato))
    return {'format': d3} if MODO_FORMATO == 'd3' else {'format': pbi, 'formatType': 'pbiFormat'}


def _c(direccion):
    try:   # incluye direcciones a la medida (PBIX_TOKENS_EXTRA)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from estilo_a_medida import cargar_tokens
        return cargar_tokens(_TOK)['direcciones'][direccion]
    except ImportError:
        return json.load(open(_TOK, encoding='utf-8'))['direcciones'][direccion]


def _rgba(h, a):
    h = h.lstrip('#')
    return f'rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})'


def _config(c):
    # background 'transparent' (null no es válido en el esquema); customFormatTypes: sin él Vega-Lite descarta pbiFormat
    # [probado: vega-lite 6.4.3,]
    return {'background': 'transparent', 'customFormatTypes': True, 'view': {'stroke': None}, 'font': 'Segoe UI',
            'axis': {'labelColor': c['tinta3'], 'labelFontSize': 12, 'labelFont': 'Segoe UI', 'title': None, 'domain': False,
                     'ticks': False, 'labelPadding': 6, 'gridColor': c['linea'], 'gridOpacity': .6},
            'axisX': {'grid': False, 'labelAngle': 0}, 'legend': {'disable': True},
            'text': {'font': 'Segoe UI', 'fontSize': 12, 'color': c['tinta']}, 'padding': 4}


def _base(c, extra):
    return {'$schema': VL, 'data': {'name': 'dataset'}, 'width': 'container', 'height': 'container', 'config': _config(c), **extra}


def area_degradado(direccion='aurora', x='Mes', orden='Orden', y='Valor', comparacion='Comparación', formato='moneda', formato_eje='moneda0'):
    """Serie principal con área en degradado + línea de comparación (gris) + punto y etiqueta al final."""
    c = _c(direccion); ac = c['acento']
    capas = [{'mark': {'type': 'area', 'color': {'gradient': 'linear', 'x1': 1, 'y1': 1, 'x2': 1, 'y2': 0,
                                                 'stops': [{'offset': 0, 'color': _rgba(ac, 0)}, {'offset': 1, 'color': _rgba(ac, .42)}]}},
              'encoding': {'y': {'field': y, 'type': 'quantitative',
                                 'axis': {**_fmt(formato_eje), 'tickCount': 4}}}}]
    if comparacion:
        capas.append({'mark': {'type': 'line', 'color': c['contexto'], 'strokeWidth': 1.5},
                      'encoding': {'y': {'field': comparacion, 'type': 'quantitative'}}})
    capas.append({'mark': {'type': 'line', 'color': ac, 'strokeWidth': 2.5},
                  'encoding': {'y': {'field': y, 'type': 'quantitative'},
                               'tooltip': [{'field': x}, {'field': y, **_fmt(formato)}]}})
    capas.append({'transform': [{'joinaggregate': [{'op': 'max', 'field': orden, 'as': '_ult'}]},
                                {'filter': f"datum['{orden}'] == datum._ult"}],
                  'layer': [{'mark': {'type': 'point', 'filled': True, 'size': 70, 'color': ac, 'opacity': 1},
                             'encoding': {'y': {'field': y, 'type': 'quantitative'}}},
                            {'mark': {'type': 'text', 'align': 'left', 'dx': 9, 'fontWeight': 600, 'color': c['tinta']},
                             'encoding': {'y': {'field': y, 'type': 'quantitative'},
                                          'text': {'field': y, **_fmt(formato)}}}]})
    return _base(c, {'encoding': {'x': {'field': x, 'type': 'ordinal', 'sort': {'field': orden, 'op': 'min'}}}, 'layer': capas})   # op min: con capas, sum se descarta


def anillo(direccion='aurora', avance='Avance', grosor=14):
    """Anillo de avance (1 fila: la medida de avance, 1.03 = 103 %) con el porcentaje al centro."""
    c = _c(direccion); R = 'min(width,height)/2'

    def arco():
        return {'type': 'arc', 'outerRadius': {'expr': R}, 'innerRadius': {'expr': f'{R}-{grosor}'}, 'theta': 0}
    return _base(c, {'transform': [{'calculate': f"2*PI*min(max(datum['{avance}'],0),0.9999)", 'as': '_t'}],
                     'layer': [{'mark': {**arco(), 'theta2': 6.2831, 'color': c['acento_suave']}},
                               # arco de avance: theta = _t en radianes sin escala (1 fila → se apila de 0 a _t). theta2 solo
                               # no compila y con type/scale no pasa el esquema [probado: vega-lite 6.4.3]
                               {'mark': {**{k: v for k, v in arco().items() if k != 'theta'}, 'cornerRadius': grosor / 2, 'color': c['acento']},
                                'encoding': {'theta': {'field': '_t', 'type': 'quantitative', 'scale': None}}},
                               {'mark': {'type': 'text', 'fontSize': 28, 'fontWeight': 600, 'color': c['tinta']},
                                'encoding': {'text': {'field': avance, **_fmt('pct')}}}]})


def bullet(direccion='aurora', categoria='Categoría', valor='Valor', meta='Meta', maximo=1.2):
    """Bullet por categoría: avance contra meta (barra), marca de la meta, porcentaje al final."""
    c = _c(direccion); esc = {'domain': [0, maximo]}
    return _base(c, {'transform': [{'calculate': f"datum['{valor}']/datum['{meta}']", 'as': '_r'},
                                   {'calculate': f'min(datum._r,{maximo})', 'as': '_rc'}],
                     'encoding': {'y': {'field': categoria, 'type': 'nominal', 'sort': {'field': '_r', 'op': 'max', 'order': 'descending'},
                                        'axis': {'labelColor': c['tinta2'], 'grid': False}}},
                     'layer': [{'mark': {'type': 'bar', 'height': 8, 'cornerRadius': 4, 'color': c['acento_suave']},
                                'encoding': {'x': {'datum': maximo, 'type': 'quantitative', 'scale': esc, 'axis': None}}},
                               {'mark': {'type': 'bar', 'height': 8, 'cornerRadius': 4},
                                'encoding': {'x': {'field': '_rc', 'type': 'quantitative', 'scale': esc, 'axis': None},
                                             'color': {'condition': {'test': 'datum._r >= 1', 'value': c['acento']},
                                                       'value': c['contexto']}}},
                               {'mark': {'type': 'tick', 'thickness': 2, 'size': 18, 'color': c['tinta']},
                                'encoding': {'x': {'datum': 1, 'type': 'quantitative', 'scale': esc}}},
                               {'mark': {'type': 'text', 'align': 'left', 'dx': 8, 'fontWeight': 600, 'color': c['tinta']},
                                'encoding': {'x': {'datum': maximo, 'type': 'quantitative', 'scale': esc},
                                             'text': {'field': '_r', **_fmt('pct')}}}]})


def mancuerna(direccion='aurora', categoria='Categoría', anterior='Anterior', actual='Actual', formato='entero'):
    """Mancuerna (dumbbell): antes → ahora por categoría; punto actual verde si mejora, rojo si empeora."""
    c = _c(direccion)
    return _base(c, {'transform': [{'calculate': f"max(datum['{anterior}'],datum['{actual}'])", 'as': '_mx'}],
                     'encoding': {'y': {'field': categoria, 'type': 'nominal', 'sort': {'field': actual, 'op': 'max', 'order': 'descending'},
                                        'axis': {'labelColor': c['tinta2'], 'grid': True, 'gridDash': [2, 3]}}},
                     'layer': [{'mark': {'type': 'rule', 'strokeWidth': 3, 'color': c['contexto_suave']},
                                'encoding': {'x': {'field': anterior, 'type': 'quantitative',
                                                   'axis': {**_fmt(formato), 'tickCount': 4}},
                                             'x2': {'field': actual}}},
                               {'mark': {'type': 'point', 'filled': True, 'size': 80, 'color': c['contexto'], 'opacity': 1},
                                'encoding': {'x': {'field': anterior, 'type': 'quantitative'}}},
                               {'mark': {'type': 'point', 'filled': True, 'size': 110, 'opacity': 1},
                                'encoding': {'x': {'field': actual, 'type': 'quantitative'},
                                             'color': {'condition': {'test': f"datum['{actual}'] >= datum['{anterior}']",
                                                                     'value': c['bien']}, 'value': c['mal']}}},
                               {'mark': {'type': 'text', 'align': 'left', 'dx': 10, 'fontWeight': 600, 'color': c['tinta']},
                                'encoding': {'x': {'field': '_mx', 'type': 'quantitative'},
                                             'text': {'field': actual, **_fmt(formato)}}}]})


PLANTILLAS = {'area_degradado': area_degradado, 'anillo': anillo, 'bullet': bullet, 'mancuerna': mancuerna}

if __name__ == '__main__':
    from comun import ayuda; ayuda(__doc__, 2)
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--formato' in sys.argv:
        MODO_FORMATO = sys.argv[sys.argv.index('--formato') + 1]
        args = [a for a in args if a != MODO_FORMATO]
    d = args[0] if args else 'aurora'
    out = args[1] if len(args) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    for n, f in PLANTILLAS.items():
        json.dump(f(d), open(os.path.join(out, f'{n}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('plantillas Deneb', d, '→', out, ', '.join(PLANTILLAS))
