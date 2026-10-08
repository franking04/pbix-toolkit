from base import pagina, pie
def build(direccion='moderno', archivo='operativo.html'):
    T=[('✕','mal','SKUs sin stock','14','6 de alta rotación'),('!','alerta','Pedidos pendientes','128','32 con más de 48 h'),
       ('✓','bien','Entregas a tiempo','94.2 %','meta 92 %'),('✓','bien','Días de inventario','38','rango objetivo 30–45')]
    st=''
    for i,(ic,c,l,v,ctx) in enumerate(T):
        x=20+i*304
        if i: st+=f'<div class="vr" style="left:{x-16}px;top:16px;height:72px"></div>'
        st+=f'''<div class="b" style="left:{x}px;top:16px;width:272px" data-pbi="card (valor) + card de texto (ícono + estado, color por regla) + textbox">
<div class="lab"><span style="color:var(--{c});font-weight:700">{ic}</span>&nbsp; {l}</div><div class="kpi" style="margin-top:2px">{v}</div><div class="ctx" style="margin-top:2px">{ctx}</div></div>'''
    R=[('✕','mal','90482','Premium 500 g','Norte',0,'0.0','Sin stock','Reponer hoy'),('✕','mal','90118','Clásico 1L','Centro',120,'0.6','Se agota mañana','Reponer hoy'),
       ('!','alerta','91731','Familiar 2 kg','Norte',340,'1.8','Bajo mínimo','Programar compra'),('!','alerta','90655','Snack 6 unid.','Sur',410,'2.4','Bajo mínimo','Programar compra'),
       ('!','alerta','91824','Light 1L','Centro',505,'2.9','Bajo mínimo','Programar compra'),('✓','bien','90339','Orgánico 250 g','Sur',780,'4.2','En tránsito','Llega 08/10'),
       ('✓','bien','93118','Mix 12 unid.','Norte',920,'5.0','En tránsito','Llega 07/10'),('✓','bien','90442','Edición estacional','Centro',1150,'6.3','Cubierto','—'),
       ('✓','bien','90071','Clásica 500 ml','Sur',1310,'7.1','Cubierto','—')]
    rows=''.join(f'<tr><td><span style="color:var(--{c});font-weight:700">{ic}</span> <span style="color:var(--{c});font-weight:600">{e}</span></td><td>{a}</td><td>{b}</td><td style="color:var(--tinta2)">{bo}</td><td class="n">{s:,}</td><td class="n">{d}</td><td style="color:var(--tinta2)">{ac}</td></tr>' for ic,c,a,b,bo,s,d,e,ac in R)
    cuerpo=f'''
<div class="b kick" style="left:24px;top:24px" data-pbi="textbox">Operaciones · inventario</div>
<div class="b tit" style="left:24px;top:42px" data-pbi="card de texto (título-conclusión dinámico)">14 SKUs sin stock y 128 pedidos esperando</div>
<div class="b sub" style="left:24px;top:72px" data-pbi="card de texto (medida Actualizado)">Datos al 06/10/2026 07:30 · se actualiza cada mañana</div>
<div class="sl" style="left:928px;top:32px;width:160px" data-pbi="slicer Dropdown"><span><span class="k">Bodega</span>Todas</span></div>
<div class="sl" style="left:1096px;top:32px;width:160px" data-pbi="slicer Dropdown"><span><span class="k">Categoría</span>Todas</span></div>
<div class="card" style="left:24px;top:104px;width:1232px;height:104px" data-pbi="shape (fondo) + 4 estados separados por líneas">{st}</div>
<div class="card" style="left:24px;top:224px;width:808px;height:456px" data-pbi="tableEx: orden por cobertura asc.; Estado con ícono y color por regla; anchos fijos">
 <div class="b" style="left:20px;top:16px"><div class="vt">Qué requiere acción hoy</div><div class="vs">SKUs ordenados por días de cobertura · primero lo urgente</div></div>
 <div class="b" style="left:12px;top:64px;width:784px"><table><tr><th>Estado</th><th>SKU</th><th>Producto</th><th>Bodega</th><th class="n">Stock (und.)</th><th class="n">Cobertura (días)</th><th>Acción</th></tr>{rows}</table></div></div>
<div class="card" style="left:848px;top:224px;width:408px;height:220px" data-pbi="columnChart (hoy destacado por regla de color; etiqueta solo en hoy)">
 <div class="b" style="left:20px;top:16px"><div class="vt">Pedidos despachados por día</div><div class="vs">Últimos 14 días · hoy, en curso</div></div>
 <div class="b" id="cd" style="left:8px;top:64px;width:392px;height:144px"></div></div>
<div class="card" style="left:848px;top:460px;width:408px;height:220px" data-pbi="barChart (pendientes por bodega)">
 <div class="b" style="left:20px;top:16px"><div class="vt">Pendientes por bodega</div><div class="vs">Pedidos sin despachar</div></div>
 <div class="b" id="pb" style="left:8px;top:72px;width:392px;height:132px"></div></div>
{pie('WMS Inventario','06/10/2026 07:30')}'''
    script="columnas('cd',['23','24','25','26','27','28','29','30','1','2','3','4','5','6'],[182,175,190,168,201,154,160,188,193,179,205,198,186,121],{hi:13,lab:[13]});barras('pb',['Norte','Centro','Sur'],[61,44,23],{f:v=>fmt(v),L:72});"
    ficha=[('Tipo / público','Operativo · jefes de bodega y compras, revisión diaria al empezar el turno'),
       ('Premisa','El equipo actúa sobre excepciones, porque lo normal no requiere decisión; por eso el bloque principal es la lista de acción ordenada por urgencia y los estados van con ícono + texto.'),
       ('Pregunta de 5 s','¿Qué tengo que resolver hoy? → 14 SKUs sin stock, empezar por los de cobertura 0'),
       ('Rejilla','12 col; franja de estados a ancho completo; lista 9 col + 2 apoyos 3 col'),
       ('Variante','grafito para pantalla mural (mismo contenido, tokens oscuros)'),
       ('Supuestos','Umbrales: cobertura < 1 día = crítico, < 3 = alerta. Estados nunca solo por color.')]
    open(archivo,'w',encoding='utf-8').write(pagina('Operativo · referencia',direccion,cuerpo,script,ficha))
if __name__=='__main__':
    build(); build('grafito','operativo_grafito.html')
