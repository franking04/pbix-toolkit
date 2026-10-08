# EJEMPLO: réplica nativa de un dashboard HTML ("Roadmap de ventas") en Layout clásico.
"""Página Roadmap: esquinas sutiles, títulos con aire, KPIs grandes y sin scroll interno.
Parte de un .pbix en Layout clásico con las medidas RV ya en el modelo (ver roadmap_medidas.dax), reemplaza la página
'Roadmap de ventas' y escribe un archivo nuevo.
Uso: python roadmap_pagina.py origen.pbix salida.pbix"""
import json, sys, zipfile
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / 'scripts'))
from modificar_layout import Pbix, lit, dnum, dint, color

ORIGEN = Path(sys.argv[1] if len(sys.argv) > 1 else 'origen.pbix')
DESTINO = Path(sys.argv[2] if len(sys.argv) > 2 else 'salida.pbix')
p = Pbix(str(ORIGEN))
R = 'Roadmap de ventas'

# ---- limpiar la versión anterior (página y botón de la portada) ----
p.layout['sections'] = [s for s in p.layout['sections'] if s['displayName'] != R]
for i, s in enumerate(p.layout['sections']): s['ordinal'] = i
intro = p.pagina('Intro')
intro['visualContainers'] = [v for v in intro['visualContainers'] if 'Roadmap de ventas (Power BI)' not in v['config']]

NAVY, INK, GRIS, LINEA, FONDO = '#0B2545', '#13315C', '#5B6B82', '#DDE3EC', '#F2F4F8'
ORO, SUBE, BAJA, BLANCO, SUBT = '#C9A227', '#2E8B57', '#C0392B', '#FFFFFF', '#B9C6D8'
REG = "'Segoe UI', wf_segoe-ui_normal, helvetica, arial, sans-serif"
SEMI = "'Segoe UI Semibold', wf_segoe-ui_semibold, helvetica, arial, sans-serif"
BOLD = "'Segoe UI Bold', wf_segoe-ui_bold, helvetica, arial, sans-serif"
F = 'FactMovimientos'
RADIO = 8
def M(n, vis=None): return (F, n, 'measure', vis)
def pt(px_): return round(px_ * 0.75, 1)

def regla(medida, casos):
    left = {'Measure': {'Expression': {'SourceRef': {'Entity': F}}, 'Property': medida}}
    return {'solid': {'color': {'expr': {'Conditional': {'Cases': [
        {'Condition': {'Comparison': {'ComparisonKind': k, 'Left': left, 'Right': {'Literal': {'Value': f'{float(u)}D'}}}},
         'Value': {'Literal': {'Value': f"'{c}'"}}} for k, u, c in casos]}}}}}
SEMAFORO = lambda m: regla(m, [(2, 0, SUBE), (3, 0, BAJA)])
WILD = lambda q: {'data': [{'dataViewWildcard': {'matchingOption': 1}}], 'metadata': q}
def marco(): return {'title': [{'properties': {'show': lit(False)}}], 'background': [{'properties': {'show': lit(False)}}],
                     'border': [{'properties': {'show': lit(False)}}], 'visualHeader': [{'properties': {'show': lit(False)}}]}

ANCHO, ALTO, G = 1280, 1426, 16
pag = p.agregar_pagina(R, ancho=ANCHO, alto=ALTO, fondo=FONDO)
cfg = json.loads(pag['config'])
cfg['objects']['outspace'] = [{'properties': {'color': color(FONDO), 'transparency': dnum(0)}}]
pag['config'] = json.dumps(cfg, ensure_ascii=False)

def caja(x, y, w, h, fondo=BLANCO, borde=LINEA, radio=RADIO):
    vco = {'background': [{'properties': {'show': lit(True), 'color': color(fondo), 'transparency': dnum(0)}}],
           'visualHeader': [{'properties': {'show': lit(False)}}],
           'border': [{'properties': {'show': lit(borde is not None), 'color': color(borde or fondo), 'radius': dnum(radio)}}]}
    return p.agregar_visual(R, 'textbox', (x, y, w, h),
        objects={'general': [{'properties': {'paragraphs': [{'textRuns': [{'value': ''}]}]}}]}, vcObjects=vco)

def texto(x, y, w, h, runs, alinear='left'):
    par = {'textRuns': [{'value': t, 'textStyle': {'fontSize': f'{pt(sz)}pt', 'color': c, 'fontFamily': SEMI if b else REG}}
                        for t, sz, c, b in runs], 'horizontalTextAlignment': alinear}
    return p.agregar_visual(R, 'textbox', (x, y, w, h), objects={'general': [{'properties': {'paragraphs': [par]}}]},
                            vcObjects=marco())

def tarjeta(x, y, w, h, medida, tam_pt, col, fuente=BOLD, regla_color=None):
    """Tarjeta clásica: valor centrado, sin etiqueta de categoría."""
    return p.agregar_visual(R, 'card', (x, y, w, h), roles={'Values': [M(medida, ' ')]},
        objects={'labels': [{'properties': {'fontSize': dnum(tam_pt), 'color': regla_color or color(col),
                                            'fontFamily': lit(fuente), 'labelDisplayUnits': dint(1)}}],
                 'categoryLabels': [{'properties': {'show': lit(False)}}]},
        vcObjects=marco())

def encabezado_seccion(x, y, w, titulo, subtitulo):
    texto(x + 14, y + 10, w - 28, 36, [(titulo, 16, INK, True)])
    texto(x + 14, y + 44, w - 28, 30, [(subtitulo, 12.5, GRIS, False)])

# ---- 1. Encabezado (alto 132) ----
HY, HH = G, 120
ZW = 760                                     # zona de textos (izquierda); slicers a la derecha
caja(G, HY, ANCHO - 2 * G, HH, fondo=NAVY, borde=None, radio=10)
p.agregar_visual(R, 'basicShape', (G + 6, HY + HH - 4, ANCHO - 2 * G - 12, 3),
    objects={'general': [{'properties': {'shapeType': lit('rectangle')}}],
             'fill': [{'properties': {'fillColor': color(ORO), 'transparency': dnum(0)}}],
             'line': [{'properties': {'weight': dnum(0), 'lineColor': color(ORO)}}]}, vcObjects=marco())
texto(G + 16, HY + 8, ZW, 30, [('INVENTARIO  ·  VENTAS NETAS', 11.5, ORO, True)], alinear='center')
tarjeta(G + 16, HY + 32, ZW, 52, 'RV Titulo', 20, BLANCO)
tarjeta(G + 16, HY + 80, ZW, 32, 'RV Periodo', 11, SUBT, fuente=REG)
sku = p.clonar_visual(p.visual('Roadmap - Ventas', vid='ID_00100000000000000'), R, pos=(800.0, HY + 20, 180.0, 80.0))
fec = p.clonar_visual(p.visual('Roadmap - Ventas', vid='ID_00110000000000000'), R, pos=(992.0, HY + 20, 256.0, 80.0))
for s in (sku, fec): s.propiedad('vcObjects', 'border', {'radius': dnum(RADIO)})
fec.propiedad('objects', 'slider', {'show': lit(False)})

# ---- 2. Indicadores grandes (alto 150) ----
KY, KH, KG = HY + HH + 16, 112, 12
KW = (ANCHO - 2 * G - 4 * KG) / 5
kpis = [('Ventas netas', 'RV KPI ventas', None, 'Facturas + ND − NC'),
        ('Unidades netas', 'RV KPI unidades', None, 'Cajas vendidas'),
        ('Margen bruto', 'RV KPI margen', 'RV KPI margen detalle', None),
        ('Mejor mes', 'RV KPI mejor mes', 'RV KPI mejor mes valor', None),
        ('Último mes completo', 'RV KPI ultimo mes', 'RV KPI ultimo mes detalle', None)]
for i, (etq, med, det_med, det_txt) in enumerate(kpis):
    x = G + i * (KW + KG)
    caja(x, KY, KW, KH)
    texto(x + 8, KY + 4, KW - 16, 28, [(etq.upper(), 11.5, GRIS, True)], alinear='center')
    rc = SEMAFORO('RV Var ultimo mes') if med == 'RV KPI ultimo mes' else None
    tarjeta(x + 6, KY + 28, KW - 12, 50, med, 22, INK, regla_color=rc)
    if det_med: tarjeta(x + 6, KY + 76, KW - 12, 32, det_med, 9.5, GRIS, fuente=REG)
    else: texto(x + 8, KY + 78, KW - 16, 28, [(det_txt, 12, GRIS, False)], alinear='center')

# ---- 3. Evolución mensual + ruta (alto 560) ----
EY, EH, EW = KY + KH + 16, 600, 800
caja(G, EY, EW, EH)
encabezado_seccion(G, EY, EW, 'Evolución mensual', 'Ventas netas en USD y ruta mes a mes con la variación contra el mes anterior.')
RH = 104
p.agregar_visual(R, 'clusteredColumnChart', (G + 8 + RH, EY + 80, EW - 16 - RH, 300),
    roles={'Category': [('DimFecha', 'AnioMes', None, 'Mes')], 'Y': [M('RV Ventas netas', 'Ventas netas USD')]},
    orden=('DimFecha.AnioMes', 'asc'),
    objects={'dataPoint': [{'properties': {'fill': color(INK)}},
                           {'properties': {'fill': regla('RV Es mejor mes', [(0, 1, ORO), (0, 0, INK)])},
                            'selector': {'data': [{'dataViewWildcard': {'matchingOption': 1}}]}}],
             'labels': [{'properties': {'show': lit(True), 'labelPosition': lit('OutsideEnd'), 'color': color(INK),
                                        'fontSize': dnum(10), 'labelDisplayUnits': dint(1), 'labelPrecision': lit(0),
                                        'fontFamily': lit(SEMI)}}],
             'categoryAxis': [{'properties': {'show': lit(True), 'showAxisTitle': lit(False), 'axisType': lit('Categorical'),
                                              'fontSize': dnum(9.5), 'labelColor': color(INK)}}],
             'valueAxis': [{'properties': {'show': lit(False), 'showAxisTitle': lit(False), 'gridlineShow': lit(True),
                                           'gridlineColor': color(LINEA), 'start': dnum(0)}}],
             'legend': [{'properties': {'show': lit(False)}}]},
    vcObjects=marco())
p.agregar_visual(R, 'pivotTable', (G + 8, EY + 388, EW - 16, 156),
    roles={'Columns': [('DimFecha', 'AnioMes', None, 'Mes')],
           'Values': [M('RV Ruta unidades', 'Unidades'), M('RV Ruta variacion', 'Vs mes ant.'),
                      M('RV Ruta importacion', 'Import.')]},
    orden=('DimFecha.AnioMes', 'asc'),
    objects={'values': [{'properties': {'valuesOnRow': lit(True), 'fontSize': dnum(9.5), 'fontColor': color(GRIS),
                                        'backColorPrimary': color(BLANCO), 'backColorSecondary': color(BLANCO)}},
                        {'properties': {'fontColor': SEMAFORO('RV Var ventas')}, 'selector': WILD(f'{F}.RV Ruta variacion')},
                        {'properties': {'fontColor': color(ORO)}, 'selector': WILD(f'{F}.RV Ruta importacion')}],
             'columnHeaders': [{'properties': {'fontColor': color(INK), 'backColor': color(BLANCO), 'fontSize': dnum(9.5),
                                               'fontFamily': lit(SEMI), 'alignment': lit('Center'),
                                               'wordWrap': lit(True)}}],
             'rowHeaders': [{'properties': {'fontColor': color(GRIS), 'backColor': color(BLANCO), 'fontSize': dnum(9)}}],
             'columnFormatting': [{'properties': {'alignment': lit('Center')}, 'selector': {'metadata': f'{F}.{m}'}}
                                  for m in ('RV Ruta unidades', 'RV Ruta variacion', 'RV Ruta importacion')],
             'subTotals': [{'properties': {'rowSubtotals': lit(False), 'columnSubtotals': lit(False)}}],
             'grid': [{'properties': {'gridVertical': lit(False), 'gridHorizontal': lit(True), 'rowPadding': dnum(3),
                                      'gridHorizontalColor': color(LINEA), 'outlineColor': color(BLANCO)}}]},
    vcObjects=marco())
texto(G + 14, EY + EH - 44, EW - 28, 34, [
    ('■ ', 13, INK, True), ('Ventas netas USD        ', 12.5, GRIS, False),
    ('■ ', 13, ORO, True), ('Mejor mes        ', 12.5, GRIS, False),
    ('◯ ', 12.5, ORO, True), ('Importación recibida', 12.5, GRIS, False)])

# ---- 4. Participación por producto (más ancha, sin scroll) ----
PX = G + EW + 12; PW = ANCHO - G - PX
caja(PX, EY, PW, EH)
encabezado_seccion(PX, EY, PW, 'Participación por producto', 'Ventas netas del periodo seleccionado.')
anchos_rank = (('DimProducto.CodigoProducto', 50), ('DimProducto.Descripcion', 178),
               (f'{F}.RV Ventas netas', 74), (f'{F}.RV Ranking ventas', 70))
rank = p.agregar_visual(R, 'tableEx', (PX + 8, EY + 80, PW - 16, EH - 92),
    roles={'Values': [('DimProducto', 'CodigoProducto', None, 'Código'), ('DimProducto', 'Descripcion', None, 'Producto'),
                      M('RV Ventas netas', ' '), M('RV Ranking ventas', 'Ventas')]},
    orden=(f'{F}.RV Ventas netas', 'desc'),
    objects={'columnFormatting': [
                {'properties': {'dataBars': {'positiveColor': color(INK), 'negativeColor': color(BAJA), 'axisColor': color(LINEA),
                                             'reverseDirection': lit(False), 'hideText': lit(True)}},
                 'selector': {'metadata': f'{F}.RV Ventas netas'}},
                {'properties': {'alignment': lit('Right')}, 'selector': {'metadata': f'{F}.RV Ranking ventas'}}],
             'columnWidth': [{'properties': {'value': dnum(w)}, 'selector': {'metadata': q}} for q, w in anchos_rank],
             'columnHeaders': [{'properties': {'fontColor': color(GRIS), 'backColor': color(BLANCO), 'fontSize': dnum(9),
                                               'fontFamily': lit(SEMI), 'outlineColor': color(LINEA)}}],
             'values': [{'properties': {'fontColor': color(INK), 'fontSize': dnum(9.5), 'backColorPrimary': color(BLANCO),
                                        'backColorSecondary': color(BLANCO), 'wordWrap': lit(True)}}],
             'grid': [{'properties': {'gridVertical': lit(False), 'gridHorizontal': lit(True), 'gridHorizontalColor': color(LINEA),
                                      'rowPadding': dnum(6), 'outlineColor': color(BLANCO)}}],
             'total': [{'properties': {'totals': lit(False)}}]},
    vcObjects=marco())

# ---- 5. Comparativo mes a mes (todas las filas visibles) ----
CY = EY + EH + 16; CH = ALTO - CY - G
caja(G, CY, ANCHO - 2 * G, CH)
encabezado_seccion(G, CY, ANCHO - 2 * G, 'Comparativo mes a mes',
                   'Unidades y dinero contra el mes anterior. El precio promedio explica cuando ambos no se mueven igual.')
cols = [('DimFecha.AnioMes', 'Mes', 230), (f'{F}.RV Tabla unidades', 'Unidades', 190), (f'{F}.RV Tabla var unidades', 'Var und', 180),
        (f'{F}.RV Tabla ventas', 'Ventas USD', 220), (f'{F}.RV Tabla var ventas', 'Var USD', 180), (f'{F}.RV Tabla precio', 'Precio prom.', 190)]
p.agregar_visual(R, 'tableEx', (G + 8, CY + 80, ANCHO - 2 * G - 16, CH - 92),
    roles={'Values': [('DimFecha', 'AnioMes', None, 'Mes')] + [M(q.split('.', 1)[1], v) for q, v, _ in cols[1:]]},
    orden=('DimFecha.AnioMes', 'asc'),
    objects={'columnFormatting': [{'properties': {'alignment': lit('Right')}, 'selector': {'metadata': q}} for q, _, _ in cols[1:]],
             'values': [{'properties': {'fontColor': color(INK), 'fontSize': dnum(11), 'backColorPrimary': color(BLANCO),
                                        'backColorSecondary': color(BLANCO)}},
                        {'properties': {'fontColor': SEMAFORO('RV Var unidades')}, 'selector': WILD(f'{F}.RV Tabla var unidades')},
                        {'properties': {'fontColor': SEMAFORO('RV Var ventas')}, 'selector': WILD(f'{F}.RV Tabla var ventas')}],
             'columnWidth': [{'properties': {'value': dnum(w)}, 'selector': {'metadata': q}} for q, _, w in cols],
             'columnHeaders': [{'properties': {'fontColor': color(GRIS), 'backColor': color(BLANCO), 'fontSize': dnum(9.5),
                                               'fontFamily': lit(SEMI), 'outlineColor': color(LINEA)}}],
             'grid': [{'properties': {'gridVertical': lit(False), 'gridHorizontal': lit(True), 'gridHorizontalColor': color(LINEA),
                                      'rowPadding': dnum(6), 'outlineColor': color(BLANCO)}}],
             'total': [{'properties': {'totals': lit(True), 'backColor': color(FONDO), 'fontColor': color(INK),
                                       'fontFamily': lit(BOLD), 'fontSize': dnum(11)}}]},
    vcObjects=marco())

# ---- Interacción, navegación ----
cfg = json.loads(pag['config'])
cfg['relationships'] = [{'source': sku.id, 'target': rank.id, 'type': 3}]
pag['config'] = json.dumps(cfg, ensure_ascii=False)
img = p.visual('Intro', vid='ID_00010000000000000')
b = p.clonar_visual(img, 'Intro', pos=(57.43589743589743, 442.0, None, None))
b.propiedad('vcObjects', 'visualLink', {'navigationSection': lit(pag['name']), 'tooltip': lit('Roadmap de ventas (Power BI)')})

p.guardar(str(DESTINO))
print('origen', ORIGEN.name, '-> destino', DESTINO.name, '| página', ANCHO, 'x', ALTO)
