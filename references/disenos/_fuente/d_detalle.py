from base import pagina, pie
def build(direccion='suizo', archivo='detalle.html'):
    R=[('02/09/2026','Compra','OC-24518',1200,0,'6.12','7,344.00',3420,'20,931.40'),('03/09/2026','Venta','FA-88213',0,-310,'6.12','−1,897.20',3110,'19,034.20'),
       ('05/09/2026','Venta','FA-88340',0,-245,'6.12','−1,499.40',2865,'17,534.80'),('08/09/2026','Nota de crédito','NC-1031',18,0,'6.12','110.16',2883,'17,644.96'),
       ('11/09/2026','Compra','OC-24602',800,0,'6.20','4,960.00',3683,'22,604.96'),('12/09/2026','Venta','FA-88702',0,-420,'6.14','−2,578.80',3263,'20,026.16'),
       ('16/09/2026','Venta','FA-88911',0,-388,'6.14','−2,382.32',2875,'17,643.84'),('19/09/2026','Ajuste','AJ-0207',0,-12,'6.14','−73.68',2863,'17,570.16'),
       ('23/09/2026','Venta','FA-89150',0,-505,'6.14','−3,100.70',2358,'14,469.46'),('26/09/2026','Compra','OC-24771',1000,0,'6.25','6,250.00',3358,'20,719.46'),
       ('29/09/2026','Venta','FA-89402',0,-362,'6.17','−2,233.54',2996,'18,485.92')]
    q=lambda v:'' if v==0 else (f'{v:,}' if v>0 else f'−{abs(v):,}')
    rows=''.join(f'<tr><td>{a}</td><td>{b}</td><td style="color:var(--tinta2)">{c}</td><td class="n">{q(d)}</td><td class="n">{q(e)}</td><td class="n" style="color:var(--tinta2)">{f}</td><td class="n">{g}</td><td class="n" style="font-weight:600">{h:,}</td><td class="n">{i}</td></tr>' for a,b,c,d,e,f,g,h,i in R)
    K=[('Saldo inicial','2,220','01/09/2026'),('Entradas','+3,018','3 compras · 1 nota de crédito'),('Salidas','−2,242','6 ventas · 1 ajuste'),('Saldo final','2,996','valorizado $18,485.92')]
    kp=''.join(f'<div class="b" style="left:{24+i*248}px;top:160px" data-pbi="card (valor) + textbox (etiqueta y contexto), sin caja"><div class="lab">{l} <span class="ctx">und.</span></div><div class="kpi" style="font-size:24px;margin-top:2px">{v}</div><div class="ctx" style="margin-top:2px">{c}</div></div>' for i,(l,v,c) in enumerate(K))
    btn=lambda t,on: f'<span style="font-size:12px;padding:6px 11px;border-radius:6px;border:1px solid {"var(--acento)" if on else "var(--linea)"};background:{"var(--acento)" if on else "transparent"};color:{"#fff" if on else "var(--tinta2)"}">{t}</span>'
    cuerpo=f'''
<div class="b kick" style="left:24px;top:24px" data-pbi="textbox">Inventario · detalle</div>
<div class="b tit" style="left:24px;top:42px" data-pbi="card de texto (producto y periodo seleccionados)">Inventario — 90118 Clásico 1L · septiembre 2026</div>
<div class="b sub" style="left:24px;top:72px" data-pbi="textbox">Cada fila es un movimiento · cantidades en unidades, valores en USD</div>
<div class="sl" style="left:24px;top:104px;width:232px" data-pbi="slicer Between (fecha)"><span><span class="k">Fecha</span>01/09/2026 – 30/09/2026</span></div>
<div class="sl" style="left:264px;top:104px;width:264px" data-pbi="slicer Dropdown con búsqueda"><span><span class="k">Producto</span>90118 · Clásico 1L</span></div>
<div class="sl" style="left:536px;top:104px;width:168px" data-pbi="slicer Dropdown"><span><span class="k">Bodega</span>Centro</span></div>
<div class="b" style="left:728px;top:106px;display:flex;gap:6px" data-pbi="advancedSlicerVisual (botones; seleccionado = acento)">{btn('Todos',True)}{btn('Compra',False)}{btn('Venta',False)}{btn('Nota de crédito',False)}{btn('Ajuste',False)}</div>
<div class="hr" style="left:24px;top:148px;width:1232px"></div>
{kp}
<div class="hr" style="left:24px;top:232px;width:1232px"></div>
<div class="b" style="left:24px;top:240px;width:1232px" data-pbi="tableEx: anchos fijos, displayName legibles, números a la derecha, signo −, totales con regla; fechas dd/mm/yyyy">
 <table><tr><th>Fecha</th><th>Movimiento</th><th>Documento</th><th class="n">Entrada</th><th class="n">Salida</th><th class="n">Costo unit. ($)</th><th class="n">Valor mov. ($)</th><th class="n">Saldo (und.)</th><th class="n">Saldo valorizado ($)</th></tr>
 {rows}<tr class="tot"><td>Total</td><td></td><td></td><td class="n">3,018</td><td class="n">−2,242</td><td></td><td class="n">4,972.52</td><td class="n">2,996</td><td class="n">18,485.92</td></tr></table></div>
{pie('ERP Inventario (FactMovimientos)','06/10/2026 07:30','Exportar: solo datos resumidos en Report Server')}'''
    ficha=[('Tipo / público','Detalle · analistas y operación que consultan registros y concilian saldos'),
       ('Premisa','El usuario verifica movimientos uno a uno, porque concilia contra documentos; por eso la tabla es protagonista, con saldo inicial/final arriba y columnas legibles.'),
       ('Pregunta de 5 s','¿Cuadra el saldo? → inicial 2,220 + 3,018 − 2,242 = 2,996'),
       ('Rejilla','12 col; sin tarjetas; filtros en una fila; resumen en línea; tabla a ancho completo'),
       ('Escala','tabla 9 pt; resumen 18 pt (sin caja); título 15 pt'),
       ('Supuestos','Unidad en el encabezado de columna, no en cada celda. SKU fuera de la tabla porque ya está filtrado.')]
    open(archivo,'w',encoding='utf-8').write(pagina('Detalle · referencia',direccion,cuerpo,'',ficha))
if __name__=='__main__': build()
