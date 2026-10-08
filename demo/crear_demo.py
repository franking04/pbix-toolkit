"""Genera demo/demo_ventas.pbix: un .pbix SINTÉTICO para probar la skill sin un reporte propio.

Todo es inventado (empresa, productos, regiones). Solo trae metadatos: el reporte en Layout clásico y el modelo como una
pestaña de la vista TMDL. El DataModel es un marcador vacío, así que el archivo NO se abre en Power BI Desktop; sirve para
probar la lectura, el cruce reporte-modelo, la edición y la verificación.

Fallas sembradas a propósito (las debe encontrar `cruzar_reporte_modelo.py`):
  * referencia rota: la tabla de Detalle usa [Medida borrada], que no existe en el modelo;
  * medida sin uso: [Ticket promedio] no aparece en ningún visual;
  * texto de mes sin «ordenar por»: Ventas[Mes] en el eje del gráfico;
  * número guardado como texto: Ventas[Costo] es String y se suma en la tabla;
  * medida sin formato: [Ventas sin formato].

Uso: python demo/crear_demo.py [salida.pbix]   (por defecto demo/demo_ventas.pbix)
"""
import json, os, sys, zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / 'scripts'))

MODELO_TMDL = """createOrReplace

	model Model
		culture: es-PA
		defaultPowerBIDataSourceVersion: powerBI_V3
		sourceQueryCulture: es-PA

	table Ventas
		lineageTag: t-ventas

		measure 'Total ventas' = SUM(Ventas[Importe])
			formatString: \\$#,0
			displayFolder: Ventas
			lineageTag: m-total

		measure 'Unidades netas' = SUM(Ventas[Unidades])
			formatString: #,0
			lineageTag: m-unidades

		measure 'Margen %' = DIVIDE(SUM(Ventas[Importe]) - SUM(Ventas[CostoNum]), SUM(Ventas[Importe]))
			formatString: 0.0 %;-0.0 %;0.0 %
			lineageTag: m-margen

		measure 'Ventas sin formato' = SUM(Ventas[Importe])
			lineageTag: m-sinformato

		measure 'Ticket promedio' = DIVIDE([Total ventas], [Unidades netas])
			formatString: \\$#,0.00
			lineageTag: m-ticket

		column Fecha
			dataType: dateTime
			formatString: Long Date
			lineageTag: c-fecha
			summarizeBy: none
			sourceColumn: Fecha

		column Mes
			dataType: string
			lineageTag: c-mes
			summarizeBy: none
			sourceColumn: Mes

		column Producto
			dataType: string
			lineageTag: c-producto
			summarizeBy: none
			sourceColumn: Producto

		column Region
			dataType: string
			lineageTag: c-region
			summarizeBy: none
			sourceColumn: Region

		column Importe
			dataType: double
			lineageTag: c-importe
			summarizeBy: sum
			sourceColumn: Importe

		column Unidades
			dataType: int64
			formatString: 0
			lineageTag: c-unidades
			summarizeBy: sum
			sourceColumn: Unidades

		column Costo
			dataType: string
			lineageTag: c-costo
			summarizeBy: none
			sourceColumn: Costo

		column CostoNum
			dataType: double
			lineageTag: c-costonum
			summarizeBy: sum
			sourceColumn: CostoNum

		partition Ventas = m
			mode: import
			source =
					let
					    Origen = Csv.Document(File.Contents("C:\\\\demo\\\\ventas_ficticias.csv"), [Delimiter=",", Encoding=65001])
					in
					    Origen

	table Region
		lineageTag: t-region

		column Region
			dataType: string
			lineageTag: c-region-dim
			summarizeBy: none
			sourceColumn: Region

		partition Region = m
			mode: import
			source = #table({"Region"}, {{"Norte"}, {"Centro"}, {"Sur"}})

	relationship r-ventas-region
		fromColumn: Ventas.Region
		toColumn: Region.Region
"""


def campo(tipo, entidad, prop, agg=None):
    """Select de prototypeQuery: Measure, Column o Aggregation sobre la tabla con alias v (Ventas) o r (Region)."""
    alias = 'v' if entidad == 'Ventas' else 'r'
    col = {'Expression': {'SourceRef': {'Source': alias}}, 'Property': prop}
    if tipo == 'measure':
        return {'Measure': col, 'Name': f'{entidad}.{prop}'}
    if agg is None:
        return {'Column': col, 'Name': f'{entidad}.{prop}'}
    return {'Aggregation': {'Expression': {'Column': col}, 'Function': agg}, 'Name': f'Sum({entidad}.{prop})'}


def visual(vid, tipo, pos, roles, z, titulo=None, extra_cfg=None):
    """Contenedor de visual en Layout clásico. roles = {rol: [select, ...]}."""
    x, y, w, h = pos
    selects = [s for lista in roles.values() for s in lista]
    entidades = sorted({s['Name'].split('(')[-1].split('.')[0] for s in selects})
    cfg = {'name': vid, 'layouts': [{'id': 0, 'position': {'x': x, 'y': y, 'z': z, 'width': w, 'height': h, 'tabOrder': z}}],
           'singleVisual': {'visualType': tipo,
                            'projections': {rol: [{'queryRef': s['Name']} for s in lista] for rol, lista in roles.items()},
                            'prototypeQuery': {'Version': 2,
                                               'From': [{'Name': 'v' if e == 'Ventas' else 'r', 'Entity': e, 'Type': 0}
                                                        for e in entidades],
                                               'Select': selects}}}
    if titulo:
        cfg['singleVisual']['vcObjects'] = {'title': [{'properties': {
            'show': {'expr': {'Literal': {'Value': 'true'}}},
            'text': {'expr': {'Literal': {'Value': f"'{titulo}'"}}}}}]}
    if extra_cfg:
        cfg['singleVisual'].update(extra_cfg)
    return {'x': x, 'y': y, 'z': z, 'width': w, 'height': h, 'config': json.dumps(cfg, ensure_ascii=False), 'filters': '[]'}


def filtro_no_vacio(entidad, prop):
    """Filtro de página «no está en blanco» sobre una columna."""
    col = {'Column': {'Expression': {'SourceRef': {'Entity': entidad}}, 'Property': prop}}
    cond = {'Not': {'Expression': {'Comparison': {'ComparisonKind': 0,
                                                  'Left': {'Column': {'Expression': {'SourceRef': {'Source': 'r'}}, 'Property': prop}},
                                                  'Right': {'Literal': {'Value': 'null'}}}}}}
    return {'name': 'FiltroRegion', 'expression': col, 'type': 'Categorical', 'howCreated': 1,
            'filter': {'Version': 2, 'From': [{'Name': 'r', 'Entity': entidad, 'Type': 0}], 'Where': [{'Condition': cond}]}}


def construir(salida):
    resumen = [
        visual('kpiVentas', 'card', (24, 24, 280, 120), {'Values': [campo('measure', 'Ventas', 'Total ventas')]}, 1000, 'Ventas netas'),
        visual('kpiMargen', 'card', (320, 24, 280, 120), {'Values': [campo('measure', 'Ventas', 'Margen %')]}, 2000, 'Margen bruto'),
        visual('slRegion', 'slicer', (980, 24, 276, 120), {'Values': [campo('column', 'Region', 'Region')]}, 3000),
        visual('colMes', 'clusteredColumnChart', (24, 168, 820, 528),
               {'Category': [campo('column', 'Ventas', 'Mes')], 'Y': [campo('measure', 'Ventas', 'Total ventas')]}, 4000,
               'Ventas netas por mes'),
        visual('tablaProd', 'tableEx', (868, 168, 388, 528),
               {'Values': [campo('column', 'Ventas', 'Producto'), campo('column', 'Ventas', 'Costo', agg=0),
                           campo('measure', 'Ventas', 'Unidades netas')]}, 5000, 'Productos'),
    ]
    detalle = [
        visual('tablaDet', 'tableEx', (24, 24, 1232, 672),
               {'Values': [campo('column', 'Ventas', 'Fecha'), campo('column', 'Ventas', 'Producto'),
                           campo('measure', 'Ventas', 'Ventas sin formato'), campo('measure', 'Ventas', 'Medida borrada')]},
               1000, 'Detalle de ventas'),
    ]
    secciones = [
        {'name': 'ReportSectionResumen', 'displayName': 'Resumen', 'displayOption': 1, 'width': 1280, 'height': 720,
         'ordinal': 0, 'config': '{}', 'filters': json.dumps([filtro_no_vacio('Region', 'Region')]),
         'visualContainers': resumen},
        {'name': 'ReportSectionDetalle', 'displayName': 'Detalle', 'displayOption': 1, 'width': 1280, 'height': 720,
         'ordinal': 1, 'config': '{}', 'filters': '[]', 'visualContainers': detalle},
    ]
    layout = {'id': 0, 'resourcePackages': [], 'sections': secciones, 'layoutOptimization': 0, 'filters': '[]',
              'config': json.dumps({'version': '5.73', 'themeCollection': {'baseTheme': {'name': 'CY26SU05'}},
                                    'activeSectionIndex': 0})}
    tipos = ('<?xml version="1.0" encoding="utf-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="json" ContentType="" /><Override PartName="/Version" ContentType="" /></Types>')
    tmp = str(salida) + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', tipos)
        z.writestr('Version', '1.28'.encode('utf-16-le'))
        z.writestr('Metadata', json.dumps({'Version': 5, 'CreatedFrom': 'Cloud', 'CreatedFromRelease': '2026.05'}).encode('utf-16-le'))
        z.writestr('Settings', json.dumps({'Version': 4}).encode('utf-16-le'))
        z.writestr('Report/Layout', json.dumps(layout, ensure_ascii=False).encode('utf-16-le'))
        z.writestr(zipfile.ZipInfo('DataModel'), 'Demo sintético: sin modelo binario.'.encode('utf-16-le'),
                   compress_type=zipfile.ZIP_STORED)
    from scripts_modelo import incrustar
    incrustar(tmp, str(salida), tmdl={'Modelo': MODELO_TMDL})
    os.remove(tmp)
    return salida


if __name__ == '__main__':
    if any(a in ('-h', '--help') for a in sys.argv[1:]):
        print(__doc__.strip()); sys.exit(0)
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI / 'demo_ventas.pbix'
    print('demo →', construir(destino))
