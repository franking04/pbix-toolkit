from base import pagina, pie, T
def build(direccion='suizo', archivo='analitico.html'):
    D=T['direcciones'][direccion]; ramp=D['secuencial']
    regs=['Norte','Centro','Sur','Occidente']; cats=['Lácteos','Snacks','Bebidas','Repostería','Orgánicos']
    H=[[122,78,141,52,58],[177,64,133,189,54],[169,94,49,62,151],[147,57,101,63,181]]; mx=max(map(max,H))
    def cell(v):
        k=min(5,int(v/mx*5.99)); return f'<td class="n" style="background:{ramp[k]};color:{"#fff" if k>=4 else D["tinta"]};border-bottom:2px solid {D["pagina"]}">${v}K</td>'
    hm='<tr><th></th>'+''.join(f'<th class="n">{c}</th>' for c in cats)+'</tr>'+''.join('<tr><td>'+r+'</td>'+''.join(cell(v) for v in H[i])+'</tr>' for i,r in enumerate(regs))
    chk=lambda n,on: f'<div style="display:flex;align-items:center;gap:8px;font-size:12px;margin:6px 0;color:var(--tinta)"><span style="width:14px;height:14px;border-radius:3px;border:1.5px solid {"var(--acento)" if on else "var(--contexto)"};background:{"var(--acento)" if on else "transparent"};display:inline-block"></span>{n}</div>'
    cuerpo=f'''
<div class="b kick" style="left:24px;top:24px" data-pbi="textbox">Análisis comercial</div>
<div class="b tit" style="left:24px;top:42px" data-pbi="textbox">Snacks explica la mitad del crecimiento</div>
<div class="b sub" style="left:24px;top:72px" data-pbi="card de texto (filtros activos)">ene–sep 2026 vs ene–sep 2025 · 3 de 4 regiones · todos los canales · USD</div>
<div class="b" style="left:24px;top:112px;width:184px;height:560px" data-pbi="slicers en columna: Between (fecha) y List con casillas (región, canal); sin cajas">
 <div class="lab" style="font-weight:600">Periodo</div>
 <div class="sl" style="left:0;top:22px;width:184px"><span>01/01/2026 – 30/09/2026</span></div>
 <div class="b lab" style="left:0;top:76px;font-weight:600">Región</div><div class="b" style="left:0;top:94px">{''.join(chk(r,i!=2) for i,r in enumerate(regs))}</div>
 <div class="b lab" style="left:0;top:232px;font-weight:600">Canal</div><div class="b" style="left:0;top:250px">{''.join(chk(c,True) for c in ['Autoservicio','Mayorista','Tradicional','En línea'])}</div>
 <div class="b ctx" style="left:0;top:520px;width:184px">Los filtros aplican a toda la página</div></div>
<div class="vr" style="left:224px;top:112px;height:560px"></div>
<div class="b" style="left:248px;top:112px;width:496px;height:264px" data-pbi="lineChart con small multiples por categoría (o 3 lineChart con escala fija igual)">
 <div class="vt">Tendencia por categoría</div><div class="vs">Miles de USD por mes · misma escala en las tres</div>
 <div class="b lab" style="left:0;top:56px">Snacks</div><div class="b" id="m1" style="left:0;top:72px;width:152px;height:184px"></div>
 <div class="b lab" style="left:172px;top:56px">Lácteos</div><div class="b" id="m2" style="left:172px;top:72px;width:152px;height:184px"></div>
 <div class="b lab" style="left:344px;top:56px">Bebidas</div><div class="b" id="m3" style="left:344px;top:72px;width:152px;height:184px"></div></div>
<div class="vr" style="left:760px;top:112px;height:264px"></div>
<div class="b" style="left:776px;top:112px;width:480px;height:264px" data-pbi="scatterChart (X precio prom., Y unidades, detalle producto; destacado por regla)">
 <div class="vt">Precio contra volumen</div><div class="vs">Cada punto es un producto</div>
 <div class="b" id="sc" style="left:0;top:48px;width:480px;height:212px"></div></div>
<div class="hr" style="left:248px;top:392px;width:1008px"></div>
<div class="b" style="left:248px;top:408px;width:600px" data-pbi="pivotTable con escala de fondo de un solo tono">
 <div class="vt">Ventas por región y categoría</div><div class="vs">Miles de USD · más oscuro = más ventas</div>
 <table style="margin-top:10px">{hm}</table></div>
<div class="vr" style="left:864px;top:408px;height:264px"></div>
<div class="b" style="left:880px;top:408px;width:376px;height:264px" data-pbi="barChart (variación ±; color por signo; eje en cero; etiquetas)">
 <div class="vt">Cambio contra el año anterior</div><div class="vs">Por categoría · puntos porcentuales</div>
 <div class="b" id="dv" style="left:0;top:52px;width:376px;height:200px"></div></div>
{pie('ERP Ventas (FactVentas)','06/10/2026 07:30')}'''
    script=r'''
const M=['ene','may','sep'];
function mini(id,v){const [s,w,h]=svg(id);const T=8,B=20,top=200,Y=x=>h-B-(x/top)*(h-B-T),X=i=>4+i*(w-16)/(v.length-1);
 [0,100,200].forEach(g=>el('line',{x1:0,x2:w,y1:Y(g),y2:Y(g),stroke:C('linea')},s));
 el('polyline',{points:v.map((x,i)=>X(i)+','+Y(x)).join(' '),fill:'none',stroke:C('acento'),'stroke-width':2,'stroke-linejoin':'round'},s);
 const L=v.length-1;el('circle',{cx:X(L),cy:Y(v[L]),r:4,fill:C('acento'),stroke:C('superficie'),'stroke-width':2},s);
 tx(s,X(L)-6,Y(v[L])-10,'$'+v[L]+'K',{'text-anchor':'end',fill:C('tinta'),'font-weight':600});[0,4,8].forEach((i,k)=>tx(s,X(i),h-4,M[k],{'text-anchor':k==0?'start':(k==2?'end':'middle')}))}
mini('m1',[80,86,90,88,97,105,112,118,131]);mini('m2',[120,124,118,130,135,129,140,146,152]);mini('m3',[150,144,139,141,136,132,130,128,121]);
(function(){const [s,w,h]=svg('sc');const L=48,B=26,T=8,R=12;const P=[[4.2,920],[5.1,760],[6.0,640],[7.4,520],[8.1,610],[9.0,380],[10.5,300],[12.2,260],[6.8,880],[11.0,450],[5.6,540],[13.4,190]];
 const X=x=>L+(x-3)/(14-3)*(w-L-R),Y=y=>h-B-(y/1000)*(h-B-T);
 [0,250,500,750,1000].forEach(g=>{el('line',{x1:L,x2:w-R,y1:Y(g),y2:Y(g),stroke:C('linea')},s);tx(s,L-6,Y(g)+4,fmt(g),{'text-anchor':'end'})});
 [4,6,8,10,12,14].forEach(g=>tx(s,X(g),h-6,'$'+g,{'text-anchor':'middle'}));
 P.forEach((p,i)=>el('circle',{cx:X(p[0]),cy:Y(p[1]),r:5,fill:i==8?C('acento'):C('contexto_suave'),stroke:C('superficie'),'stroke-width':2},s));
 tx(s,X(6.8)+10,Y(880)+4,'Premium 500 g',{fill:C('tinta'),'font-weight':600});tx(s,w-R,h-B-6,'precio promedio →',{'text-anchor':'end'});tx(s,L+6,T+12,'↑ unidades',{})})();
(function(){const [s,w,h]=svg('dv');const Cs=['Snacks','Lácteos','Repostería','Orgánicos','Bebidas'],V=[12.4,6.1,3.2,-1.8,-6.5];const L=82,R=64,G=60,sc=(w-L-R-G)/18.9,mid=L+G+6.5*sc,band=h/Cs.length,bh=16;
 el('line',{x1:mid,x2:mid,y1:0,y2:h,stroke:C('contexto')},s);
 Cs.forEach((c,i)=>{const y=band*i+(band-bh)/2,v=V[i],x0=v>=0?mid:mid+v*sc,ww=Math.abs(v)*sc;tx(s,L-8,y+bh/2+4,c,{'text-anchor':'end',fill:C('tinta2')});
  el('rect',{x:x0,y,width:ww,height:bh,rx:3,fill:v>=0?C('bien'):C('mal')},s);tx(s,v>=0?mid+ww+6:x0-6,y+bh/2+4,(v>=0?'+':'−')+Math.abs(v).toFixed(1)+' pp',{'text-anchor':v>=0?'start':'end',fill:C('tinta'),'font-weight':600})})})();'''
    ficha=[('Tipo / público','Analítico · analistas comerciales, exploración de 15–30 minutos'),
       ('Premisa','El analista busca qué combinación explica el cambio, porque el total oculta la mezcla; por eso hay contribución por categoría (± con eje en cero) y cruces región × categoría, con filtros fijos a la izquierda.'),
       ('Pregunta de 5 s','¿Qué explica el crecimiento? → Snacks +12.4 pp'),
       ('Rejilla','12 col; sin tarjetas (suizo): columna de filtros 2 col + área de análisis 10 col en 2×2; separación por reglas'),
       ('Escala','KPI no aplica; títulos de visual 10 pt semibold; etiquetas 9 pt; acento índigo solo en la serie principal'),
       ('Supuestos','Small multiples nativos por validar en Report Server; alternativa: 3 lineChart con eje Y fijo 0–200.')]
    open(archivo,'w',encoding='utf-8').write(pagina('Analítico · referencia',direccion,cuerpo,script,ficha))
if __name__=='__main__': build()
