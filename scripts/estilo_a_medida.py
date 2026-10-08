"""Estilo a la medida: genera una dirección visual NUEVA (tokens con las mismas claves que references/tokens.json) a partir de
1–3 colores semilla (inspiración, marca, foto, referencia externa), un modo (claro/oscuro) y un carácter. Sirve para que cada
reporte tenga su propio estilo en vez de repetir moderno/aurora/vidrio; las direcciones fijas quedan como punto de partida.

Qué garantiza (calculado, no a ojo):
  · neutros teñidos con el matiz del carácter; tinta, tinta2 y tinta3 ≥ 4.5:1 sobre página y superficie; contexto ≥ 3:1;
  · acento con el matiz de la semilla y ≥ 4.5:1 (se usa en textos de énfasis); si se tuvo que oscurecer/aclarar, el color original
    queda en `marca` (solo decoración: capa de fondo, barra de acento, reglas);
  · estados bien/alerta/mal ≥ 4.5:1; aviso si el acento cae en el matiz de un estado (verde/ámbar/rojo);
  · secuencial de 6 pasos de un solo matiz, luminosidad monótona (ΔL ≥ 0.06);
  · 8 categóricos validados con los mismos umbrales que el validador de la skill `dataviz`: L en banda, croma ≥ 0.10,
    ΔE OKLab×100 adyacentes ≥ 8 con protan/deutan (Machado 2009), ≥ 15 con visión normal, contraste ≥ 3:1 sobre la superficie.
  · en 2 capas: fondo_base, luces, panel y control para la imagen de fondo (el contraste final lo mide revisar_html.js sobre la imagen).

Uso:
  python estilo_a_medida.py --nombre cobre --modo claro --semillas "#B4642D,#2E5E4E" --caracter calido \
         --inspiracion "afiche de café de especialidad; papel cálido, cobre" --salida estilos/cobre.json [--capas 2] [--muestra]
  Después: PBIX_TOKENS_EXTRA=estilos/cobre.json  (varias rutas separadas por ';' en Windows, ':' en Linux) y la dirección
  «cobre» queda disponible para tema_powerbi.py, los diseños HTML (disenos/_fuente/base.py), componentes.LienzoV2 y deneb.py.
  python estilo_a_medida.py --caracteres   → lista de caracteres con lo que cambia cada uno.
"""
import argparse, json, math, os, sys, datetime

_AQUI = os.path.dirname(os.path.abspath(__file__))
_TOK = os.path.join(_AQUI, '..', 'references', 'tokens.json')


# ----------------------------------------------------------------------------- carga de tokens (base + extra)
def cargar_tokens(ruta_base=None, extra=None):
    """tokens.json de la skill + direcciones a la medida. extra = lista de rutas o None (usa la variable PBIX_TOKENS_EXTRA,
    varias rutas separadas por os.pathsep). Una dirección extra con el mismo nombre que una fija la reemplaza (se avisa)."""
    tk = json.load(open(ruta_base or _TOK, encoding='utf-8'))
    if extra is None:
        extra = [p for p in os.environ.get('PBIX_TOKENS_EXTRA', '').split(os.pathsep) if p.strip()]
    for p in extra:
        x = json.load(open(p, encoding='utf-8'))
        for n, d in x.get('direcciones', {}).items():
            if n in tk['direcciones']:
                print(f'aviso: la dirección «{n}» de {p} reemplaza a la fija', file=sys.stderr)
            tk['direcciones'][n] = d
    return tk


# ----------------------------------------------------------------------------- color (sRGB ↔ OKLab/OKLCH, WCAG, CVD)
def _hex(h):
    h = h.strip().lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

def _a_lin(v): return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
def _de_lin(v): return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
def lin(h): return tuple(_a_lin(v) for v in _hex(h))

def luminancia(h):
    r, g, b = lin(h); return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contraste(a, b):
    x, y = sorted((luminancia(a), luminancia(b)), reverse=True); return (x + 0.05) / (y + 0.05)

def _lin_a_oklab(r, g, b):
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)

def _oklab_a_lin(L, a, b):
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)

def oklch(h):
    L, a, b = _lin_a_oklab(*lin(h)); return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360

def _en_gamut(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    return all(-1e-6 <= v <= 1 + 1e-6 for v in _oklab_a_lin(L, a, b))

def desde_oklch(L, C, H):
    """Hex más cercano: conserva L y matiz, reduce croma hasta entrar en sRGB."""
    L = min(max(L, 0), 1); lo, hi = 0.0, max(C, 0)
    if not _en_gamut(L, hi, H):
        for _ in range(30):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if _en_gamut(L, mid, H) else (lo, mid)
        C = lo
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    return '#' + ''.join(f'{round(min(max(_de_lin(v), 0), 1) * 255):02X}' for v in _oklab_a_lin(L, a, b))

def croma_max(L, H, tope=0.4):
    lo, hi = 0.0, tope
    for _ in range(25):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _en_gamut(L, mid, H) else (lo, mid)
    return lo

_MACHADO = {'protan': [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
            'deutan': [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
            'tritan': [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]}

def _sim(h, k):
    r, g, b = lin(h); M = _MACHADO[k]
    return tuple(max(0.0, min(1.0, M[i][0] * r + M[i][1] * g + M[i][2] * b)) for i in range(3))

def delta_e(h1, h2, k=None):
    """Distancia OKLab ×100; k = protan/deutan/tritan simula daltonismo (Machado, Oliveira y Fernandes 2009, severidad 1)."""
    a = _lin_a_oklab(*(_sim(h1, k) if k else lin(h1))); b = _lin_a_oklab(*(_sim(h2, k) if k else lin(h2)))
    return 100 * math.dist(a, b)

def _cvd(h1, h2): return min(delta_e(h1, h2, 'protan'), delta_e(h1, h2, 'deutan'))

def _dist_matiz(a, b): d = abs(a - b) % 360; return min(d, 360 - d)


# ----------------------------------------------------------------------------- umbrales (mismos que el validador dataviz)
BANDA = {'claro': (0.43, 0.77), 'oscuro': (0.48, 0.67)}
CROMA_MIN, CVD_META, CVD_PISO, NORMAL_PISO, CONTRASTE_MARCA, CONTRASTE_TEXTO = 0.10, 8.0, 6.0, 15.0, 3.0, 4.5
ESTADOS = {'bien': 150, 'alerta': 70, 'mal': 27}        # matiz OKLCH aproximado de verde, ámbar y rojo
# Margen sobre 4.5: los estados van como texto sobre píldoras teñidas (mezcla 10–20 % con la superficie) y, en 2 capas, todo el
# texto va sobre la imagen de fondo con luces y paneles translúcidos. Calibrado con revisar_html.js: con 4.5 justo,
# las píldoras dieron 4.43 y el texto sobre paneles de 2 capas 4.0–4.2.
MARGEN = {1: dict(texto=4.5, enfasis=4.8, estado=5.2), 2: dict(texto=5.6, enfasis=6.0, estado=5.9)}


# ----------------------------------------------------------------------------- caracteres
# tinte_h None = matiz del acento. tinte_c = croma de los neutros. cat_c = (mín, máx) de croma de categóricos.
CARACTERES = {
    'neutro':        dict(tinte_h=None, tinte_c=0.008, tarjetas=True,  radio=8,  radio_panel=14, fuente_titulo='Segoe UI Semibold',
                          fuente_kpi='Segoe UI Semibold', acento_c=0.32, cat_c=(0.11, 0.17), luz=0.45, giro2=150,
                          rasgo='equilibrado; tarjetas finas; nada llama la atención salvo el dato'),
    'calido':        dict(tinte_h=70, tinte_c=0.012, tarjetas=False, radio=4,  radio_panel=10, fuente_titulo='Georgia',
                          fuente_kpi='Segoe UI Semibold', acento_c=0.16, cat_c=(0.11, 0.15), luz=0.40, giro2=60,
                          rasgo='papel cálido, reglas en vez de cajas, título con serifa; cercano, editorial'),
    'frio':          dict(tinte_h=245, tinte_c=0.014, tarjetas=True,  radio=8,  radio_panel=14, fuente_titulo='Segoe UI Semibold',
                          fuente_kpi='Segoe UI Semibold', acento_c=0.32, cat_c=(0.11, 0.16), luz=0.45, giro2=-60,
                          rasgo='grises azulados, limpio, corporativo sin ser marino'),
    'tecnico':       dict(tinte_h=None, tinte_c=0.004, tarjetas=False, radio=2,  radio_panel=4,  fuente_titulo='Segoe UI Semibold',
                          fuente_kpi='Segoe UI Light', acento_c=0.32, cat_c=(0.11, 0.15), luz=0.30, giro2=180,
                          rasgo='casi sin tinte, esquinas rectas, cifras en Light, alineación estricta; preciso'),
    'energico':      dict(tinte_h=None, tinte_c=0.012, tarjetas=True,  radio=12, radio_panel=18, fuente_titulo='Segoe UI Bold',
                          fuente_kpi='Segoe UI Bold', acento_c=0.32, cat_c=(0.13, 0.19), luz=0.55, giro2=150,
                          rasgo='acento saturado, radios amplios, pesos fuertes; comercial, campañas, ventas'),
    'sereno':        dict(tinte_h=None, tinte_c=0.010, tarjetas=False, radio=10, radio_panel=16, fuente_titulo='Segoe UI Semibold',
                          fuente_kpi='Segoe UI Light', acento_c=0.12, cat_c=(0.10, 0.13), luz=0.35, giro2=40,
                          rasgo='croma bajo, colores análogos, mucho aire; salud, RR. HH., servicio'),
    'premium':       dict(tinte_h=None, tinte_c=0.006, tarjetas=False, radio=0,  radio_panel=2,  fuente_titulo='Georgia',
                          fuente_kpi='Segoe UI Light', acento_c=0.12, cat_c=(0.10, 0.14), luz=0.25, giro2=30,
                          rasgo='sobrio y caro: casi monocromo, serifa en el título, cifras finas, luces muy tenues'),
    'institucional': dict(tinte_h=255, tinte_c=0.020, tarjetas=True,  radio=4,  radio_panel=8,  fuente_titulo='Segoe UI Semibold',
                          fuente_kpi='Segoe UI Semibold', acento_c=0.32, cat_c=(0.11, 0.15), luz=0.30, giro2=-120,
                          rasgo='formal, neutros con tinte azul, esquinas casi rectas; gobierno, finanzas, auditoría'),
}

FUENTES = {'Segoe UI': 'probado', 'Segoe UI Semibold': 'probado', 'Segoe UI Light': 'probado', 'Segoe UI Bold': 'probado',
           'Georgia': 'probado (solo títulos; nunca cifras)', 'Bahnschrift': 'por validar (Windows 10+; no está en la lista de Power BI)',
           'Corbel': 'por validar', 'Candara': 'por validar', 'Constantia': 'por validar (solo títulos)', 'Trebuchet MS': 'por validar'}

# luminosidad OKLCH objetivo de los neutros por modo
_NEUTROS = {'claro':  dict(pagina=0.968, pagina_sin=0.978, superficie=0.997, linea=0.900, tinta=0.215, tinta2=0.405,
                           tinta3=0.505, contexto=0.640, contexto_suave=0.855),
            'oscuro': dict(pagina=0.165, pagina_sin=0.165, superficie=0.215, linea=0.320, tinta=0.955, tinta2=0.845,
                           tinta3=0.745, contexto=0.600, contexto_suave=0.360)}


def _hasta_contraste(L, C, H, fondos, minimo, modo):
    """Mueve L (más oscuro en claro, más claro en oscuro) hasta que el color cumpla `minimo` contra todos los fondos."""
    paso = -0.005 if modo == 'claro' else 0.005
    for _ in range(220):
        h = desde_oklch(L, C, H)
        if all(contraste(h, f) >= minimo for f in fondos): return h, L
        L += paso
        if not 0 <= L <= 1: break
    return desde_oklch(min(max(L, 0), 1), C, H), L


def _neutros(modo, car, h_acento, capas=1):
    H = car['tinte_h'] if car['tinte_h'] is not None else h_acento
    c, n = car['tinte_c'], _NEUTROS[modo]
    pag = desde_oklch(n['pagina'] if car['tarjetas'] else n['pagina_sin'], c, H)
    sup = desde_oklch(n['superficie'], c * 0.3, H) if car['tarjetas'] else pag
    if modo == 'oscuro' and car['tarjetas']: sup = desde_oklch(n['superficie'], c * 1.4, H)
    fondos = [pag, sup]
    out = dict(pagina=pag, superficie=sup, linea=desde_oklch(n['linea'], c * 1.2, H))
    out['tinta'], _ = _hasta_contraste(n['tinta'], c * 1.6, H, fondos, 12.0, modo)
    out['tinta2'], _ = _hasta_contraste(n['tinta2'], c * 1.8, H, fondos, 7.0, modo)
    out['tinta3'], _ = _hasta_contraste(n['tinta3'], c * 1.8, H, fondos, MARGEN[capas]['texto'], modo)
    out['contexto'], _ = _hasta_contraste(n['contexto'], c * 2.0, H, fondos, CONTRASTE_MARCA, modo)
    out['contexto_suave'] = desde_oklch(n['contexto_suave'], c * 1.6, H)
    return out


def _estado(nombre, modo, fondos, capas=1):
    H = ESTADOS[nombre]; L0 = {'claro': 0.52, 'oscuro': 0.78}[modo]
    C = 0.15 if modo == 'claro' else 0.14
    return _hasta_contraste(L0, C, H, fondos, MARGEN[capas]['estado'], modo)[0]


def _secuencial(modo, acento, sup):
    L, C, H = oklch(acento)
    if modo == 'claro':
        Ls = [0.95, 0.86, 0.76, 0.66, 0.56, min(L, 0.47)]
    else:
        Ls = [0.30, 0.40, 0.50, 0.61, 0.72, 0.84]
    Cs = [max(0.03, C * f) for f in (0.25, 0.45, 0.65, 0.85, 1.0, 1.0)]
    return [desde_oklch(l, min(c, croma_max(l, H)), H) for l, c in zip(Ls, Cs)]


def _validar_ordinal(rampa):
    Ls = [oklch(c)[0] for c in rampa]; Hs = [oklch(c)[2] for c in rampa if oklch(c)[1] > 0.02]
    monotona = all(b < a for a, b in zip(Ls, Ls[1:])) or all(b > a for a, b in zip(Ls, Ls[1:]))
    paso = min(abs(b - a) for a, b in zip(Ls, Ls[1:]))
    spread = max((_dist_matiz(a, b) for a in Hs for b in Hs), default=0)
    return dict(monotona=monotona, paso_min=round(paso, 3), dispersion_matiz=round(spread), ok=monotona and paso >= 0.06 and spread <= 40)


def validar_categoricos(pal, modo, superficie, pares='adyacentes'):
    lo, hi = BANDA[modo]; n = len(pal)
    lista = [(i, j) for i in range(n) for j in range(i + 1, n)] if pares == 'todos' else [(i, i + 1) for i in range(n - 1)]
    banda = [c for c in pal if not lo <= oklch(c)[0] <= hi]
    croma = [c for c in pal if oklch(c)[1] < CROMA_MIN]
    cvd = min((_cvd(pal[i], pal[j]), pal[i], pal[j]) for i, j in lista)
    nor = min((delta_e(pal[i], pal[j]), pal[i], pal[j]) for i, j in lista)
    tri = min(delta_e(pal[i], pal[j], 'tritan') for i, j in lista)
    bajo = [(c, round(contraste(c, superficie), 2)) for c in pal if contraste(c, superficie) < CONTRASTE_MARCA]
    estado_cvd = 'pasa' if cvd[0] >= CVD_META else ('piso' if cvd[0] >= CVD_PISO else 'falla')
    ok = not banda and not croma and estado_cvd != 'falla' and nor[0] >= NORMAL_PISO
    return dict(ok=ok, pares=pares, fuera_de_banda=banda, croma_baja=croma, cvd=round(cvd[0], 1), cvd_estado=estado_cvd,
                cvd_par=cvd[1:], normal=round(nor[0], 1), normal_par=nor[1:], tritan=round(tri, 1), contraste_bajo=bajo)


def _categoricos(modo, acento, superficie, car, n=8):
    lo, hi = BANDA[modo]; cmin, cmax = car['cat_c']
    Ls = [lo + (hi - lo) * f for f in ((0.15, 0.35, 0.55, 0.75) if modo == 'claro' else (0.2, 0.45, 0.7, 0.9))]
    L0, C0, H0 = oklch(acento)
    # ranura 1 = acento llevado a la banda y al croma mínimo
    L1 = min(max(L0, lo + 0.02), hi - 0.02); C1 = max(min(C0, cmax), cmin + 0.01)
    c1 = desde_oklch(L1, min(C1, croma_max(L1, H0)), H0)
    if oklch(c1)[1] < CROMA_MIN:   # acento casi gris (marca neutra): primer categórico = matiz del acento con croma mínima posible
        Lb = max(Ls, key=lambda l: croma_max(l, H0)); c1 = desde_oklch(Lb, max(cmin + 0.01, 0.11), H0)
    pool, Lm = [], (lo + hi) / 2
    for H in range(0, 360, 6):
        for L in Ls:
            C = min(cmax, croma_max(L, H))
            if C < max(cmin, CROMA_MIN + 0.008) or turbio(L, H): continue
            h = desde_oklch(L, C, H)
            pool.append((h, contraste(h, superficie) >= CONTRASTE_MARCA, abs(L - Lm)))
    elegidos = [c1]
    while len(elegidos) < n:
        mejor = None
        for h, ok_con, dl in pool:
            if h in elegidos: continue
            prev = elegidos[-1]
            dn_prev, dc_prev = delta_e(h, prev), _cvd(h, prev)
            if dn_prev < NORMAL_PISO or dc_prev < CVD_META: continue
            dn = min(delta_e(h, e) for e in elegidos); dc = min(_cvd(h, e) for e in elegidos)
            s = min(dn, 1.8 * dc) + (4 if ok_con else 0) + 0.15 * dc_prev - 25 * dl   # premia L cerca del centro de la banda
            if mejor is None or s > mejor[0]: mejor = (s, h)
        if mejor is None: break
        elegidos.append(mejor[1])
    return elegidos


def _base_validada(modo):
    tk = json.load(open(_TOK, encoding='utf-8'))['direcciones']
    return list(tk['moderno' if modo == 'claro' else 'aurora']['categoricos'])


def _choque_estado(h_hex):
    L, C, H = oklch(h_hex)
    if C < 0.06: return None
    for n, he in ESTADOS.items():
        if _dist_matiz(H, he) <= 22: return n
    return None


def turbio(L, H, modo='claro'):
    """Oliva y marrón: amarillos/verde lima con L baja y naranjas oscuros. Se ven sucios en un tablero; se evitan al generar."""
    return (55 <= H <= 135 and L < 0.66) or (30 <= H < 55 and L < 0.56)


def _rgba(h, a):
    r, g, b = (round(v * 255) for v in _hex(h)); return f'rgba({r},{g},{b},{a})'


def generar(nombre, modo, semillas, caracter='neutro', capas=1, uso='', inspiracion='', fuente_titulo=None, fuente_kpi=None):
    car = dict(CARACTERES[caracter])
    if fuente_titulo: car['fuente_titulo'] = fuente_titulo
    if fuente_kpi: car['fuente_kpi'] = fuente_kpi
    semillas = [s if s.startswith('#') else '#' + s for s in semillas]
    avisos = []
    # acento: primera semilla que no choque con un estado; si todas chocan, la primera (y aviso)
    cromaticas = [s for s in semillas if oklch(s)[1] >= 0.04]
    candidatas = [s for s in cromaticas if not _choque_estado(s)] or cromaticas
    if not candidatas:   # todas casi grises: el acento toma el matiz del carácter (o azul) y las semillas quedan como marca
        Hs = car['tinte_h'] if car['tinte_h'] is not None else 250
        sem_acento = desde_oklch(0.50, 0.13, Hs)
        avisos.append(f'semillas casi grises: quedan en `marca`; el acento usa el matiz {Hs}° del carácter ({sem_acento})')
    else:
        sem_acento = candidatas[0]
        if sem_acento != semillas[0]:
            motivo = (f'cae en el matiz de «{_choque_estado(semillas[0])}»' if _choque_estado(semillas[0]) else 'es casi gris')
            avisos.append(f'{semillas[0]} {motivo}: queda como color de marca (decoración); el acento sale de {sem_acento}')
        elif _choque_estado(sem_acento):
            avisos.append(f'el acento {sem_acento} cae en el matiz de «{_choque_estado(sem_acento)}»: estado SIEMPRE con ícono + texto, '
                          'y el color de estado nunca en títulos ni kickers')
    L0, C0, H0 = oklch(sem_acento)
    neu = _neutros(modo, car, H0, capas)
    fondos = [neu['pagina'], neu['superficie']]
    C_ac = min(C0, car['acento_c'])
    meta_ac = MARGEN[capas]['enfasis']
    acento, _ = _hasta_contraste(L0, C_ac, H0, fondos, meta_ac, modo)
    if acento.upper() != sem_acento.upper():
        avisos.append(f'acento ajustado {sem_acento} → {acento} para {meta_ac}:1 sobre página y superficie; el original queda en `marca`')
    # acento 2: segunda semilla o giro de matiz según el carácter (marcas y decoración: 3:1)
    otras = [s for s in semillas if s != sem_acento and oklch(s)[1] >= 0.04]
    if otras:
        L2, C2, H2 = oklch(otras[0])
    else:   # giro de matiz según el carácter, esquivando verde/ámbar/rojo (acento2 sintético nunca parece un estado)
        L2, C2, H2 = L0, max(C_ac, 0.08), (H0 + car['giro2']) % 360
        for _ in range(24):
            if all(_dist_matiz(H2, he) > 28 for he in ESTADOS.values()) and not 55 <= H2 <= 135: break
            H2 = (H2 + (15 if car['giro2'] >= 0 else -15)) % 360
    acento2, _ = _hasta_contraste(L2, min(C2, car['acento_c']), H2, fondos, CONTRASTE_MARCA, modo)
    if _choque_estado(acento2):
        avisos.append(f'acento2 {acento2} cae en el matiz de «{_choque_estado(acento2)}»: úsalo solo en decoración (capa de fondo, '
                      'reglas), nunca en marcas de datos')
    suave = desde_oklch(0.945 if modo == 'claro' else 0.30, min(0.04, C_ac * 0.35), H0)
    d = dict(uso=uso or f'a la medida ({caracter}, {modo})', fuente='Segoe UI', fuente_titulo=car['fuente_titulo'],
             fuente_kpi=car['fuente_kpi'], **neu, acento=acento, acento2=acento2, acento_suave=suave)
    for e in ('bien', 'alerta', 'mal'): d[e] = _estado(e, modo, fondos, capas)
    d['secuencial'] = _secuencial(modo, acento, neu['superficie'])
    sup_graf = neu['superficie']
    cat = _categoricos(modo, acento, sup_graf, car)
    val = validar_categoricos(cat, modo, sup_graf) if len(cat) == 8 else dict(ok=False)
    if not val['ok']:
        avisos.append('no salió una paleta categórica propia válida: se usa la validada de la skill '
                      f"({'moderno' if modo == 'claro' else 'aurora'})")
        cat = _base_validada(modo); val = validar_categoricos(cat, modo, sup_graf)
    d['categoricos'] = cat
    d.update(tarjetas=car['tarjetas'], capas=capas, radio=car['radio'], radio_panel=car['radio_panel'],
             marca=semillas, caracter=caracter)
    if capas == 2:
        if modo == 'oscuro':
            a = desde_oklch(0.22, 0.05, H0); c = desde_oklch(0.19, 0.05, H2)
            d['fondo_base'] = f"linear-gradient(160deg,{a} 0%,{neu['pagina']} 48%,{c} 100%)"
            d['luces'] = [desde_oklch(0.72, 0.15, H0), desde_oklch(0.66, 0.15, (H0 + H2) / 2 if abs(H0 - H2) < 180 else (H0 + H2 + 360) / 2 % 360),
                          desde_oklch(0.62, 0.16, H2)]
            d['panel'] = ('background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.10);box-shadow:inset 0 1px 0 '
                          'rgba(255,255,255,.06),0 18px 40px rgba(0,0,0,.35);backdrop-filter:blur(18px) saturate(140%)')
            d['control'] = 'background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.14)'
        else:
            a = desde_oklch(0.975, 0.012, H0); c = desde_oklch(0.965, 0.014, H2)
            d['fondo_base'] = f"linear-gradient(135deg,{a} 0%,{neu['pagina']} 50%,{c} 100%)"
            d['luces'] = [desde_oklch(0.84, 0.09, H0), desde_oklch(0.86, 0.08, (H0 + 50) % 360), desde_oklch(0.88, 0.08, H2)]
            sombra = _rgba(desde_oklch(0.30, 0.05, H0), .08)
            d['panel'] = (f'background:rgba(255,255,255,.64);border:1px solid rgba(255,255,255,.9);box-shadow:0 10px 30px {sombra},'
                          f'0 1px 2px {sombra};backdrop-filter:blur(20px) saturate(160%)')
            d['control'] = 'background:rgba(255,255,255,.7);border:1px solid rgba(255,255,255,.95)'
        d['luz_opacidad'] = car['luz']
    rep = dict(contraste_texto={k: {f: round(contraste(d[k], d[f]), 2) for f in ('pagina', 'superficie')}
                                for k in ('tinta', 'tinta2', 'tinta3', 'acento', 'bien', 'alerta', 'mal')},
               contraste_marcas={k: {f: round(contraste(d[k], d[f]), 2) for f in ('pagina', 'superficie')} for k in ('contexto', 'acento2')},
               categoricos_adyacentes=val, categoricos_todos=validar_categoricos(cat, modo, sup_graf, 'todos'),
               secuencial=_validar_ordinal(d['secuencial']), fuentes={f: FUENTES.get(f, 'por validar') for f in
                                                                       {d['fuente'], d['fuente_titulo'], d['fuente_kpi']}})
    textos_ok = all(v >= CONTRASTE_TEXTO for x in rep['contraste_texto'].values() for v in x.values())
    marcas_ok = all(v >= CONTRASTE_MARCA for x in rep['contraste_marcas'].values() for v in x.values())
    rep['ok'] = textos_ok and marcas_ok and val['ok'] and rep['secuencial']['ok']
    if capas == 2: avisos.append('2 capas: el contraste final del texto se mide con revisar_html.js sobre la imagen de fondo')
    origen = dict(semillas=semillas, caracter=caracter, modo=modo, capas=capas, inspiracion=inspiracion,
                  fecha=datetime.date.today().isoformat(), rasgo=car['rasgo'])
    return {'_nota': 'Dirección a la medida generada por scripts/estilo_a_medida.py. Úsala con PBIX_TOKENS_EXTRA=<este archivo>.',
            'direcciones': {nombre: d}, '_origen': origen, 'validacion': rep, '_avisos': avisos}


def muestra_html(x, ruta):
    """Hoja de muestra simple (no es un diseño): neutros, acento, estados, categóricos, secuencial y un texto de prueba."""
    n, d = next(iter(x['direcciones'].items()))
    sw = lambda c, t='': (f'<div style="display:inline-block;margin:0 8px 8px 0;font:12px Segoe UI;color:{d["tinta2"]}">'
                          f'<div style="width:72px;height:40px;background:{c};border:1px solid {d["linea"]}"></div>{t or c}</div>')
    fila = lambda tit, cs: f'<h3 style="font:600 13px Segoe UI;margin:16px 0 6px">{tit}</h3>' + ''.join(sw(c) for c in cs)
    neu = [d[k] for k in ('pagina', 'superficie', 'linea', 'contexto_suave', 'contexto', 'tinta3', 'tinta2', 'tinta')]
    html = (f'<!doctype html><meta charset="utf-8"><title>{n}</title><body style="margin:0;background:{d["pagina"]};color:{d["tinta"]};'
            f'font-family:Segoe UI;padding:24px"><div style="font:600 12px Segoe UI;color:{d["acento"]}">Estilo a la medida · '
            f'{x["_origen"]["caracter"]} · {x["_origen"]["modo"]}</div><h1 style="font:600 26px {d["fuente_titulo"]},Segoe UI;margin:4px 0">'
            f'{n}</h1><div style="color:{d["tinta3"]};font-size:13px">{x["_origen"]["rasgo"]}</div>'
            f'<div style="background:{d["superficie"]};border:1px solid {d["linea"]};border-radius:{d["radio"]}px;padding:16px;'
            f'margin:16px 0;width:360px"><div style="font-size:12px;color:{d["tinta3"]}">Ventas netas · ene–sep</div>'
            f'<div style="font:36px {d["fuente_kpi"]},Segoe UI">$1,234.5 M</div><div style="font-size:12px;color:{d["bien"]}">▲ 4.2 % '
            f'<span style="color:{d["tinta3"]}">vs año anterior</span></div></div>'
            + fila('Neutros', neu) + fila('Acento · acento 2 · suave · marca', [d['acento'], d['acento2'], d['acento_suave']] + d['marca'])
            + fila('Estados', [d['bien'], d['alerta'], d['mal']]) + fila('Categóricos', d['categoricos'])
            + fila('Secuencial', d['secuencial']) + '</body>')
    open(ruta, 'w', encoding='utf-8').write(html)


def _imprimir(x):
    n, d = next(iter(x['direcciones'].items())); v = x['validacion']
    print(f'Dirección «{n}» ({x["_origen"]["caracter"]}, {x["_origen"]["modo"]}, {d["capas"]} capa/s) → '
          f'{"OK" if v["ok"] else "REVISAR"}')
    m = MARGEN[d['capas']]
    print(f'  texto (meta {m["texto"]}, énfasis {m["enfasis"]}, estados {m["estado"]}): ' + ', '.join(f'{k} {min(c.values())}' for k, c in v['contraste_texto'].items()))
    print('  marcas (≥3):  ' + ', '.join(f'{k} {min(c.values())}' for k, c in v['contraste_marcas'].items()))
    a = v['categoricos_adyacentes']; t = v['categoricos_todos']
    print(f'  categóricos: {"OK" if a["ok"] else "FALLA"} · CVD adyacente {a["cvd"]} ({a["cvd_estado"]}) · normal adyacente {a["normal"]} · '
          f'todos los pares: CVD {t["cvd"]} normal {t["normal"]} · contraste < 3: {len(a["contraste_bajo"])}')
    s = v['secuencial']; print(f'  secuencial: {"OK" if s["ok"] else "FALLA"} · paso ΔL {s["paso_min"]} · matiz ±{s["dispersion_matiz"]}°')
    print('  fuentes: ' + '; '.join(f'{k} [{e}]' for k, e in v['fuentes'].items()))
    for av in x['_avisos']: print('  aviso:', av)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--nombre'); ap.add_argument('--modo', choices=['claro', 'oscuro'], default='claro')
    ap.add_argument('--semillas', help='1–3 colores hex separados por coma (inspiración o marca)')
    ap.add_argument('--caracter', choices=list(CARACTERES), default='neutro'); ap.add_argument('--capas', type=int, choices=[1, 2], default=1)
    ap.add_argument('--uso', default=''); ap.add_argument('--inspiracion', default='')
    ap.add_argument('--fuente-titulo'); ap.add_argument('--fuente-kpi')
    ap.add_argument('--salida'); ap.add_argument('--muestra', action='store_true', help='escribe además <salida>.html')
    ap.add_argument('--caracteres', action='store_true', help='lista los caracteres y sale')
    a = ap.parse_args()
    if a.caracteres:
        for k, c in CARACTERES.items(): print(f'{k:14} {c["rasgo"]}')
        return
    if not (a.nombre and a.semillas): ap.error('faltan --nombre y --semillas')
    x = generar(a.nombre, a.modo, [s.strip() for s in a.semillas.split(',') if s.strip()], a.caracter, a.capas, a.uso,
                a.inspiracion, a.fuente_titulo, a.fuente_kpi)
    _imprimir(x)
    if a.salida:
        os.makedirs(os.path.dirname(os.path.abspath(a.salida)), exist_ok=True)
        json.dump(x, open(a.salida, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('→', a.salida)
        if a.muestra:
            muestra_html(x, os.path.splitext(a.salida)[0] + '.html'); print('→', os.path.splitext(a.salida)[0] + '.html')
    sys.exit(0 if x['validacion']['ok'] else 1)


if __name__ == '__main__':
    main()
