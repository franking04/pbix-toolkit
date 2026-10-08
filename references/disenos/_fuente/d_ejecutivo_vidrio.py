"""Nivel impactante · dirección vidrio (clara, 2 capas). Dirección general en laptop: cierre mensual."""
from base import pagina, pie, fondo
def build(direccion='vidrio', archivo='ejecutivo_vidrio.html'):
    mini = [('Ventas netas', '$18.9M', 'up', '▲ 4.2 %', 'vs agosto'),
            ('Margen bruto', '33.0 %', 'up', '▲ 1.4 pp', 'vs agosto'),
            ('Gasto operativo', '$3.98M', 'up', '▼ 2.7 %', 'vs agosto · bajar es bueno')]
    m = ''.join(f'''<div class="b" style="left:20px;top:{276 + i * 92}px;width:256px">
 <div class="lab">{l}</div><div class="kpi" style="margin-top:2px">{v}</div>
 <div style="margin-top:4px;font-size:12px"><span class="pill {c}">{d}</span> <span class="ctx">{x}</span></div></div>''' for i, (l, v, c, d, x) in enumerate(mini))
    m += ''.join(f'<div class="hr" style="left:20px;top:{266 + i * 92}px;width:256px"></div>' for i in range(3))
    unidades = [('Consumo', '$2.61M', 'up', '▲ 9.8 %', '[2.2,2.3,2.3,2.4,2.5,2.4,2.5,2.38,2.61]'),
                ('Institucional', '$1.84M', 'up', '▲ 15.1 %', '[1.5,1.6,1.5,1.7,1.7,1.6,1.7,1.6,1.84]'),
                ('Exportación', '$1.22M', 'up', '▲ 18.4 %', '[0.9,0.9,1.0,1.0,1.1,1.0,1.1,1.03,1.22]'),
                ('Digital', '$0.57M', 'up', '▲ 6.2 %', '[0.42,0.45,0.47,0.5,0.5,0.52,0.55,0.54,0.57]')]
    filas = ''.join(f'<tr><td>{u}</td><td class="n">{v}</td><td class="n"><span class="pill {c}" style="font-size:12px">{d}</span></td>'
                    f'<td><div id="u{i}" style="width:96px;height:22px"></div></td></tr>' for i, (u, v, c, d, _) in enumerate(unidades))
    js = ''.join(f"spark('u{i}',{s});" for i, (*_, s) in enumerate(unidades))
    cuerpo = fondo(direccion, luces=[(150, 140, 600, 0, 1), (1180, 120, 560, 1, .9), (760, 760, 700, 2, .85), (300, 640, 380, 1, .5)]) + f'''
<div class="b kick" style="left:24px;top:22px;color:var(--acento)" data-pbi="textbox">Dirección general · cierre de septiembre 2026</div>
<div class="b tit" style="left:24px;top:40px" data-pbi="card de texto (título-conclusión dinámico, DAX)">El margen se recupera 1.4 pp gracias a menores costos logísticos</div>
<div class="b sub" style="left:24px;top:70px" data-pbi="card de texto (medida Periodo)">Septiembre 2026 · USD · contra agosto y contra septiembre de 2025</div>
<div class="sl" style="left:920px;top:30px;width:160px" data-pbi="slicer Dropdown (sin fondo ni borde: la píldora está en la imagen)"><span><span class="k">Mes</span>sep 2026</span></div>
<div class="sl" style="left:1096px;top:30px;width:160px" data-pbi="slicer Dropdown (sin fondo ni borde)"><span><span class="k">Unidad</span>Todas</span></div>
<div class="card" style="left:24px;top:112px;width:296px;height:568px" data-pbi="cardVisual héroe + Deneb área con degradado (12 meses) + cardVisual de 3 filas (Δ con color por regla)">
 <div class="b lab" style="left:20px;top:20px">Utilidad operativa · septiembre</div>
 <div class="b impacto" style="left:20px;top:38px">$6.24M</div>
 <div class="b" style="left:20px;top:110px;font-size:12px"><span class="pill up">▲ 12.6 % vs ago</span></div>
 <div class="b ctx" style="left:20px;top:138px">▲ 8.1 % vs sep 2025 ($5.77M)</div>
 <div class="b" id="ha" style="left:16px;top:168px;width:264px;height:72px"></div><div class="b ctx" style="left:20px;top:242px">Últimos 12 meses</div>
 {m}</div>
<div class="card" style="left:336px;top:112px;width:920px;height:280px" data-pbi="Deneb: área con degradado (2026) + línea gris (2025), etiqueta al final · alternativa nativa: lineChart">
 <div class="b" style="left:20px;top:16px"><div class="vt">Utilidad operativa por mes</div><div class="vs">Millones de USD · 2026 contra 2025</div></div>
 <div class="b leg" style="right:20px;top:20px"><span><i style="background:var(--acento)"></i>2026</span><span><i style="background:var(--contexto)"></i>2025</span></div>
 <div class="b" id="ln" style="left:12px;top:60px;width:896px;height:208px"></div></div>
<div class="card" style="left:336px;top:408px;width:452px;height:272px" data-pbi="barChart nativo divergente (color por regla: verde suma, rojo resta), ordenado por impacto">
 <div class="b" style="left:20px;top:16px"><div class="vt">Qué movió la utilidad: de $5.54M a $6.24M</div><div class="vs">Contribución de cada factor de agosto a septiembre · millones de USD</div></div>
 <div class="b" id="cs" style="left:12px;top:68px;width:420px;height:180px"></div></div>
<div class="card" style="left:804px;top:408px;width:452px;height:272px" data-pbi="tableEx: medida SVG píldora Δ + medida SVG sparkline (ImageUrl)">
 <div class="b" style="left:20px;top:16px"><div class="vt">Unidades de negocio</div><div class="vs">Utilidad operativa de septiembre · Δ vs agosto · 9 meses</div></div>
 <div class="b" style="left:20px;top:62px;width:412px"><table><tr><th>Unidad</th><th class="n">Utilidad</th><th class="n">vs ago</th><th>Tendencia</th></tr>{filas}
 <tr class="tot"><td>Total</td><td class="n">$6.24M</td><td class="n"><span class="pill up" style="font-size:12px">▲ 12.6 %</span></td><td></td></tr></table></div></div>
{pie('ERP Finanzas (estado de resultados)', '06/10/2026 07:30')}'''
    script = f'''const M=['ene','feb','mar','abr','may','jun','jul','ago','sep'];const fM=v=>'$'+v.toFixed(2)+'M';
linea('ln',M,[{{n:'2025',v:[4.8,4.9,5.0,5.1,5.3,5.2,5.6,5.6,5.77],c:C('contexto'),lc:C('tinta3')}},{{n:'2026',v:[4.9,5.1,5.0,5.4,5.6,5.3,5.7,5.54,6.24],c:C('acento'),area:.32}}],{{f:fM,R:110}});
areaSpark('ha',[4.6,4.7,4.9,4.9,5.1,5.0,5.4,5.6,5.3,5.7,5.54,6.24]);
divergente('cs',['Logística','Precio','Volumen','Otros','Materia prima'],[.36,.21,.17,.08,-.12],{{f:v=>'$'+v.toFixed(2)+'M'}});{js}'''
    ficha = [('Nivel / capas', 'Impactante · 2 capas: fondo claro con luces pastel y paneles vidrio en la imagen; visuales nativos transparentes, 2 Deneb (áreas) y medidas SVG'),
             ('Tipo / público', 'Ejecutivo · director general y su equipo en laptop; revisión mensual de 3–5 minutos'),
             ('Premisa', 'La dirección pregunta si la mejora de utilidad es sostenible; el héroe muestra la utilidad y las barras de contribución muestran que el salto viene sobre todo de logística, no solo de precio.'),
             ('Pregunta de 5 s', '¿Mejoró la utilidad y por qué? → +12.6 % vs agosto, sobre todo por logística'),
             ('Efectos', 'Luces pastel desenfocadas detrás de los paneles (profundidad), paneles vidrio con borde blanco, áreas con degradado; píldoras y sparklines SVG en la tabla'),
             ('Rejilla', '12 col; héroe vertical 3 col × 2 filas; derecha 9 col: tendencia arriba, contribución y tabla abajo'),
             ('Escala', 'kicker 9 · título 15 · nota 9 · título visual 10 · KPI 21 · impacto 36 pt (solo el héroe)'),
             ('Supuestos', 'Gasto operativo: bajar es bueno (verde con flecha hacia abajo). Sin meta mensual de utilidad.')]
    open(archivo, 'w', encoding='utf-8').write(pagina('Ejecutivo · vidrio', direccion, cuerpo, script, ficha))
if __name__ == '__main__': build()
