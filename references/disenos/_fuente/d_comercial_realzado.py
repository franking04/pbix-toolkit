"""Nivel realzado · dirección moderno (1 capa): solo efectos nativos (sombra, barra de acento, botones con estados)
y medidas SVG en la tabla. Seguimiento comercial semanal."""
from base import pagina, pie
def build(direccion='moderno', archivo='comercial_realzado.html'):
    kp = [('Ventas de la semana', '$2.84M', 'up', '▲ 4.1 %', 'vs semana 38'),
          ('Avance de la meta del mes', '98 %', 'wr', '$0.4M por cerrar', 'quedan 4 días hábiles'),
          ('Pedidos', '1,962', 'up', '▲ 2.6 %', 'vs semana 38'),
          ('Ticket promedio', '$1,447', 'nt', '■ 0.4 %', 'sin cambio relevante')]
    k = ''.join(f'''<div class="card sombra acb" style="left:{24 + i * 312}px;top:112px;width:296px;height:112px" data-pbi="cardVisual (sombra nativa + barra de acento) · referencia Δ con color por regla">
 <div class="b lab" style="left:20px;top:16px">{l}</div><div class="b kpi" style="left:20px;top:36px">{v}</div>
 <div class="b" style="left:20px;top:76px;font-size:12px"><span class="pill {c}">{d}</span> <span class="ctx">{x}</span></div></div>''' for i, (l, v, c, d, x) in enumerate(kp))
    cl = [('Distribuidora Norte', '$412K', 'up', '▲ 8.2 %', 1.08), ('Cadena Central', '$388K', 'up', '▲ 3.1 %', 1.03), ('Grupo Occidente', '$301K', 'dn', '▼ 2.4 %', .97),
          ('Mayoreo del Sur', '$264K', 'up', '▲ 1.0 %', 1.01), ('Tiendas Costa', '$219K', 'dn', '▼ 6.8 %', .92), ('Club Altiplano', '$187K', 'up', '▲ 12.5 %', 1.12)]
    filas = ''.join(f'<tr><td>{c}</td><td class="n">{v}</td><td class="n"><span class="pill {s}" style="font-size:12px">{d}</span></td>'
                    f'<td><div id="c{i}" style="width:110px;height:16px"></div></td></tr>' for i, (c, v, s, d, _) in enumerate(cl))
    js = ''.join(f"meta('c{i}',{x});" for i, (*_, x) in enumerate(cl))
    cuerpo = f'''
<div class="b kick" style="left:24px;top:22px" data-pbi="textbox">Ventas · seguimiento semanal</div>
<div class="b tit" style="left:24px;top:40px" data-pbi="card de texto (título-conclusión dinámico, DAX)">La semana 39 cierra al 98 % de la meta: faltan $0.4M para el mes</div>
<div class="b sub" style="left:24px;top:70px" data-pbi="card de texto (medida Periodo)">Semana 39 (22–28 sep 2026) · USD · contra semana anterior y meta mensual</div>
<div class="tabs" style="left:968px;top:28px" data-pbi="3 actionButton con estados (por defecto / al pasar / presionado / seleccionado) → navegación de página">
 <span class="tab on">Resumen</span><span class="tab">Clientes</span><span class="tab">Productos</span></div>
{k}
<div class="card sombra" style="left:24px;top:240px;width:752px;height:440px" data-pbi="clusteredColumnChart + línea de referencia constante (meta diaria) · hoy resaltado por regla">
 <div class="b" style="left:20px;top:16px"><div class="vt">Ventas por día</div><div class="vs">Miles de USD · septiembre 2026 · línea = meta diaria ($118K)</div></div>
 <div class="b" id="cd" style="left:12px;top:64px;width:728px;height:360px"></div></div>
<div class="card sombra" style="left:792px;top:240px;width:464px;height:440px" data-pbi="tableEx: medida SVG píldora Δ + medida SVG bullet contra objetivo (ImageUrl)">
 <div class="b" style="left:20px;top:16px"><div class="vt">Clientes principales</div><div class="vs">Ventas del mes · Δ vs agosto · avance contra objetivo</div></div>
 <div class="b" style="left:20px;top:64px;width:424px"><table><tr><th>Cliente</th><th class="n">Ventas</th><th class="n">vs ago</th><th>Objetivo</th></tr>{filas}</table></div></div>
{pie('CRM y ERP Ventas', '06/10/2026 07:30')}'''
    dias = list(range(1, 29)); dias = [d for d in dias if (d % 7) not in (6, 0)]
    vals = [96, 104, 121, 118, 99, 112, 125, 131, 108, 117, 122, 128, 135, 101, 109, 119, 126, 133, 98, 115, 124, 129, 140, 0][:len(dias)]
    script = f'''const D={[str(d) for d in dias]};const V={vals};
columnas('cd',D,V,{{f:v=>'$'+fmt(v)+'K',hi:V.length-1,lab:[V.length-1]}});
(()=>{{const s=document.querySelector('#cd svg'),w=s.clientWidth||728,h=360,L=44,R=8,T=18,B=22,mx=Math.max(...V),st=nice(mx),top=Math.ceil(mx/st)*st,y=h-B-(118/top)*(h-B-T);el('line',{{x1:L,x2:w-R,y1:y,y2:y,stroke:C('tinta2'),'stroke-dasharray':'4 3','stroke-width':1.5}},s);tx(s,L+6,y-6,'Meta $118K',{{'text-anchor':'start',fill:C('tinta2'),'font-weight':600}})}})();{js}'''
    ficha = [('Nivel / capas', 'Realzado · 1 capa: todo nativo; efectos = sombra y barra de acento (cardVisual), botones con estados, píldoras y bullets SVG en la tabla'),
             ('Tipo / público', 'Operativo-comercial · gerentes de ventas en laptop; revisión diaria de 1–2 minutos'),
             ('Premisa', 'El gerente necesita saber si llega a la meta del mes y con qué clientes; el título dice cuánto falta, las tarjetas el ritmo y la tabla a quién llamar.'),
             ('Pregunta de 5 s', '¿Llegamos a la meta? → 98 %, faltan $0.4M; Tiendas Costa y Grupo Occidente abajo'),
             ('Efectos', 'Sombra suave y barra de acento en tarjetas, pestañas como botones con estados, día actual resaltado, píldoras y bullets SVG'),
             ('Rejilla', '12 col; 4 tarjetas de 3 col; gráfico 8 col + tabla 4 col (redondeado a medianil)'),
             ('Escala', 'kicker 9 · título 15 · nota 9 · título visual 10 · KPI 21 pt'),
             ('Supuestos', 'Meta diaria constante = meta mensual / días hábiles. Ventas de hoy parciales (último día).')]
    open(archivo, 'w', encoding='utf-8').write(pagina('Comercial · realzado', direccion, cuerpo, script, ficha))
if __name__ == '__main__': build()
