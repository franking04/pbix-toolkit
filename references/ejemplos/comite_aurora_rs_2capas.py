"""EJEMPLO VIGENTE [probado en el Desktop para RS 2026.05 y publicado en el servidor RS]: diseño de 2 capas en Layout clásico
con fondo, tema, cardVisual + cardImage SVG, tabla top N con píldoras SVG y medidas incrustadas.
Réplica de references/disenos/comite_aurora (nivel impactante) sobre una COPIA de un .pbix de inventario guardado por el
Desktop para RS 2026.05 (Layout clásico, tabla FactMovimientos y medidas RV). La base no se toca. Ajusta nombres y campos.
  * Tema aurora (tema_powerbi, 2 capas: visuales sin fondo ni borde) + imagen de fondo comite_aurora_fondo.png (fondo_pagina).
  * Visuales nativos en las cajas de comite_aurora_visuales.json (coordenadas de Power BI), con los campos del modelo.
  * Medidas nuevas (Δ vs mes anterior y SVG en la dirección aurora) INCRUSTADAS con scripts_modelo: pestaña TMDL «1 Aplicar
    medidas comité» + pestaña DAX «2 Comprobar medidas comité». Hasta que el usuario pulse Aplicar, los visuales que las usan muestran error.
  * Lo que no se puede por script (Deneb) usa la alternativa nativa del mapa del diseño (areaChart).
Uso: python comite_aurora_rs_2capas.py base_rs.pbix salida.pbix"""
import json, os, sys, tempfile
from pathlib import Path
AQUI = Path(__file__).resolve().parent
R = AQUI.parents[1]
sys.path.insert(0, str(R / 'scripts'))
from modificar_layout import Pbix, lit, dnum, dint, color
from componentes import SEMI, REG, BOLD, alto_min
from fondo_pagina import fondo_clasico
from tema_powerbi import DIRECCIONES, tema
from plataforma import detectar
import svg_medidas as S
import scripts_modelo as SM

D = R / 'references' / 'disenos'
BASE = Path(sys.argv[1] if len(sys.argv) > 1 else 'base_rs.pbix')
DESTINO = Path(sys.argv[2] if len(sys.argv) > 2 else 'comite_aurora_rs.pbix')
# Notas de RS 2026.05 [probado]: título y periodo de una línea en cardVisual de 36–48 px salen cortados → card clásica de ancho
# medido (text measure del CLI); customFormatString de cardVisual se ignora → medidas de presentación con formato #,0.
# La variación compara mes contra mes anterior ([RV Var ultimo mes]); comparar el total del periodo contra UN mes da ▲595 %.
F = 'FactMovimientos'
T = DIRECCIONES['aurora']
PAGINA = 'Comité · aurora'
SIN_CAJA = {'background': [{'properties': {'show': lit(False)}}], 'border': [{'properties': {'show': lit(False)}}],
            'visualHeader': [{'properties': {'show': lit(False)}}]}
DEF = {'id': 'default'}

def M(n, vis=None): return (F, n, 'measure', vis)
def medida_expr(n): return {'expr': {'Measure': {'Expression': {'SourceRef': {'Entity': F}}, 'Property': n}}}

# ------------------------------------------------------------------ medidas incrustadas (dirección aurora)
# NOTA (regla 2.6.1): hoy la skill pone la cifra NATIVA al lado y el SVG solo con forma (cifras=False por defecto). Este ejemplo
# se probó con la cifra dentro del SVG en "en-US"; se dejan esos parámetros para reproducirlo tal cual.
def medidas():
    """Variación = [RV Var ultimo mes] del modelo: último mes con ventas vs el mes anterior con datos, EN EL CONTEXTO DE LA FILA."""
    C = 'Comité aurora'; P = "DimProducto[Descripcion]"
    rank = {'nombre': 'CA Rank ventas producto', 'expr': f'IF(ISINSCOPE({P}), RANKX(ALLSELECTED({P}), [RV Ventas netas], , DESC, Dense))',
            'formato': '0', 'carpeta': C, 'descripcion': 'Posición del producto por ventas netas en lo seleccionado.'}
    top = {'nombre': 'CA Ventas top 6', 'carpeta': C, 'formato': r'\$#,0',
           'descripcion': 'Ventas netas de los 6 primeros productos (blanco para el resto: la fila no se muestra).',
           'expr': f'IF(ISINSCOPE({P}), IF([CA Rank ventas producto] <= 6, [RV Ventas netas]), SUMX(TOPN(6, ALLSELECTED({P}), [RV Ventas netas]), [RV Ventas netas]))'}
    pil = S.pildora('CA SVG variacion ventas', '[RV Var ultimo mes]', direccion='aurora', cifras=True, cultura='en-US')
    pil_top = {'nombre': 'CA SVG variacion top 6', 'carpeta': C, 'categoria': 'ImageUrl',
               'descripcion': 'Píldora Δ último mes solo para los 6 primeros productos.',
               'expr': f'IF(NOT ISINSCOPE({P}) || [CA Rank ventas producto] <= 6, [CA SVG variacion ventas])'}
    heroe = S.pildora('CA SVG variacion heroe', '[RV Var ultimo mes]', direccion='aurora', ancho=172, sufijo=' vs mes ant.', cifras=True, cultura='en-US')
    ani = S.anillo('CA SVG margen', '[RV Margen bruto]', direccion='aurora', tam=64, cifras=True, cultura='en-US')
    sel = lambda m: {**{k: m[k] for k in ('nombre', 'expr', 'categoria', 'descripcion') if k in m}, 'carpeta': C}
    pres = [{'nombre': f'CA {n}', 'expr': f'[RV {n}]', 'formato': '#,0', 'carpeta': C,
             'descripcion': f'[RV {n}] con separador de miles (la tarjeta ignora customFormatString en RS 2026.05).'}
            for n in ('Unidades netas', 'Importaciones')]
    return [rank, top, sel(pil), pil_top, sel(heroe), sel(ani)] + pres

def comprobar_dax():
    """Consultas agregadas (el usuario las ejecuta) + alarma de semántica: |Δ| > 200 % en la mayoría de filas."""
    return ('// 1) Totales y alarma: "filas_delta_mayor_200" debe ser una minoría de "filas_con_delta"\n'
            'EVALUATE\nVAR _t = ADDCOLUMNS ( VALUES ( DimProducto[Descripcion] ), "@d", [RV Var ultimo mes] )\n'
            'RETURN ROW (\n\t"var_total_ultimo_mes", [RV Var ultimo mes],\n'
            '\t"filas_con_delta", COUNTROWS ( FILTER ( _t, NOT ISBLANK ( [@d] ) ) ),\n'
            '\t"filas_delta_mayor_200", COUNTROWS ( FILTER ( _t, ABS ( [@d] ) > 2 ) ),\n'
            '\t"largo_pildora_heroe", LEN ( [CA SVG variacion heroe] ),\n\t"largo_anillo", LEN ( [CA SVG margen] )\n)\n\n'
            '// 2) Top 6 por ventas con su Δ último mes (lo que muestra la tabla)\n'
            'EVALUATE\nTOPN ( 6, SUMMARIZECOLUMNS ( DimProducto[Descripcion], "ventas", [RV Ventas netas], "delta_ultimo_mes", [RV Var ultimo mes] ), [ventas], DESC )\n'
            'ORDER BY [ventas] DESC\n')

# ------------------------------------------------------------------ visuales
def texto(p, x, y, w, h, runs, alinear='left'):
    par = {'textRuns': [{'value': t, 'textStyle': {'fontSize': f'{pt}pt', 'color': c, 'fontFamily': SEMI if b else REG}} for t, pt, c, b in runs],
           'horizontalTextAlignment': alinear}
    return p.agregar_visual(PAGINA, 'textbox', (x, y, w, max(h, alto_min(max(r[1] for r in runs) / 0.75))),
                            objects={'general': [{'properties': {'paragraphs': [par]}}]}, vcObjects={**SIN_CAJA, 'title': [{'properties': {'show': lit(False)}}]})

def tarjeta(p, caja, medida, etiqueta, imagen=None, alto_img=64, tam=27, formato=None):
    """cardVisual transparente (la caja está pintada en la imagen de fondo); imagen = medida SVG en cardImage [probado]."""
    # unidades «ninguna» (dint 1): «auto» sale en el idioma del Desktop («$152 mil») [probado]; formato = cadena propia
    val = {'fontSize': dnum(tam), 'fontColor': color(T['texto']), 'fontFamily': lit(SEMI), 'labelDisplayUnits': dint(1)}
    # customFormatString: ignorado por el Desktop para RS 2026.05 [probado] → el formato sale de la medida
    objs = {'value': [{'properties': val, 'selector': DEF}],
            'label': [{'properties': {'show': lit(True), 'text': lit(etiqueta), 'fontColor': color(T['texto2']), 'fontSize': dnum(11),
                                      'position': lit('aboveValue')}, 'selector': DEF}],
            'fillCustom': [{'properties': {'show': lit(False)}, 'selector': DEF}],
            'outline': [{'properties': {'show': lit(False)}, 'selector': DEF}],
            'divider': [{'properties': {'show': lit(False)}, 'selector': DEF}]}   # sin línea entre valor e imagen
    if imagen:
        objs['cardImage'] = [{'properties': {'show': lit(True), 'imageType': lit('imageUrl'), 'imageUrl': medida_expr(imagen),
                                             'imageUrlFit': lit('Normal'), 'imageHeight': lit(alto_img)}, 'selector': DEF}]   # con Fit la píldora llena la tarjeta
    return p.agregar_visual(PAGINA, 'cardVisual', (caja['x'], caja['y'], caja['w'], caja['h']), roles={'Data': [M(medida, etiqueta)]},
                            objects=objs, vcObjects={**SIN_CAJA, 'title': [{'properties': {'show': lit(False)}}]})

def titulo_visual(t, sub):
    return {**SIN_CAJA, 'title': [{'properties': {'show': lit(True), 'text': lit(t), 'fontColor': color(T['texto']), 'fontSize': dnum(12),
                                                  'fontFamily': lit(SEMI)}}],
            'subTitle': [{'properties': {'show': lit(True), 'text': lit(sub), 'fontColor': color(T['texto2']), 'fontSize': dnum(10)}}]}

def construir():
    info = detectar(str(BASE)); assert info['plataforma'] == 'report_server' and info['formato_reporte'] == 'Layout', info
    cajas = {c['orden']: c for c in json.load(open(D / 'comite_aurora_visuales.json', encoding='utf-8'))['cajas']}
    p = Pbix(str(BASE))
    s = p.agregar_pagina(PAGINA)
    fondo_clasico(p, s['name'], open(D / 'comite_aurora_fondo.png', 'rb').read(), 'fondo_comite_aurora.png', papel=T['pagina'])
    c = cajas
    texto(p, c[0]['x'], c[0]['y'] - 6, 420, 24, [('Comité de dirección · Inventario de ventas', 9, T['acento'], True)])
    # título-conclusión y periodo: medidas de texto del modelo (card clásica: valor centrado → cardVisual alineado a la izquierda [por validar])
    # card clásica: valor centrado en su caja [probado]; ancho = texto por defecto medido con `powerbi-report-author text measure`
    # (título 422 px a 16 pt semibold → caja 520: entran títulos con producto; periodo 169 px → 220). cardVisual de 48/36 px: cortado.
    for k, med, tam, ancho, alto, col, fam in ((1, 'RV Titulo', 16, 520, 40, T['texto'], SEMI), (2, 'RV Periodo', 10, 220, 30, T['texto2'], REG)):
        p.agregar_visual(PAGINA, 'card', (c[k]['x'], c[k]['y'] - (8 if k == 1 else 4), ancho, alto), roles={'Values': [M(med, ' ')]},
                         vcObjects={**SIN_CAJA, 'title': [{'properties': {'show': lit(False)}}]},
                         objects={'labels': [{'properties': {'fontSize': dnum(tam), 'color': color(col), 'fontFamily': lit(fam)}}],
                                  'categoryLabels': [{'properties': {'show': lit(False)}}]})
    # slicers desplegables (la píldora está pintada en la imagen)
    for k, (ent, col, txt) in ((3, ('DimProducto', 'Descripcion', 'Producto')), (4, ('DimTipoMov', 'Descripcion', 'Movimiento'))):
        # etiqueta dentro de la píldora pintada en el fondo (sin ella solo se ve «Todas»)
        texto(p, c[k]['x'] + 10, c[k]['y'] + 2, 76, 28, [(txt, 9, T['texto2'], False)])
        p.agregar_visual(PAGINA, 'slicer', (c[k]['x'] + 82, c[k]['y'], c[k]['w'] - 90, c[k]['h']), roles={'Values': [(ent, col, None, txt)]},
                         vcObjects={**SIN_CAJA, 'title': [{'properties': {'show': lit(False)}}]},
                         objects={'data': [{'properties': {'mode': lit('Dropdown')}}], 'header': [{'properties': {'show': lit(False)}}],
                                  'items': [{'properties': {'fontColor': color(T['texto']), 'background': color(T['superficie']), 'textSize': dnum(10)}}]})
    # héroe + 3 tarjetas
    tarjeta(p, c[5], 'RV Ventas netas', 'Ventas netas acumuladas', imagen='CA SVG variacion heroe', alto_img=20, tam=36, formato='$#,0')
    tarjeta(p, c[6], 'RV Margen bruto', 'Margen bruto', imagen='CA SVG margen', formato='0.0%')
    tarjeta(p, c[7], 'CA Unidades netas', 'Unidades netas')
    tarjeta(p, c[8], 'CA Importaciones', 'Importaciones recibidas')
    # gráfico (alternativa nativa a Deneb: areaChart transparente)
    g = c[9]
    p.agregar_visual(PAGINA, 'areaChart', (g['x'], g['y'], g['w'], g['h']),
                     roles={'Category': [('DimFecha', 'AnioMes', None, 'Mes')], 'Y': [M('RV Ventas netas', 'Ventas netas')]},
                     orden=('DimFecha.AnioMes', 'asc'), vcObjects=titulo_visual('Ventas netas por mes', 'USD · por mes'),
                     objects={'dataPoint': [{'properties': {'fill': color(T['acento'])}}],
                              'categoryAxis': [{'properties': {'showAxisTitle': lit(False), 'labelColor': color(T['texto2']), 'fontSize': dnum(9)}}],
                              'valueAxis': [{'properties': {'showAxisTitle': lit(False), 'labelColor': color(T['texto2']), 'fontSize': dnum(9), 'labelDisplayUnits': dint(1),
                                                            'gridlineColor': color(T['linea'])}}],
                              'legend': [{'properties': {'show': lit(False)}}]})
    # tabla top 6: medidas en blanco fuera del top → sin filas de más ni barra (no hay un filtro Top N guardado por el Desktop para copiar)
    t = c[10]
    p.agregar_visual(PAGINA, 'tableEx', (t['x'], t['y'], t['w'], t['h']),
                     roles={'Values': [('DimProducto', 'Descripcion', None, 'Producto'), M('CA Ventas top 6', 'Ventas'),
                                       M('CA SVG variacion top 6', 'Δ último mes')]},
                     orden=(f'{F}.CA Ventas top 6', 'desc'), vcObjects=titulo_visual('Top 6 productos por ventas', 'Δ último mes con ventas vs el anterior'),
                     objects={'grid': [{'properties': {'imageWidth': dnum(76), 'imageHeight': dnum(20), 'gridVertical': lit(False),
                                                       'gridHorizontalColor': color(T['linea']), 'rowPadding': dnum(4)}}],
                              'columnWidth': [{'properties': {'value': dnum(w)}, 'selector': {'metadata': q}}
                                              for q, w in (('DimProducto.Descripcion', 196), (f'{F}.CA Ventas top 6', 84), (f'{F}.CA SVG variacion top 6', 92))],
                              'columnHeaders': [{'properties': {'fontColor': color(T['texto2']), 'fontSize': dnum(9), 'wordWrap': lit(False)}}],
                              'values': [{'properties': {'fontColor': color(T['texto']), 'fontSize': dnum(10), 'wordWrap': lit(False)}}]})
    # pie de confianza
    texto(p, c[11]['x'], c[11]['y'] - 8, 900, 24, [('Fuente: ', 9, T['texto2'], False), ('Inventario de movimientos (Excel)', 9, T['texto'], True),
                                                  (' · medidas RV del modelo · réplica de comite_aurora (2 capas)', 9, T['texto2'], False)])
    p.ordenar_paginas([s['name']] + [x['name'] for x in p.layout['sections'] if x is not s], activa=s['name'])
    p.tema_personalizado(tema('Tema aurora', T))
    tmp = Path(tempfile.gettempdir()) / '_comite_aurora_sin_medidas.pbix'; p.guardar(str(tmp))
    ms = medidas()
    comprobar = comprobar_dax()
    SM.incrustar(str(tmp), str(DESTINO), tmdl={'1 Aplicar medidas comité': SM.tmdl_medidas(F, ms)},
                 dax={'2 Comprobar medidas comité': comprobar}, por_defecto='1 Aplicar medidas comité')
    os.remove(tmp)
    return DESTINO, ms

if __name__ == '__main__':
    d, ms = construir()
    print('->', d, '| medidas incrustadas:', [m['nombre'] for m in ms])
