"""Medidas DAX que devuelven una imagen SVG (píldora de variación, bullet contra meta, anillo de avance, sparkline,
barra de progreso). Se ven en tableEx/pivotTable (columna de imagen) y en cardVisual como imagen (cardImage.imageUrl);
NO en la card clásica ni como valor de cardVisual (ahí sale el texto de la URL).
Son el recurso de los niveles «realzado» e «impactante»: dan gráficos finos que los visuales nativos no tienen, sin
visuales personalizados.

Cada generador devuelve dict(nombre, expr, categoria='ImageUrl', carpeta, descripcion, svg_ejemplo) listo para
scripts_modelo.tmdl_medidas (que escribe `dataCategory: ImageUrl`) y para previsualizar el SVG con valores de ejemplo.
El SVG del DAX y el de la vista previa salen de la MISMA plantilla (marcas «variable»), así que lo que se ve en la vista
previa es lo que dibuja Power BI.

Reglas (la medida se crea con dataCategory ImageUrl desde la pestaña TMDL y devuelve el SVG [probado: Desktop para RS 2026.05 y Desktop de la nube 2026.09,];
dónde se dibuja [probado]: tableEx y cardVisual con cardImage.imageUrl = medida, en RS 2026.05 y nube; la card clásica y el
valor (Data) de cardVisual muestran el texto de la URL, no la imagen. Genera el SVG con la MISMA dirección que el tema):
  * La medida devuelve "data:image/svg+xml;utf8," & svg, con '%' → %25 y '#' → %23 (si no, el color o el texto se cortan).
  * Comillas simples dentro del SVG (la cadena DAX usa dobles). Fuente 'Segoe UI'. Sin <style>, sin imágenes externas.
  * La categoría de datos ImageUrl NO se puede poner desde la vista de consultas DAX: va en el script TMDL (dataCategory).
  * Tamaño en tabla: Formato → Cuadrícula → Imágenes (alto/ancho) del visual = alto/ancho del SVG.
  * Por defecto sin cifras (cifras=False): la cifra va nativa al lado, con formatString, que es lo único que sigue la
    configuración regional del lector. Con cifras=True el texto usa la cultura del modelo (cultura="modelo", FORMAT sin
    cultura); cultura="usuario" usa USERCULTURE() (no coincide con los formatString en RS [probado]) y "en-US" (u otra) la fija. La GEOMETRÍA del SVG (coordenadas, anchos, dasharray) va SIEMPRE con "en-US": SVG exige punto decimal.
Colores desde references/tokens.json (dirección elegida)."""
import json, os, re, math

_TOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'references', 'tokens.json')

def mezcla(a, b, p):
    A, B = (tuple(int(x.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)) for x in (a, b))
    return '#' + ''.join(f'{round(p * u + (1 - p) * w):02X}' for u, w in zip(A, B))

def _direccion(direccion):
    """Tokens de una dirección fija o a la medida (PBIX_TOKENS_EXTRA → estilo_a_medida.cargar_tokens), como deneb._c."""
    try:
        import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from estilo_a_medida import cargar_tokens
        return cargar_tokens(_TOK)['direcciones'][direccion]
    except ImportError:
        return json.load(open(_TOK, encoding='utf-8'))['direcciones'][direccion]

def colores(direccion='moderno'):
    D = _direccion(direccion)
    clara = int(D['superficie'].lstrip('#')[:2], 16) > 128
    c = {k: D[k] for k in ('tinta', 'tinta2', 'tinta3', 'acento', 'acento_suave', 'contexto', 'contexto_suave', 'bien', 'mal', 'alerta', 'superficie')}
    for k in ('bien', 'mal', 'alerta'): c[k + '_suave'] = mezcla(D[k], D['superficie'], .10 if clara else .20)
    return c

# ---------------------------------------------------------------- plantilla → DAX / vista previa
def _dax(tpl):
    """'<svg ... fill=«fg»>' → "<svg ... fill=" & fg & ">" (las marcas «x» son variables DAX)."""
    out = []
    for i, p in enumerate(re.split(r'«(\w+)»', tpl)):
        if i % 2 == 0:
            if p: out.append('"' + p.replace('"', '""') + '"')
        else: out.append(p)
    return ' & '.join(out)

def _vista(tpl, vals): return re.sub(r'«(\w+)»', lambda m: str(vals[m.group(1)]), tpl)
def uri(svg): return 'data:image/svg+xml;utf8,' + svg.replace('%', '%25').replace('#', '%23')
_RET = 'RETURN IF(ISBLANK({v}), BLANK(), "data:image/svg+xml;utf8," & SUBSTITUTE(SUBSTITUTE(_svg, "%", "%25"), "#", "%23"))'
def _n(x, d=1): return f'{x:.{d}f}'
def _cult(cultura='modelo'):
    """'usuario' → USERCULTURE(); 'modelo' → sin tercer argumento (cultura del modelo); otra → literal fijo ('en-US', 'es-CO'…).
    [probado: RS 2026.05] USERCULTURE() NO coincide con los formatString: en el Desktop devolvió es-ES (idioma del
    programa) mientras los formatString salían en estilo inglés; en el portal los formatString siguen el navegador (español) y la
    píldora con USERCULTURE() salió en estilo inglés. Ver references/report_server.md."""
    if cultura in (None, 'usuario'): return 'USERCULTURE()'
    if cultura == 'modelo': return None
    return '"' + cultura + '"'
_F = "font-family='Segoe UI, Arial'"

def _medida(nombre, vars_dax, tpl, guarda, desc, ejemplo, carpeta='Visual SVG'):
    expr = '\n'.join(vars_dax + [f'VAR _svg = {_dax(tpl)}', _RET.format(v=guarda)])
    return dict(nombre=nombre, expr=expr, categoria='ImageUrl', carpeta=carpeta, descripcion=desc, svg_ejemplo=_vista(tpl, ejemplo))

# ---------------------------------------------------------------- generadores
def pildora(nombre, delta, unidad='%', polaridad=1, direccion='moderno', ancho=None, alto=20, sufijo='', cultura='modelo', cifras=False):
    """Píldora con flecha y variación. delta = expresión DAX de la variación (0.061 = 6.1 %).
    unidad: '%' (FORMAT 0.0 %), 'pp' (puntos porcentuales: delta 0.006 → 0.6 pp) o 'num' (0.0).
    polaridad: 1 si subir es bueno, -1 si bajar es bueno (gasto, días de inventario...).
    sufijo: contexto dentro de la píldora (p. ej. ' vs mes ant.'); agranda `ancho` (≈ 7 px por carácter a 12 px).
    cifras=False (por defecto): solo la forma (fondo de color + flecha); la cifra va NATIVA al lado (medida
    numérica con formatString: es lo único que sigue la configuración regional del lector en Desktop y portal [probado]).
    cifras=True: con el texto, en la cultura del modelo (cultura='modelo') salvo que se pida otra."""
    c = colores(direccion); h2 = alto / 2
    ancho = ancho or (76 if cifras else 28)
    cu = _cult(cultura)
    a = f', {cu}' if cu else ''
    txt = {'%': f'FORMAT(ABS(_d), "0.0 %"{a})', 'pp': f'FORMAT(ABS(_d) * 100, "0.0"{a}) & " pp"',
           'num': f'FORMAT(ABS(_d), "#,0.0"{a})'}[unidad]
    if sufijo: txt += ' & "' + sufijo.replace('"', '""') + '"'
    up, dn = f'M8 {h2 + 3} L12 {h2 - 3} L16 {h2 + 3} Z', f'M8 {h2 - 3} L12 {h2 + 3} L16 {h2 - 3} Z'
    v = [f'VAR _d = {delta}', f'VAR _bueno = _d * {polaridad} >= 0',
         f'VAR _fg = IF(_bueno, "{c["bien"]}", "{c["mal"]}")', f'VAR _bg = IF(_bueno, "{c["bien_suave"]}", "{c["mal_suave"]}")',
         f'VAR _tri = IF(_d >= 0, "{up}", "{dn}")', f'VAR _txt = {txt}']
    if not cifras:   # solo forma: flecha centrada
        v = v[:-1]; cx = ancho / 2 - 12
        up, dn = f'M{cx + 8} {h2 + 3} L{cx + 12} {h2 - 3} L{cx + 16} {h2 + 3} Z', f'M{cx + 8} {h2 - 3} L{cx + 12} {h2 + 3} L{cx + 16} {h2 - 3} Z'
        v[4] = f'VAR _tri = IF(_d >= 0, "{up}", "{dn}")'
        tpl = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{ancho}' height='{alto}' viewBox='0 0 {ancho} {alto}'>"
               f"<rect width='{ancho}' height='{alto}' rx='{h2}' fill='«_bg»'/><path d='«_tri»' fill='«_fg»'/></svg>")
        return _medida(nombre, v, tpl, '_d', f'Píldora de variación (solo forma); verde si mejora según polaridad {polaridad}.',
                       dict(_bg=c['bien_suave'], _fg=c['bien'], _tri=up))
    tpl = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{ancho}' height='{alto}' viewBox='0 0 {ancho} {alto}'>"
           f"<rect width='{ancho}' height='{alto}' rx='{h2}' fill='«_bg»'/><path d='«_tri»' fill='«_fg»'/>"
           f"<text x='{(ancho + 14) / 2}' y='{h2 + 4}' text-anchor='middle' {_F} font-size='12' font-weight='600' fill='«_fg»'>«_txt»</text></svg>")
    return _medida(nombre, v, tpl, '_d', f'Píldora de variación ({unidad}); verde si mejora según polaridad {polaridad}.',
                   dict(_bg=c['bien_suave'], _fg=c['bien'], _tri=up, _txt=('6.1 %' if unidad == '%' else '0.6 pp') + sufijo))

def bullet(nombre, valor, meta, maximo=1.2, direccion='moderno', ancho=120, alto=16):
    """Barra de avance contra meta con marca de la meta. Color acento si alcanza la meta, contexto si no."""
    c = colores(direccion); W = ancho - 4; t = W / maximo
    v = [f'VAR _r = DIVIDE({valor}, {meta})', f'VAR _w = FORMAT(MAX(MIN(_r, {maximo}), 0) / {maximo} * {W}, "0.0", "en-US")',
         f'VAR _c = IF(_r >= 1, "{c["acento"]}", "{c["contexto"]}")']
    y = alto / 2 - 3
    tpl = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{ancho}' height='{alto}' viewBox='0 0 {ancho} {alto}'>"
           f"<rect x='0' y='{y}' width='{W}' height='6' rx='3' fill='{c['acento_suave']}'/>"
           f"<rect x='0' y='{y}' width='«_w»' height='6' rx='3' fill='«_c»'/>"
           f"<rect x='{_n(t - 1)}' y='1' width='2' height='{alto - 2}' rx='1' fill='{c['tinta']}'/></svg>")
    return _medida(nombre, v, tpl, '_r', f'Bullet: avance contra meta (escala hasta {int(maximo * 100)} %), marca = meta.',
                   dict(_w=_n(1.04 / maximo * W), _c=c['acento']))

def anillo(nombre, avance, direccion='moderno', tam=64, grosor=7, fuente=13, cultura='modelo', cifras=False):
    """Anillo de avance (0–100 %). avance = expresión DAX (1.03 = 103 %). cifras=False (por defecto): sin el % al centro; el número
    va en la tarjeta nativa (formatString). cifras=True: % al centro en la cultura del modelo."""
    c = colores(direccion); r = tam / 2 - grosor / 2 - 1; L = 2 * math.pi * r; m = tam / 2
    v = [f'VAR _p = {avance}', f'VAR _dash = FORMAT(MAX(MIN(_p, 1), 0) * {_n(L, 2)}, "0.00", "en-US")',
         'VAR _txt = FORMAT(_p, "0 %"' + (f', {_cult(cultura)}' if _cult(cultura) else '') + ')']
    tpl = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{tam}' height='{tam}' viewBox='0 0 {tam} {tam}'>"
           f"<circle cx='{m}' cy='{m}' r='{_n(r)}' fill='none' stroke='{c['acento_suave']}' stroke-width='{grosor}'/>"
           f"<circle cx='{m}' cy='{m}' r='{_n(r)}' fill='none' stroke='{c['acento']}' stroke-width='{grosor}' stroke-linecap='round' "
           f"stroke-dasharray='«_dash» {_n(L, 2)}' transform='rotate(-90 {m} {m})'/>"
           + (f"<text x='{m}' y='{m + fuente / 3:.1f}' text-anchor='middle' {_F} font-size='{fuente}' font-weight='600' fill='{c['tinta']}'>«_txt»</text>" if cifras else '')
           + "</svg>")
    if not cifras: v = v[:-1]
    return _medida(nombre, v, tpl, '_p', 'Anillo de avance' + (' con porcentaje al centro.' if cifras else ' (sin cifra: va nativa al lado).'),
                   dict(_dash=_n(.78 * L, 2), **({'_txt': '78 %'} if cifras else {})))

def sparkline(nombre, medida, eje, tabla_eje, direccion='moderno', ancho=96, alto=24, color=None):
    """Línea de tendencia por fila (p. ej. por unidad de negocio) sobre los periodos visibles (ALLSELECTED del eje).
    eje: columna ordenable (AñoMes numérico, fecha de inicio de mes). Punto final marcado en acento."""
    c = colores(direccion); col = color or c['acento']; W, H = ancho - 8, alto - 6
    v = [f'VAR _T = FILTER(ADDCOLUMNS(CALCULATETABLE(VALUES({eje}), ALLSELECTED({tabla_eje})), "@v", {medida}), NOT ISBLANK([@v]))',
         'VAR _mn = MINX(_T, [@v])', 'VAR _mx = MAXX(_T, [@v])', 'VAR _n = COUNTROWS(_T)',
         f'VAR _T2 = ADDCOLUMNS(_T, "@i", RANKX(_T, {eje}, , ASC, DENSE))',
         f'VAR _pts = CONCATENATEX(_T2, FORMAT(2 + ([@i] - 1) * DIVIDE({W}, _n - 1), "0.0", "en-US") & "," & '
         f'FORMAT({alto - 3} - DIVIDE([@v] - _mn, _mx - _mn) * {H}, "0.0", "en-US"), " ", [@i], ASC)',
         'VAR _ult = MAXX(FILTER(_T2, [@i] = _n), [@v])',
         f'VAR _cy = FORMAT({alto - 3} - DIVIDE(_ult - _mn, _mx - _mn) * {H}, "0.0", "en-US")']
    tpl = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{ancho}' height='{alto}' viewBox='0 0 {ancho} {alto}'>"
           f"<polyline points='«_pts»' fill='none' stroke='{c['contexto']}' stroke-width='1.5' stroke-linejoin='round'/>"
           f"<circle cx='{2 + W}' cy='«_cy»' r='3' fill='{col}'/></svg>")
    return _medida(nombre, v, tpl, '_n', 'Sparkline de los periodos visibles; punto final en acento.',
                   dict(_pts='2,18 13,15 24,16 35,11 46,12 57,9 68,10 79,6 90,3', _cy='3'))

def progreso(nombre, avance, direccion='moderno', ancho=120, alto=8):
    """Barra de progreso simple (0–100 %)."""
    c = colores(direccion)
    v = [f'VAR _p = {avance}', f'VAR _w = FORMAT(MAX(MIN(_p, 1), 0) * {ancho}, "0.0", "en-US")']
    tpl = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{ancho}' height='{alto}' viewBox='0 0 {ancho} {alto}'>"
           f"<rect width='{ancho}' height='{alto}' rx='{alto / 2}' fill='{c['acento_suave']}'/>"
           f"<rect width='«_w»' height='{alto}' rx='{alto / 2}' fill='{c['acento']}'/></svg>")
    return _medida(nombre, v, tpl, '_p', 'Barra de progreso 0–100 %.', dict(_w=_n(.64 * ancho)))

def vista_previa_html(medidas, ruta, fondo='#FFFFFF'):
    """HTML con cada SVG de ejemplo como <img src=data URI> (misma codificación que la medida) para revisarlos."""
    filas = ''.join(f"<tr><td>{m['nombre']}</td><td><img src=\"{uri(m['svg_ejemplo'])}\"></td></tr>" for m in medidas)
    open(ruta, 'w', encoding='utf-8').write(f"<!doctype html><meta charset='utf-8'><body style='background:{fondo};font:13px Segoe UI,Arial;"
                                            f"padding:16px'><table cellpadding='8'>{filas}</table></body>")

if __name__ == '__main__':
    from comun import ayuda; ayuda(__doc__, 0)
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from scripts_modelo import tmdl_medidas
    d = sys.argv[1] if len(sys.argv) > 1 else 'moderno'
    ms = [pildora('SVG Δ ventas', '[Δ % ventas]', direccion=d), pildora('SVG Δ margen', '[Δ margen]', 'pp', direccion=d),
          pildora('SVG Δ gasto', '[Δ % gasto]', polaridad=-1, direccion=d), bullet('SVG avance meta', '[Ventas]', '[Meta]', direccion=d),
          anillo('SVG anillo plan', 'DIVIDE([Ventas], [Plan])', direccion=d),
          sparkline('SVG tendencia', '[Ventas]', "'Fecha'[AñoMes]", "'Fecha'", direccion=d), progreso('SVG progreso', '[Avance]', direccion=d)]
    print(tmdl_medidas('Medidas', ms))
