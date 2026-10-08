"""Nivel impactante · dirección aurora (oscura, 2 capas). Comité de dirección en sala o pantalla."""
from base import pagina, pie, fondo
def build(direccion='aurora', archivo='comite_aurora.html'):
    tiles = [('Margen bruto', '36.4 %', 'dn', '▼ 0.6 pp vs plan', 0.984, 'Meta 37.0 % · real 36.4 %', '[37.1,36.9,37.0,36.6,36.8,36.5,36.7,36.3,36.4]', 'mal'),
             ('Cobertura de inventario', '41 días', 'up', 'En rango (35–45)', 0.911, 'Tope 45 días · hace un mes 47', '[52,50,49,48,47,47,46,47,41]', 'acento'),
             ('Nivel de servicio', '96.2 %', 'up', '▲ 1.1 pp vs plan', 1.013, 'Meta 95.0 % · real 96.2 %', '[94.1,94.6,95.0,94.8,95.3,95.6,95.9,95.7,96.2]', 'acento')]
    xs, ws = [440, 717, 995], [261, 262, 261]
    k, js = '', ''
    for i, (l, v, c, d, m, mt, serie, col) in enumerate(tiles):
        k += f'''<div class="card" style="left:{xs[i]}px;top:112px;width:{ws[i]}px;height:220px" data-pbi="cardVisual (valor + referencia Δ con color por regla) + medida SVG bullet vs meta (ImageUrl) · sparkline nativo">
 <div class="b lab" style="left:20px;top:20px">{l}</div><div class="b kpi" style="left:20px;top:40px">{v}</div>
 <div class="b" style="left:20px;top:84px;font-size:12px"><span class="pill {c}">{d}</span></div>
 <div class="b" id="m{i}" style="left:20px;top:122px;width:{ws[i]-40}px;height:20px"></div>
 <div class="b ctx" style="left:20px;top:148px">{mt}</div>
 <div class="b" id="k{i}" style="left:20px;top:176px;width:{ws[i]-40}px;height:28px"></div></div>'''
        js += f"meta('m{i}',{m});spark('k{i}',{serie},C('{col}'));"
    regiones = [('Norte', '$11.2M', 'up', '▲ 6.1 %', 1.061), ('Centro', '$10.4M', 'up', '▲ 4.0 %', 1.040), ('Occidente', '$8.9M', 'up', '▲ 2.3 %', 1.023),
                ('Costa', '$6.3M', 'up', '▲ 0.5 %', 1.005), ('Sur', '$7.1M', 'dn', '▼ 1.8 %', .982), ('Altiplano', '$4.7M', 'dn', '▼ 4.9 %', .951)]
    filas = ''.join(f'<tr><td>{r}</td><td class="n">{v}</td><td class="n"><span class="pill {c}" style="font-size:12px">{d}</span></td>'
                    f'<td><div id="r{i}" style="width:108px;height:16px"></div></td></tr>' for i, (r, v, c, d, _) in enumerate(regiones))
    js += ''.join(f"meta('r{i}',{x});" for i, (*_, x) in enumerate(regiones))
    cuerpo = fondo(direccion, luces=[(330, 250, 560, 0, .8), (760, 60, 460, 1, .55), (1150, 650, 640, 2, .9), (420, 720, 420, 1, .45)],
                   trazos=[(24, 99, 620)]) + f'''
<div class="b kick" style="left:24px;top:22px;color:var(--acento)" data-pbi="textbox">Comité de dirección · octubre 2026</div>
<div class="b tit" style="left:24px;top:40px" data-pbi="card de texto (título-conclusión dinámico, DAX)">Las ventas superan el plan 3.2 % y la cobertura de inventario vuelve al rango</div>
<div class="b sub" style="left:24px;top:70px" data-pbi="card de texto (medida Periodo)">Acumulado enero–septiembre 2026 · USD · contra plan y contra 2025</div>
<div class="sl" style="left:864px;top:30px;width:184px" data-pbi="slicer Dropdown (sin fondo ni borde: la píldora está en la imagen)"><span><span class="k">Periodo</span>ene–sep 2026</span></div>
<div class="sl" style="left:1072px;top:30px;width:184px" data-pbi="slicer Dropdown (sin fondo ni borde)"><span><span class="k">Región</span>Todas</span></div>
<div class="card" style="left:24px;top:112px;width:400px;height:220px" data-pbi="cardVisual héroe (valor + 2 referencias) + medida SVG anillo (ImageUrl) + sparkline nativo">
 <div class="b lab" style="left:20px;top:20px">Ventas netas acumuladas</div>
 <div class="b impacto" style="left:20px;top:38px">$48.6M</div>
 <div class="b" style="left:20px;top:110px;font-size:12px"><span class="pill up">▲ 3.2 % vs plan</span></div>
 <div class="b ctx" style="left:20px;top:140px">▲ 9.7 % vs ene–sep 2025 ($44.3M)</div>
 <div class="b" id="an" style="left:270px;top:24px;width:110px;height:110px"></div>
 <div class="b ctx" style="left:270px;top:140px;width:110px;text-align:center">del plan acumulado</div>
 <div class="b" id="sh" style="left:20px;top:172px;width:360px;height:32px"></div></div>
{k}
<div class="card" style="left:24px;top:348px;width:800px;height:332px" data-pbi="Deneb: área con degradado (2026) + línea punteada (plan) + línea gris (2025); etiquetas al final · alternativa nativa: areaChart con transparencia">
 <div class="b" style="left:20px;top:16px"><div class="vt">Ventas netas por mes</div><div class="vs">Millones de USD · 2026 contra plan y contra 2025</div></div>
 <div class="b leg" style="right:20px;top:20px"><span><i style="background:var(--acento)"></i>2026</span><span><i style="background:var(--acento2)"></i>Plan</span><span><i style="background:var(--contexto)"></i>2025</span></div>
 <div class="b" id="ln" style="left:12px;top:64px;width:776px;height:256px"></div></div>
<div class="card" style="left:840px;top:348px;width:416px;height:332px" data-pbi="tableEx: medida SVG píldora Δ + medida SVG bullet vs plan (ImageUrl); sin bandas ni bordes verticales">
 <div class="b" style="left:20px;top:16px"><div class="vt">Cumplimiento por región</div><div class="vs">Ventas acumuladas · Δ y avance contra plan</div></div>
 <div class="b" style="left:20px;top:64px;width:376px"><table><tr><th>Región</th><th class="n">Ventas</th><th class="n">vs plan</th><th>Avance</th></tr>{filas}
 <tr class="tot"><td>Total</td><td class="n">$48.6M</td><td class="n"><span class="pill up" style="font-size:12px">▲ 3.2 %</span></td><td></td></tr></table></div></div>
{pie('ERP Ventas y Plan comercial', '06/10/2026 07:30')}'''
    script = f'''const M=['ene','feb','mar','abr','may','jun','jul','ago','sep'];const fM=v=>'$'+v.toFixed(1)+'M';
linea('ln',M,[{{n:'2025',v:[4.4,4.6,4.8,4.7,5.0,5.0,5.3,5.2,5.3],c:C('contexto'),lc:C('tinta3')}},{{n:'Plan',v:[4.7,4.9,5.1,5.1,5.4,5.4,5.6,5.5,5.4],c:C('acento2'),dash:'5 4',lc:C('tinta2')}},{{n:'2026',v:[4.8,5.0,5.3,5.2,5.6,5.5,5.8,5.6,5.8],c:C('acento'),area:.42}}],{{f:fM}});
anillo('an',1.032,{{t:'103 %',g:9,fs:16}});spark('sh',[4.8,5.0,5.3,5.2,5.6,5.5,5.8,5.6,5.8]);{js}'''
    ficha = [('Nivel / capas', 'Impactante · 2 capas: decoración (luces, paneles vidrio, línea de luz) como imagen de fondo; datos con visuales nativos transparentes, 1 Deneb y medidas SVG'),
             ('Tipo / público', 'Ejecutivo de comité · dirección general en sala con pantalla; lectura de 2–3 minutos guiada por quien presenta'),
             ('Premisa', 'El comité quiere saber si vamos arriba del plan y qué región compensa a cuál; el héroe es Ventas vs plan con anillo de avance, y la tabla de regiones muestra quién está abajo.'),
             ('Pregunta de 5 s', '¿Vamos arriba del plan? → Sí, 103 % del plan acumulado; Sur y Altiplano abajo'),
             ('Efectos', 'Luces de color detrás del héroe y del cierre (guían la mirada en diagonal), paneles vidrio, línea de luz bajo el título; área con degradado (Deneb); anillo y bullets (SVG)'),
             ('Rejilla', '12 col (margen 24, medianil 16, col 88); filas 112/348; héroe 4 col, 3 tiles en 8 col; gráfico 8 col + tabla 4 col'),
             ('Escala', 'kicker 9 · título 15 · nota 9 · título visual 10 · KPI 21 · impacto 36 pt (solo el héroe)'),
             ('Supuestos', 'Polaridad: ventas y servicio ↑ bueno; margen ↓ malo; cobertura buena dentro de 35–45 días.')]
    open(archivo, 'w', encoding='utf-8').write(pagina('Comité · aurora', direccion, cuerpo, script, ficha))
if __name__ == '__main__': build()
