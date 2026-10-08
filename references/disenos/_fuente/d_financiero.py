from base import pagina, pie
def build(direccion='editorial', archivo='financiero.html'):
    K=[('Utilidad neta','$214K','up','▲ 1.9 %','vs presupuesto ($210K)',True),('Ingresos','$2.41M','up','▲ 3.2 %','vs presupuesto',False),
       ('Margen bruto','35.8 %','dn','▼ 1.8 pp','vs presupuesto',False),('EBITDA','$398K','up','▲ 4.5 %','16.5 % de ingresos',False)]
    kp=''; x=24
    for i,(l,v,c,d,ctx,h) in enumerate(K):
        w=344 if h else 264
        if i: kp+=f'<div class="vr" style="left:{x-16}px;top:112px;height:88px"></div>'
        kp+=f'''<div class="b" style="left:{x}px;top:112px;width:{w-24}px" data-pbi="card (valor) + card de texto (Δ vs ppto, color por favorabilidad)">
<div class="lab">{l}</div><div class="{'heroe' if h else 'kpi'}" style="margin-top:4px">{v}</div><div style="margin-top:4px;font-size:12px"><span class="{c}">{d}</span> <span class="ctx">{ctx}</span></div></div>'''
        x+=w+32
    F=[('Ingresos',2410,2335,2268,''),('Costo de ventas',-1548,-1457,-1450,''),('Utilidad bruta',862,878,818,'sub'),('Gastos de venta',-281,-296,-270,''),
       ('Gastos administrativos',-183,-201,-188,''),('EBITDA',398,381,360,'sub'),('Depreciación',-62,-60,-58,''),('Gastos financieros',-41,-38,-44,''),
       ('Impuestos',-81,-73,-70,''),('Utilidad neta',214,210,188,'tot')]
    m=lambda v:('−' if v<0 else '')+f'{abs(v):,}'
    rows=''
    for n,r,p,a,e in F:
        var=r-p; fav=var>=0; cls='up' if fav else 'dn'
        rows+=f'<tr class="{e}"><td>{n}</td><td class="n">{m(r)}</td><td class="n" style="color:var(--tinta2)">{m(p)}</td><td class="n"><span class="{cls}">{"▲" if fav else "▼"} {m(abs(var)) if fav else m(-abs(var))}</span></td><td class="n" style="color:var(--tinta2)">{m(a)}</td><td class="n" style="color:var(--tinta2)">{abs(r)/2410*100:.1f} %</td></tr>'
    cuerpo=f'''
<div class="b kick" style="left:24px;top:24px" data-pbi="textbox">Finanzas · cierre mensual</div>
<div class="b tit" style="left:24px;top:40px" data-pbi="textbox (fuente Georgia solo en el título)">Estado de resultados — septiembre 2026</div>
<div class="b sub" style="left:24px;top:76px" data-pbi="card de texto (medida Periodo)">Real contra presupuesto y contra septiembre 2025 · miles de USD · ▲▼ = favorable / desfavorable al resultado</div>
<div class="sl" style="left:776px;top:32px;width:144px" data-pbi="slicer Dropdown"><span><span class="k">Mes</span>sep 2026</span></div>
<div class="sl" style="left:928px;top:32px;width:184px" data-pbi="slicer Dropdown"><span><span class="k">Compañía</span>Consolidado</span></div>
<div class="sl" style="left:1120px;top:32px;width:136px" data-pbi="slicer Dropdown"><span><span class="k">Moneda</span>USD</span></div>
<div class="hr" style="left:24px;top:100px;width:1232px"></div>
{kp}
<div class="hr" style="left:24px;top:216px;width:1232px"></div>
<div class="b" style="left:24px;top:232px;width:728px" data-pbi="pivotTable: filas = cuentas; subtotales en semibold con regla superior; Var con ícono y color por regla de favorabilidad">
 <div class="vt">Estado de resultados</div><div class="vs">Miles de USD · gastos en negativo</div>
 <table style="margin-top:12px"><tr><th>Cuenta</th><th class="n">Real</th><th class="n">Presupuesto</th><th class="n">Var vs ppto</th><th class="n">sep 2025</th><th class="n">% ingresos</th></tr>{rows}</table></div>
<div class="vr" style="left:776px;top:232px;height:440px"></div>
<div class="b" style="left:800px;top:232px;width:456px;height:440px" data-pbi="waterfallChart (aumento = bien, disminución = mal, total = tinta 2)">
 <div class="vt">Del presupuesto al real</div><div class="vs">Utilidad neta · qué rubros explican la diferencia</div>
 <div class="b" id="wf" style="left:0;top:56px;width:456px;height:300px"></div>
 <div class="b" style="left:0;top:372px;width:440px;font-size:12px;color:var(--tinta2)" data-pbi="card de texto (lectura dinámica, DAX)">Más ventas compensaron un costo de ventas por encima de lo previsto; el gasto controlado sostuvo la utilidad.</div></div>
{pie('ERP Contabilidad (mayor general)','05/10/2026 22:10 · cierre preliminar')}'''
    script="cascada('wf',[{l:'Ppto.',v:210,t:1},{l:'Ingresos',v:75},{l:'Costo\\nventas',v:-91},{l:'Gastos\\nventa',v:15},{l:'Gastos\\nadmin.',v:18},{l:'Financ. e\\nimpuestos',v:-13},{l:'Real',v:214,t:1}],{f:v=>'$'+fmt(v)+'K'});"
    ficha=[('Tipo / público','Financiero · gerencia y comité, lectura de filas y variaciones'),
       ('Premisa','La gerencia revisa desvíos contra presupuesto, porque cada línea tiene un responsable; por eso la matriz de cuentas es el bloque principal y la cascada explica el total.'),
       ('Pregunta de 5 s','¿Cumplimos la utilidad del mes? → Utilidad neta $214K, ▲ 1.9 % vs presupuesto'),
       ('Rejilla','12 col; sin tarjetas: secciones separadas por reglas de 1 px; matriz 8 col + cascada 4 col'),
       ('Escala','título Georgia 18 pt (solo título); resto Segoe UI: nota 9 · visual 10 · KPI 21 · héroe 27 pt; cifras siempre Segoe UI'),
       ('Supuestos','Favorabilidad por tipo de cuenta (ingreso ↑ bueno, gasto ↓ bueno). Aviso "cierre preliminar" condicional por DAX.')]
    open(archivo,'w',encoding='utf-8').write(pagina('Financiero · referencia',direccion,cuerpo,script,ficha))
if __name__=='__main__': build()
