# EJEMPLO: rediseño de todas las páginas de un reporte de inventario en dos direcciones visuales con componentes.py.
"""Rediseño de todas las páginas con pbix-toolkit, en dos direcciones visuales (servicio de Power BI, PBIR).
Brief: público mixto (dirección → Roadmap; analistas/operación → Inventario), laptop 1280 px, HTML oculta, portada como menú.
Necesita dos archivos del mismo reporte: uno en Layout clásico (para construir) y el mismo guardado por el Desktop en PBIR
con las medidas RV en el modelo. Ajusta ids de página, campos y medidas a tu archivo.
Uso: python rediseno_dos_versiones.py clasico.pbix guardado_pbir.pbix [marca|corporativo ...]
     → salida_marca.pbix y salida_corporativo.pbix en la carpeta actual"""
import json, sys, os, zipfile, tempfile, copy
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / 'scripts'))
from modificar_layout import Pbix, lit, dnum, dint, color
from componentes import Lienzo, regla, wild, marco, REG, SEMI, BOLD
from pbir import visual_layout_a_pbir, reemplazar_paginas, page_json_desde_seccion
from tema_powerbi import DIRECCIONES, tema, aplicar_tema_pbir

CLASICO = Path('clasico.pbix')            # Layout clásico (para construir); se cambia por argumento
GUARDADO = Path('guardado_pbir.pbix')     # PBIR guardado por Desktop (modelo con medidas); se cambia por argumento
F = 'FactMovimientos'
ID = {'portada': 'ID_00020000000000000', 'inventario': 'ID_00030000000000000', 'html': 'ID_00040000000000000',
      'roadmap': 'ID_00050000000000000'}
NAV = [('Portada', ID['portada']), ('Roadmap de ventas', ID['roadmap']), ('Inventario de movimientos', ID['inventario'])]

# Marca "Marca Demo S.A." (colores de la portada original). Paleta categórica validada con dataviz
# (light, #FFFFFF): CVD ≥ 11.5, normal ≥ 17.1; oro y rosa < 3:1 → siempre con etiqueta. Rojo y caramelo NO pueden
# ir juntos (CVD 3.3): por eso el caramelo no está en la paleta categórica, solo como énfasis de una serie.
MARCA = dict(colores=['#D9381E', '#2F5D9E', '#D4A72C', '#1F8A70', '#8466B8', '#B5651D', '#D77FA3', '#5E9A35'],
             pagina='#FBF6EE', superficie='#FFFFFF', texto='#3A2A1A', texto2='#7A6555', linea='#EADFD2',
             acento='#6B4226', radio=8, sombra=False,
             enc_fondo='#4A2C17', enc_texto='#FFFFFF', enc_sub='#E8D9C4', enc_kicker='#E1C233', enc_linea='#E1C233',
             enfasis='#6B4226', mejor='#D4A72C', contexto='#CDBFAF', sube='#1E7A3C', baja='#C0392B')
VERSIONES = {'marca': MARCA, 'corporativo': DIRECCIONES['corporativo']}

def fondo_pagina(sec, T, imagen=None):
    cfg = json.loads(sec.get('config') or '{}')
    cfg['objects'] = {'background': [{'properties': {'color': color(T['pagina']), 'transparency': dnum(0)}}],
                      'outspace': [{'properties': {'color': color(T['pagina']), 'transparency': dnum(0)}}]}
    cfg.pop('visibility', None)
    sec['config'] = json.dumps(cfg, ensure_ascii=False)

# ------------------------------------------------------------------ Portada
def portada(p, T, version):
    sec = p.pagina('Intro'); sec['visualContainers'] = []; sec['displayName'] = 'Portada'
    fondo_pagina(sec, T)
    L = Lienzo(p, 'Portada', T, F)
    L.barra_nav(NAV, ID['portada'], marca='MARCA DEMO S.A.' if version == 'marca' else 'Inventario y ventas')
    if version == 'marca':
        img = p.agregar_visual('Portada', 'image', (16, 52, 500, 652), objects={'image': [{'properties': {'sourceFile': {'image': {
            'name': lit('foto_producto.jpg'), 'url': {'expr': {'ResourcePackageItem': {'PackageName': 'RegisteredResources',
            'PackageType': 1, 'ItemName': 'foto_producto.jpg'}}}, 'scaling': lit('Fill')}}}}]},
            vcObjects={**marco(), 'border': [{'properties': {'show': lit(True), 'color': color(T['linea']), 'radius': dnum(T['radio'])}}]})
        X, W = 532, 732
        L.texto(X, 60, W, 30, [('MARCA DEMO S.A.  ·  REPORTE COMERCIAL', 12, T['acento'], True)])
        L.texto(X, 88, W, 60, [('Inventario y ventas', 34, 'texto', True)])
        L.texto(X, 146, W, 30, [('Movimientos de inventario y ventas netas por producto.', 14, 'texto2', False)])
        L.caja(X, 182, 300, 34, fondo=T['pagina'], borde='linea')
        L.valor(X + 4, 184, 292, 30, 'RV Periodo', 10, 'texto', fuente=REG)
        Y0 = 236
    else:
        L.encabezado(16, 52, 1248, 168, 'Reporte comercial · Inventario', titulo='Inventario y ventas',
                     sub='Movimientos de inventario y ventas netas por producto.', ancho_texto=860)
        L.caja(1000, 150, 248, 34, fondo=T['enc_fondo'], borde='enc_linea')
        L.valor(1004, 152, 240, 30, 'RV Periodo', 10, T['enc_texto'], fuente=REG)
        X, W, Y0 = 16, 1248, 236
    KG = 12; KW = (W - 2 * KG) / 3
    for i, (et, med, det) in enumerate([('Ventas netas', 'RV KPI ventas', 'Facturas + ND − NC'),
                                        ('Unidades netas', 'RV KPI unidades', 'Cajas vendidas'),
                                        ('Margen bruto', 'RV KPI margen', None)]):
        L.kpi(X + i * (KW + KG), Y0, KW, 112, et, med, detalle=det,
              detalle_medida='RV KPI margen detalle' if det is None else None)
    NY, NH, NG = Y0 + 128, 228 if version == 'marca' else 240, 12
    NW = (W - NG) / 2
    destinos = [('Roadmap de ventas', ID['roadmap'], 'Para dirección',
                 'Evolución mensual de las ventas netas, mejor mes, variación contra el mes anterior, '
                 'participación por producto y comparativo de unidades, dinero y precio promedio.'),
                ('Inventario de movimientos', ID['inventario'], 'Para análisis y operación',
                 'Entradas, salidas y saldos por SKU y fecha, con valor de cada movimiento, documento y costo promedio. '
                 'Elige un producto, un tipo de movimiento y un periodo.')]
    for i, (tit, pid, quien, desc) in enumerate(destinos):
        x = X + i * (NW + NG)
        L.caja(x, NY, NW, NH)
        L.texto(x + 16, NY + 10, NW - 32, 28, [(quien.upper(), 11.5, T['acento'], True)])
        L.texto(x + 16, NY + 36, NW - 32, 40, [(tit, 20, 'texto', True)])
        L.texto(x + 16, NY + 78, NW - 32, 90, [(desc, 13, 'texto2', False)], lineas=3)
        L.boton_nav(x + 16, NY + NH - 52, 150, 36, 'Abrir  →', pid, activo=True)
    L.texto(X, NY + NH + 14, W, 30, [('Cada página tiene sus propios filtros de producto y periodo. '
                                       'Pasa el mouse sobre un visual para ver el detalle.', 12, 'texto2', False)])

# ------------------------------------------------------------------ Inventario (detalle para análisis y operación)
def inventario(p, T):
    sec = p.pagina('Inventario'); sec['displayName'] = 'Inventario de movimientos'
    fondo_pagina(sec, T)
    P = 'Inventario de movimientos'
    sku = p.visual(P, vid='ID_00060000000000000'); tipo = p.visual(P, vid='ID_00070000000000000')
    fecha = p.visual(P, vid='ID_00080000000000000'); tabla = p.visual(P, vid='ID_00090000000000000')
    L = Lienzo(p, P, T, F)
    L.barra_nav(NAV, ID['inventario'], marca='MARCA DEMO S.A.' if T is MARCA else 'Inventario y ventas')
    L.encabezado(16, 48, 1248, 88, 'Inventario de movimientos', titulo='Entradas, salidas y saldo por producto', ancho_texto=900)
    # filtros: fecha dentro del encabezado; producto a la izquierda; tipo de movimiento sobre la tabla
    fecha.mover(1004, 58, 248, 68)
    fecha.propiedad('objects', 'slider', {'show': lit(False)})
    fecha.propiedad('vcObjects', 'title', {'show': lit(False)})
    fecha.propiedad('vcObjects', 'background', {'show': lit(True), 'color': color(T['superficie']), 'transparency': dnum(0)})
    fecha.propiedad('vcObjects', 'border', {'show': lit(True), 'color': color(T['linea']), 'radius': dnum(T['radio'])})
    fecha.propiedad('objects', 'header', {'show': lit(True), 'text': lit('Periodo'), 'fontColor': color(T['texto'])})
    sku.renombrar_ref('CountNonNull(Producto.Código)', 'Max(Producto.Código)')   # queryRef viejo
    sku.mover(16, 148, 224, 556)
    sku.propiedad('vcObjects', 'title', {'show': lit(True), 'text': lit('Producto'), 'fontColor': color(T['texto']),
                                         'background': color(T['superficie']), 'fontSize': dnum(11)})
    sku.propiedad('vcObjects', 'background', {'show': lit(True), 'color': color(T['superficie']), 'transparency': dnum(0)})
    sku.propiedad('vcObjects', 'border', {'show': lit(True), 'color': color(T['linea']), 'radius': dnum(T['radio'])})
    sku.propiedad('objects', 'layout', {'lineColor': color(T['linea']), 'borderColor': color(T['linea']),
                                        'gridlineColor': color(T['linea']), 'borderWidth': dnum(1)})
    X, W = 252, 1012
    KG = 12; KW = (W - 3 * KG) / 4
    for i, (et, col, det) in enumerate([('Entradas', 'Entrada', 'unidades que ingresan'),
                                        ('Salidas', 'Salida', 'unidades que salen'),
                                        ('Movimiento neto', 'Cantidad', 'entradas − salidas'),
                                        ('Valor de los movimientos', 'ValorMovimiento', 'costo valorizado')]):
        L.kpi(X + i * (KW + KG), 148, KW, 104, et, detalle=det, columna=(F, col, 'Sum', 0), tam_pt=20)
    tipo.mover(X, 264, W, 52)
    tipo.propiedad('vcObjects', 'title', {'show': lit(False)})
    tipo.propiedad('vcObjects', 'background', {'show': lit(True), 'color': color(T['superficie']), 'transparency': dnum(0)})
    tipo.propiedad('vcObjects', 'border', {'show': lit(True), 'color': color(T['linea']), 'radius': dnum(T['radio'])})
    tipo.propiedad('objects', 'general', {'outlineColor': color(T['enfasis'])})
    # tabla: queryRefs reales, orden de lectura, anchos que caben sin scroll horizontal, números a la derecha
    tabla.renombrar_ref('Sum(FactMovimientos.CostoUnitario)', 'Avg(FactMovimientos.CostoUnitario)')
    tabla.renombrar_ref('Sum(FactMovimientos.SaldoAcumulado)', 'FactMovimientos.SaldoAcumulado')
    tabla.renombrar_ref('Sum(FactMovimientos.SaldoValorAcumulado)', 'FactMovimientos.SaldoValorAcumulado')
    cols = [('DimFecha.Fecha', 70), ('FactMovimientos.CodigoProducto', 58), ('FactMovimientos.TipoMov', 40),
            ('FactMovimientos.TipoMovDesc', 90), ('FactMovimientos.Documento', 80), ('FactMovimientos.DocumentoFiscal', 96),
            ('Sum(FactMovimientos.Entrada)', 58), ('Sum(FactMovimientos.Salida)', 58), ('Sum(FactMovimientos.Cantidad)', 62),
            ('Avg(FactMovimientos.CostoUnitario)', 72), ('Sum(FactMovimientos.ValorMovimiento)', 84),
            ('FactMovimientos.SaldoAcumulado', 72), ('FactMovimientos.SaldoValorAcumulado', 86), ('FactMovimientos.CostoPromedio', 72)]
    tabla.ordenar_rol('Values', [q for q, _ in cols])
    numeros = [q for q, _ in cols[6:]]
    tabla.sv['objects'] = {
        'columnWidth': [{'properties': {'value': dnum(w)}, 'selector': {'metadata': q}} for q, w in cols],
        'columnFormatting': [{'properties': {'alignment': lit('Right')}, 'selector': {'metadata': q}} for q in numeros] +
                            [{'properties': {'labelPrecision': lit(2)}, 'selector': {'metadata': q}}
                             for q in ('Avg(FactMovimientos.CostoUnitario)', 'Sum(FactMovimientos.ValorMovimiento)')],
        'columnHeaders': [{'properties': {'fontColor': color(T['texto2']), 'backColor': color(T['superficie']), 'fontSize': dnum(8.5),
                                          'fontFamily': lit(SEMI), 'wordWrap': lit(True),
                                          'outlineColor': color(T['linea'])}}],
        'values': [{'properties': {'fontColor': color(T['texto']), 'fontSize': dnum(9), 'backColorPrimary': color(T['superficie']),
                                   'backColorSecondary': color(T['pagina'])}}],
        'grid': [{'properties': {'gridVertical': lit(False), 'gridHorizontal': lit(True), 'gridHorizontalColor': color(T['linea']),
                                 'rowPadding': dnum(4), 'outlineColor': color(T['superficie'])}}],
        'total': [{'properties': {'totals': lit(True), 'backColor': color(T['pagina']), 'fontColor': color(T['texto']),
                                  'fontFamily': lit(BOLD)}}]}
    tabla.sv['vcObjects'] = {'title': [{'properties': {'show': lit(False)}}],
                             'background': [{'properties': {'show': lit(True), 'color': color(T['superficie']), 'transparency': dnum(0)}}],
                             'border': [{'properties': {'show': lit(True), 'color': color(T['linea']), 'radius': dnum(T['radio'])}}]}
    tabla._sync()
    tabla.mover(X, 328, W, 376)
    # el lienzo se dibujó después: los visuales originales deben quedar por encima de cajas y encabezado
    zmax = max(v['z'] for v in sec['visualContainers'])
    for i, v in enumerate((fecha, sku, tipo, tabla)):
        z = zmax + 1000 * (i + 1); v.cont['z'] = z; v.cont['tabOrder'] = z
        v.cfg['layouts'][0]['position'].update(z=z, tabOrder=z); v._sync()

# ------------------------------------------------------------------ Roadmap de ventas (ejecutivo)
def roadmap(p, T):
    R = 'Roadmap de ventas'; ANCHO, G = 1280, 16
    sec = p.agregar_pagina(R, ancho=ANCHO, alto=1470, fondo=T['pagina'])
    sec['name'] = ID['roadmap']                     # mismo id que en el PBIR: la navegación sigue válida
    fondo_pagina(sec, T)
    L = Lienzo(p, R, T, F)
    SEM = lambda m: regla(F, m, [(2, 0, T['sube']), (3, 0, T['baja'])])
    M = lambda n, vis=None: (F, n, 'measure', vis)
    L.barra_nav(NAV, ID['roadmap'], marca='MARCA DEMO S.A.' if T is MARCA else 'Inventario y ventas')
    HY, HH = 48, 120
    L.encabezado(G, HY, ANCHO - 2 * G, HH, 'Inventario  ·  Ventas netas', titulo_medida='RV Titulo', sub_medida='RV Periodo', ancho_texto=760)
    sku = p.clonar_visual(p.visual('Roadmap - Ventas', vid='ID_00100000000000000'), R, pos=(800.0, HY + 20, 180.0, 80.0))
    fec = p.clonar_visual(p.visual('Roadmap - Ventas', vid='ID_00110000000000000'), R, pos=(992.0, HY + 20, 256.0, 80.0))
    for s in (sku, fec):
        s.propiedad('vcObjects', 'border', {'show': lit(True), 'radius': dnum(T['radio']), 'color': color(T['linea'])})
        s.propiedad('objects', 'header', {'fontColor': color(T['texto'])})
    fec.propiedad('objects', 'slider', {'show': lit(False)})
    # KPIs
    KY, KH, KG = HY + HH + 16, 112, 12
    KW = (ANCHO - 2 * G - 4 * KG) / 5
    for i, (et, med, dmed, dtxt) in enumerate([('Ventas netas', 'RV KPI ventas', None, 'Facturas + ND − NC'),
            ('Unidades netas', 'RV KPI unidades', None, 'Cajas vendidas'), ('Margen bruto', 'RV KPI margen', 'RV KPI margen detalle', None),
            ('Mejor mes', 'RV KPI mejor mes', 'RV KPI mejor mes valor', None),
            ('Último mes completo', 'RV KPI ultimo mes', 'RV KPI ultimo mes detalle', None)]):
        L.kpi(G + i * (KW + KG), KY, KW, KH, et, med, detalle=dtxt, detalle_medida=dmed,
              regla_color=SEM('RV Var ultimo mes') if med == 'RV KPI ultimo mes' else None)
    # Evolución mensual + ruta
    EY, EH, EW = KY + KH + 16, 600, 800
    cx, cy, cw, ch = L.seccion(G, EY, EW, EH, 'Evolución mensual', 'Ventas netas en USD y ruta mes a mes con la variación contra el mes anterior.')
    RH = 104
    p.agregar_visual(R, 'clusteredColumnChart', (cx + RH, cy, cw - RH, 300),
        roles={'Category': [('DimFecha', 'AnioMes', None, 'Mes')], 'Y': [M('RV Ventas netas', 'Ventas netas USD')]},
        orden=('DimFecha.AnioMes', 'asc'),
        objects={'dataPoint': [{'properties': {'fill': color(T['enfasis'])}},
                               {'properties': {'fill': regla(F, 'RV Es mejor mes', [(0, 1, T['mejor']), (0, 0, T['enfasis'])])},
                                'selector': {'data': [{'dataViewWildcard': {'matchingOption': 1}}]}}],
                 'labels': [{'properties': {'show': lit(True), 'labelPosition': lit('OutsideEnd'), 'color': color(T['texto']),
                                            'fontSize': dnum(10), 'labelDisplayUnits': dint(1), 'labelPrecision': lit(0), 'fontFamily': lit(SEMI)}}],
                 'categoryAxis': [{'properties': {'show': lit(True), 'showAxisTitle': lit(False), 'axisType': lit('Categorical'),
                                                  'fontSize': dnum(9.5), 'labelColor': color(T['texto'])}}],
                 'valueAxis': [{'properties': {'show': lit(False), 'showAxisTitle': lit(False), 'gridlineShow': lit(True),
                                               'gridlineColor': color(T['linea']), 'start': dnum(0)}}],
                 'legend': [{'properties': {'show': lit(False)}}]}, vcObjects=marco())
    p.agregar_visual(R, 'pivotTable', (cx, cy + 308, cw, 168),
        roles={'Columns': [('DimFecha', 'AnioMes', None, 'Mes')],
               'Values': [M('RV Ruta unidades', 'Unidades'), M('RV Ruta variacion', 'Vs mes ant.'), M('RV Ruta importacion', 'Import.')]},
        orden=('DimFecha.AnioMes', 'asc'),
        objects={'values': [{'properties': {'valuesOnRow': lit(True), 'fontSize': dnum(8.5), 'fontColor': color(T['texto2']),
                                            'wordWrap': lit(True), 'backColorPrimary': color(T['superficie']),
                                            'backColorSecondary': color(T['superficie'])}},
                            {'properties': {'fontColor': SEM('RV Var ventas')}, 'selector': wild(f'{F}.RV Ruta variacion')},
                            {'properties': {'fontColor': color(T['mejor'])}, 'selector': wild(f'{F}.RV Ruta importacion')}],
                 'columnHeaders': [{'properties': {'fontColor': color(T['texto']), 'backColor': color(T['superficie']), 'fontSize': dnum(9),
                                                   'fontFamily': lit(SEMI), 'alignment': lit('Center'), 'wordWrap': lit(True)}}],
                 'rowHeaders': [{'properties': {'fontColor': color(T['texto2']), 'backColor': color(T['superficie']), 'fontSize': dnum(8.5)}}],
                 'columnFormatting': [{'properties': {'alignment': lit('Center')}, 'selector': {'metadata': f'{F}.{m}'}}
                                      for m in ('RV Ruta unidades', 'RV Ruta variacion', 'RV Ruta importacion')],
                 'subTotals': [{'properties': {'rowSubtotals': lit(False), 'columnSubtotals': lit(False)}}],
                 'grid': [{'properties': {'gridVertical': lit(False), 'gridHorizontal': lit(True), 'rowPadding': dnum(3),
                                          'gridHorizontalColor': color(T['linea']), 'outlineColor': color(T['superficie'])}}]},
        vcObjects=marco())
    L.texto(G + 14, EY + EH - 44, EW - 28, 34, [('■ ', 13, T['enfasis'], True), ('Ventas netas USD        ', 12.5, 'texto2', False),
            ('■ ', 13, T['mejor'], True), ('Mejor mes        ', 12.5, 'texto2', False),
            ('◯ ', 12.5, T['mejor'], True), ('Importación recibida', 12.5, 'texto2', False)])
    # Participación por producto (el slicer de SKU no la filtra, como en el HTML)
    PX = G + EW + 12; PW = ANCHO - G - PX
    rx, ry, rw, rh = L.seccion(PX, EY, PW, EH, 'Participación por producto', 'Ventas netas del periodo seleccionado.')
    anchos = (('DimProducto.CodigoProducto', 50), ('DimProducto.Descripcion', 178), (f'{F}.RV Ventas netas', 74), (f'{F}.RV Ranking ventas', 70))
    rank = p.agregar_visual(R, 'tableEx', (rx, ry, rw, rh),
        roles={'Values': [('DimProducto', 'CodigoProducto', None, 'Código'), ('DimProducto', 'Descripcion', None, 'Producto'),
                          M('RV Ventas netas', ' '), M('RV Ranking ventas', 'Ventas')]},
        orden=(f'{F}.RV Ventas netas', 'desc'),
        objects={'columnFormatting': [
                    {'properties': {'dataBars': {'positiveColor': color(T['enfasis']), 'negativeColor': color(T['baja']),
                                                 'axisColor': color(T['linea']), 'reverseDirection': lit(False), 'hideText': lit(True)}},
                     'selector': {'metadata': f'{F}.RV Ventas netas'}},
                    {'properties': {'alignment': lit('Right')}, 'selector': {'metadata': f'{F}.RV Ranking ventas'}}],
                 'columnWidth': [{'properties': {'value': dnum(w)}, 'selector': {'metadata': q}} for q, w in anchos],
                 'columnHeaders': [{'properties': {'fontColor': color(T['texto2']), 'backColor': color(T['superficie']), 'fontSize': dnum(9),
                                                   'fontFamily': lit(SEMI), 'outlineColor': color(T['linea'])}}],
                 'values': [{'properties': {'fontColor': color(T['texto']), 'fontSize': dnum(9.5), 'backColorPrimary': color(T['superficie']),
                                            'backColorSecondary': color(T['superficie']), 'wordWrap': lit(True)}}],
                 'grid': [{'properties': {'gridVertical': lit(False), 'gridHorizontal': lit(True), 'gridHorizontalColor': color(T['linea']),
                                          'rowPadding': dnum(6), 'outlineColor': color(T['superficie'])}}],
                 'total': [{'properties': {'totals': lit(False)}}]}, vcObjects=marco())
    # Comparativo mes a mes
    CY = EY + EH + 16; ALTO = sec['height']; CH = ALTO - CY - G
    tx, ty, tw, th = L.seccion(G, CY, ANCHO - 2 * G, CH, 'Comparativo mes a mes',
                               'Unidades y dinero contra el mes anterior. El precio promedio explica cuando ambos no se mueven igual.')
    cols = [('DimFecha.AnioMes', 'Mes', 230), (f'{F}.RV Tabla unidades', 'Unidades', 190), (f'{F}.RV Tabla var unidades', 'Var und', 180),
            (f'{F}.RV Tabla ventas', 'Ventas USD', 220), (f'{F}.RV Tabla var ventas', 'Var USD', 180), (f'{F}.RV Tabla precio', 'Precio prom.', 190)]
    p.agregar_visual(R, 'tableEx', (tx, ty, tw, th),
        roles={'Values': [('DimFecha', 'AnioMes', None, 'Mes')] + [M(q.split('.', 1)[1], v) for q, v, _ in cols[1:]]},
        orden=('DimFecha.AnioMes', 'asc'),
        objects={'columnFormatting': [{'properties': {'alignment': lit('Right')}, 'selector': {'metadata': q}} for q, _, _ in cols[1:]],
                 'values': [{'properties': {'fontColor': color(T['texto']), 'fontSize': dnum(11), 'backColorPrimary': color(T['superficie']),
                                            'backColorSecondary': color(T['superficie'])}},
                            {'properties': {'fontColor': SEM('RV Var unidades')}, 'selector': wild(f'{F}.RV Tabla var unidades')},
                            {'properties': {'fontColor': SEM('RV Var ventas')}, 'selector': wild(f'{F}.RV Tabla var ventas')}],
                 'columnWidth': [{'properties': {'value': dnum(w)}, 'selector': {'metadata': q}} for q, _, w in cols],
                 'columnHeaders': [{'properties': {'fontColor': color(T['texto2']), 'backColor': color(T['superficie']), 'fontSize': dnum(9.5),
                                                   'fontFamily': lit(SEMI), 'outlineColor': color(T['linea'])}}],
                 'grid': [{'properties': {'gridVertical': lit(False), 'gridHorizontal': lit(True), 'gridHorizontalColor': color(T['linea']),
                                          'rowPadding': dnum(6), 'outlineColor': color(T['superficie'])}}],
                 'total': [{'properties': {'totals': lit(True), 'backColor': color(T['pagina']), 'fontColor': color(T['texto']),
                                           'fontFamily': lit(BOLD), 'fontSize': dnum(11)}}]}, vcObjects=marco())
    cfg = json.loads(sec['config']); cfg['relationships'] = [{'source': sku.id, 'target': rank.id, 'type': 3}]
    sec['config'] = json.dumps(cfg, ensure_ascii=False)
    return sec

# ------------------------------------------------------------------ armado
def construir(version):
    T = VERSIONES[version]
    p = Pbix(str(CLASICO))
    portada(p, T, version); inventario(p, T); roadmap(p, T)
    tmp = Path(tempfile.gettempdir()) / f'_rediseno_{version}.pbix'
    p.guardar(str(tmp))
    L = json.loads(zipfile.ZipFile(tmp).read('Report/Layout').decode('utf-16-le'))
    z = zipfile.ZipFile(GUARDADO)
    schema = json.loads(z.read(f"Report/definition/pages/{ID['portada']}/page.json"))['$schema']
    paginas = {}
    for clave, nombre, vista in (('portada', 'Portada', 'FitToPage'), ('inventario', 'Inventario de movimientos', 'FitToPage'),
                                 ('roadmap', 'Roadmap de ventas', 'FitToWidth')):
        s = next(x for x in L['sections'] if x['displayName'] == nombre)
        paginas[ID[clave]] = (page_json_desde_seccion(s, ID[clave], schema, vista=vista),
                              [visual_layout_a_pbir(v) for v in s['visualContainers']])
    medio = Path(tempfile.gettempdir()) / f'_rediseno_{version}_pbir.pbix'
    reemplazar_paginas(str(GUARDADO), str(medio), paginas, orden=[ID['portada'], ID['roadmap'], ID['inventario'], ID['html']],
                       activa=ID['portada'])
    destino = Path(f'salida_{version}.pbix')
    nombre_tema = 'marca_demo.json' if version == 'marca' else 'corporativo.json'
    aplicar_tema_pbir(str(medio), str(destino), tema('Tema ' + ('Marca Demo' if version == 'marca' else 'corporativo'), T), nombre_tema)
    json.dump(tema('Tema', T), open(f'tema_{version}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.remove(tmp); os.remove(medio)
    print(version, '->', destino.name, {k: len(v[1]) for k, v in paginas.items()})

if __name__ == '__main__':
    if len(sys.argv) > 2: CLASICO, GUARDADO = Path(sys.argv[1]), Path(sys.argv[2])
    for v in (sys.argv[3:] or ['marca', 'corporativo']): construir(v)
