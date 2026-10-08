from base import pagina, pie
def build(direccion='moderno', archivo='ejecutivo.html'):
    sec=[('Margen bruto','36.1 %','dn','▼ 1.2 pp','vs ene–sep 2025',"[38,37.5,37.8,37,36.5,36.8,36.2,36.4,36.1]"),
         ('Unidades','312,480','up','▲ 5.1 %','vs ene–sep 2025',"[30,31,33,34,35,35,36,37,38]"),
         ('Ticket promedio','$15.42','nt','■ 0.3 %','sin cambio relevante',"[15.2,15.3,15.1,15.4,15.3,15.5,15.4,15.4,15.42]")]
    k=''; sp=''
    for i,(l,v,c,d,ctx,serie) in enumerate(sec):
        x=24+i*272
        k+=f'''<div class="b" style="left:{x}px;top:20px;width:248px" data-pbi="card (valor) + card de texto (Δ con ícono, color por regla)">
<div class="lab">{l}</div><div class="kpi" style="margin-top:4px">{v}</div><div style="margin-top:6px;font-size:12px"><span class="{c}">{d}</span> <span class="ctx">{ctx}</span></div></div>
<div class="b" id="s{i}" style="left:{x}px;top:116px;width:224px;height:40px" data-pbi="lineChart mini (sin ejes ni leyenda)"></div>'''
        if i: k+=f'<div class="vr" style="left:{x-16}px;top:20px;height:144px"></div>'
        col = 'C("mal")' if c == 'dn' else 'C("acento")'
        sp += f"spark('s{i}',{serie},{col});"
    cuerpo=f'''
<div class="b kick" style="left:24px;top:24px" data-pbi="textbox">Dirección comercial · resumen ejecutivo</div>
<div class="b tit" style="left:24px;top:42px" data-pbi="card de texto (título-conclusión dinámico, DAX)">Las ventas crecen 8.4 % y el margen cae 1.2 pp</div>
<div class="b sub" style="left:24px;top:72px" data-pbi="card de texto (medida Periodo)">Enero–septiembre 2026 · comparado con el mismo periodo de 2025 · USD</div>
<div class="sl" style="left:752px;top:32px;width:168px" data-pbi="slicer Dropdown"><span><span class="k">Periodo</span>ene–sep 2026</span></div>
<div class="sl" style="left:928px;top:32px;width:160px" data-pbi="slicer Dropdown"><span><span class="k">Región</span>Todas</span></div>
<div class="sl" style="left:1096px;top:32px;width:160px" data-pbi="slicer Dropdown"><span><span class="k">Canal</span>Todos</span></div>
<div class="card" style="left:24px;top:104px;width:400px;height:184px" data-pbi="shape (fondo) + card héroe + card de texto Δ + lineChart mini">
 <div class="b lab" style="left:20px;top:18px">Ventas netas</div>
 <div class="b heroe" style="left:20px;top:38px">$4.82M</div>
 <div class="b" style="left:20px;top:88px;font-size:12px"><span class="up">▲ 8.4 %</span> <span class="ctx">vs ene–sep 2025 ($4.45M)</span></div>
 <div class="b" id="sh" style="left:20px;top:116px;width:360px;height:52px"></div></div>
<div class="card" style="left:440px;top:104px;width:816px;height:184px" data-pbi="shape (fondo) con 3 KPI secundarios separados por líneas">{k}</div>
<div class="card" style="left:24px;top:304px;width:800px;height:376px" data-pbi="lineChart: 2026 en acento, 2025 en gris; etiqueta solo al final; sin leyenda ni eje Y2">
 <div class="b" style="left:20px;top:16px"><div class="vt">Ventas netas por mes</div><div class="vs">Miles de USD · 2026 contra el mismo mes de 2025</div></div>
 <div class="b" id="ln" style="left:12px;top:64px;width:772px;height:300px"></div></div>
<div class="card" style="left:840px;top:304px;width:416px;height:376px" data-pbi="barChart (orden desc., etiquetas de datos, sin eje X; destacado por regla)">
 <div class="b" style="left:20px;top:16px"><div class="vt">Productos que más venden</div><div class="vs">Top 8 · miles de USD · en acento el que más crece</div></div>
 <div class="b" id="hb" style="left:12px;top:68px;width:392px;height:296px"></div></div>
{pie('ERP Ventas (FactVentas)','06/10/2026 07:30')}'''
    script=f'''const M=['ene','feb','mar','abr','may','jun','jul','ago','sep'];
linea('ln',M,[{{n:'2025',v:[380,401,433,449,470,488,503,522,551],c:C('contexto'),lc:C('tinta3')}},{{n:'2026',v:[402,438,455,470,512,531,560,598,640],c:C('acento')}}],{{f:v=>'$'+fmt(v)+'K'}});
barras('hb',['Clásico 1L','Premium 500 g','Familiar 2 kg','Snack 6 unid.','Light 1L','Orgánico 250 g','Mix 12 unid.','Edición estacional'],[812,694,560,498,421,377,302,188],{{f:v=>'$'+fmt(v)+'K',hi:1}});
spark('sh',[40,44,45,47,51,53,56,60,64]);{sp}'''
    ficha=[('Tipo / público','Ejecutivo · dirección comercial, lectura de 2–3 minutos en comité'),
       ('Premisa','El comité decide si el crecimiento es sano, porque ventas y margen pueden ir en sentidos opuestos; por eso el héroe es Ventas y el primer secundario es Margen, con el título-conclusión que los relaciona.'),
       ('Pregunta de 5 s','¿Crecemos y a qué costo? → Ventas +8.4 % con margen −1.2 pp'),
       ('Rejilla','12 col (margen 24, medianil 16, col 88); filas 104/304; héroe 4 col + 3 secundarios en 8 col'),
       ('Escala','kicker 9 pt · título 15 pt · nota 9 pt · título visual 10 pt · KPI 21 pt · héroe 27 pt'),
       ('Supuestos','Polaridad: ventas, unidades ↑ bueno; margen ↓ malo. Meta no definida (si existe, línea de referencia).')]
    open(archivo,'w',encoding='utf-8').write(pagina('Ejecutivo · referencia',direccion,cuerpo,script,ficha))
if __name__=='__main__': build()
