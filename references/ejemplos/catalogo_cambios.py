# EJEMPLO: catálogo de cambios sobre un reporte de inventario en Layout clásico (páginas Intro e Inventario, tabla
# FactMovimientos). Sirve como plantilla: cambia nombres de página, ids de visual y campos por los de tu archivo.
"""Catálogo de cambios sobre un reporte de inventario.
Uso: python catalogo_cambios.py base.pbix salida.pbix"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from modificar_layout import Pbix, lit, dnum, color

ORIGEN = Path(sys.argv[1] if len(sys.argv) > 1 else 'base.pbix')
DESTINO = Path(sys.argv[2] if len(sys.argv) > 2 else 'base_modificado.pbix')
p = Pbix(str(ORIGEN))
ROJO, AMARILLO, BLANCO, OSCURO = '#F0391D', '#FFCD00', '#FFFFFF', '#3A2A1A'
F = 'FactMovimientos'

# 1) Texto: corregir errata en el tooltip del botón de la portada
img = p.visual('Intro', vid='ID_00010000000000000')
img.propiedad('vcObjects', 'visualLink', {'tooltip': lit('Road Map de Ventas')})

# 2) Tabla de movimientos: título, borde, posición, campos, agregación, formato condicional
t = p.visual('Inventario', tipo='tableEx')
t.titulo('Inventario – Movimientos históricos', mostrar=True, tamaño=12, color_fondo=ROJO, color_letra=BLANCO)
t.propiedad('vcObjects', 'border', {'show': lit(True), 'color': color(AMARILLO), 'radius': dnum(12)})
t.mover(y=206.0, h=504.0)
t.quitar_campo('FactMovimientos.DocumentoFiscal')                         # columna "documento fiscal"
t.renombrar_ref('Sum(FactMovimientos.CostoUnitario)', 'Avg(FactMovimientos.CostoUnitario)')   # Name decía Sum y era Avg
t.renombrar_ref('Sum(FactMovimientos.SaldoAcumulado)', 'FactMovimientos.SaldoAcumulado')      # no tiene agregación
t.renombrar_ref('Sum(FactMovimientos.SaldoValorAcumulado)', 'FactMovimientos.SaldoValorAcumulado')
t.ordenar_rol('Values', ['DimFecha.Fecha', 'FactMovimientos.CodigoProducto', 'FactMovimientos.TipoMov',
    'FactMovimientos.TipoMovDesc', 'FactMovimientos.Documento', 'Sum(FactMovimientos.Entrada)',
    'Sum(FactMovimientos.Salida)', 'Sum(FactMovimientos.Cantidad)', 'Avg(FactMovimientos.CostoUnitario)',
    'Sum(FactMovimientos.ValorMovimiento)', 'FactMovimientos.SaldoAcumulado',
    'FactMovimientos.SaldoValorAcumulado', 'FactMovimientos.CostoPromedio'])
t.gradiente('Sum(FactMovimientos.Cantidad)', F, 'Cantidad', 'Sum', minimo=BLANCO, maximo=AMARILLO)

# 3) Slicer de SKU: limpiar el Name engañoso (CountNonNull -> Max)
sku = p.visual('Inventario', tipo='advancedSlicerVisual')
sku.renombrar_ref('CountNonNull(Producto.Código)', 'Max(Producto.Código)')

# 4) Tarjetas KPI nuevas en la página Inventario (fila entre los slicers y la tabla)
def tarjeta(pagina, x, y, w, h, campo, visible, titulo):
    return p.agregar_visual(pagina, 'card', (x, y, w, h), roles={'Values': [(F, campo, 'Sum', visible)]},
        titulo=titulo,
        objects={'labels': [{'properties': {'fontSize': dnum(20), 'color': color(OSCURO)}}],
                 'categoryLabels': [{'properties': {'show': lit(False)}}]},
        vcObjects={'background': [{'properties': {'show': lit(True), 'color': color(BLANCO), 'transparency': dnum(10)}}],
                   'border': [{'properties': {'show': lit(True), 'color': color(ROJO), 'radius': dnum(12)}}],
                   'title': [{'properties': {'fontColor': color(ROJO), 'fontSize': dnum(10)}}]})
x0, ancho = 253.0, 333.0
for i, (campo, vis, tit) in enumerate([('Entrada', 'Entradas', 'Unidades que entran'),
                                       ('Salida', 'Salidas', 'Unidades que salen'),
                                       ('ValorMovimiento', 'Valor', 'Valor de los movimientos')]):
    tarjeta('Inventario', x0 + i * (ancho + 8), 116.0, ancho, 82.0, campo, vis, tit)

# 5) Filtro de página: excluir movimientos sin SKU
p.agregar_filtro('Inventario', F, 'CodigoProducto')

# 6) Página nueva con visuales de distintos tipos
p.agregar_pagina('Resumen de movimientos', fondo='#FFF8E7')
R = 'Resumen de movimientos'
p.agregar_visual(R, 'textbox', (20.0, 10.0, 900.0, 60.0), objects={'general': [{'properties': {'paragraphs': [
    {'textRuns': [{'value': 'Resumen de movimientos de inventario',
                   'textStyle': {'fontWeight': 'bold', 'fontSize': '20pt', 'color': ROJO, 'fontFamily': 'Verdana'}}]}]}}]})
p.agregar_visual(R, 'slicer', (940.0, 10.0, 320.0, 60.0), roles={'Values': [('DimFecha', 'Anio', None, 'Año')]},
    objects={'data': [{'properties': {'mode': lit('Dropdown')}}]}, titulo='Año')
for i, (campo, vis) in enumerate([('Entrada', 'Entradas'), ('Salida', 'Salidas'),
                                  ('Cantidad', 'Cantidad neta'), ('ValorMovimiento', 'Valor')]):
    tarjeta(R, 20.0 + i * 312, 85.0, 300.0, 90.0, campo, vis, vis)
p.agregar_visual(R, 'clusteredBarChart', (20.0, 190.0, 610.0, 250.0),
    roles={'Category': [('DimTipoMov', 'Descripcion', None, 'Tipo de movimiento')],
           'Y': [(F, 'Cantidad', 'Sum', 'Cantidad')]},
    titulo='Cantidad por tipo de movimiento', orden=('Sum(FactMovimientos.Cantidad)', 'desc'),
    objects={'dataPoint': [{'properties': {'fill': color(ROJO)}}],
             'labels': [{'properties': {'show': lit(True)}}]})
p.agregar_visual(R, 'lineChart', (645.0, 190.0, 615.0, 250.0),
    roles={'Category': [('DimFecha', 'Fecha', None, 'Fecha')],
           'Y': [(F, 'ValorMovimiento', 'Sum', 'Valor')]},
    titulo='Valor de los movimientos en el tiempo',
    objects={'dataPoint': [{'properties': {'fill': color(OSCURO)}}]})
top = p.agregar_visual(R, 'tableEx', (20.0, 455.0, 1240.0, 250.0),
    roles={'Values': [('DimProducto', 'Descripcion', None, 'Producto'), (F, 'Entrada', 'Sum', 'Entradas'),
                      (F, 'Salida', 'Sum', 'Salidas'), (F, 'ValorMovimiento', 'Sum', 'Valor')]},
    titulo='Movimientos por producto', orden=('Sum(FactMovimientos.ValorMovimiento)', 'desc'),
    objects={'columnHeaders': [{'properties': {'backColor': color(ROJO), 'fontColor': color(BLANCO)}}]})
p.agregar_filtro(R, 'DimProducto', 'Descripcion', visual=top)
top.gradiente('Sum(FactMovimientos.ValorMovimiento)', F, 'ValorMovimiento', 'Sum', minimo=BLANCO, maximo=ROJO)

# 7) Navegación: clonar el botón-imagen de la portada hacia la página nueva, y un botón de regreso
nueva = p.pagina(R)['name']
b = p.clonar_visual(img, 'Intro', pos=(57.43589743589743, 442.0, None, None))
b.propiedad('vcObjects', 'visualLink', {'navigationSection': lit(nueva), 'tooltip': lit('Resumen de movimientos')})
v = p.clonar_visual(img, R, pos=(1200.0, 650.0, 60.0, 60.0))
v.propiedad('vcObjects', 'visualLink', {'navigationSection': lit(p.pagina('Intro')['name']), 'tooltip': lit('Volver a la portada')})

p.guardar(str(DESTINO))
DESTINO.with_suffix('.cambios.json').write_text(json.dumps(p.log, ensure_ascii=False, indent=1), encoding='utf-8')
print('\n'.join(p.log))
