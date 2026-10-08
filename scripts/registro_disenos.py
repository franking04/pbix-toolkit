"""Registro de diseños entregados y control anti-repetición.

Cada diseño queda como una ficha corta (arquetipo, estilo, acento, tipografía, forma, héroe, visuales firma, inspiración).
`comparar` puntúa una propuesta contra el registro (0–1) y dice en qué se parece; así la skill propone algo distinto a lo último
que entregó en vez de repetir el mismo estilo. Las páginas de un mismo reporte (misma `familia`) no se comparan entre sí: ahí la
coherencia es lo correcto.

Dónde vive el registro: --registro, o la variable PBIX_REGISTRO_DISENOS, o ./registro_disenos.json (carpeta del proyecto).

Uso:
  python registro_disenos.py sembrar                      # agrega los diseños de referencia de la skill (estado 'referencia')
  python registro_disenos.py listar
  python registro_disenos.py comparar --ficha propuesta.json [--ultimos 6]
  python registro_disenos.py agregar --ficha propuesta.json  # al entregar
  python registro_disenos.py resumen                      # qué arquetipos/estilos se repiten
Ficha (JSON): {"reporte", "familia", "pagina", "tipo", "publico", "nivel", "arquetipo", "direccion", "tokens" (ruta de
estilo_a_medida, opcional), "modo", "capas", "acento", "fuente_titulo", "tarjetas", "radio", "heroe", "firmas": [...],
"inspiracion": [...], "estado": "propuesta|entregado|referencia"}. Si trae "tokens" o una "direccion" conocida, los campos de
estilo (modo, capas, acento, fuente_titulo, tarjetas, radio) se completan solos."""
import argparse, datetime, json, math, os, sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _AQUI)
PESOS = dict(arquetipo=3.0, direccion=1.5, acento=2.0, modo=1.0, capas=0.5, fuente_titulo=0.5, tarjetas=0.5, radio=0.5,
             heroe=1.0, firmas=1.5, nivel=0.5)
UMBRAL_REPITE, UMBRAL_PARECIDO = 0.60, 0.45
CAMPOS_ESTILO = ('modo', 'capas', 'acento', 'fuente_titulo', 'tarjetas', 'radio')

# Diseños de referencia de la skill (references/disenos/).
REFERENCIAS = [
    dict(reporte='ref:ejecutivo', tipo='ejecutivo', nivel='sobrio', arquetipo='heroe_tira', direccion='moderno', heroe='cifra+linea',
         firmas=['linea_vs_anterior', 'ranking_enfasis']),
    dict(reporte='ref:financiero', tipo='financiero', nivel='sobrio', arquetipo='puente', direccion='editorial', heroe='cifra',
         firmas=['matriz_favorabilidad', 'cascada']),
    dict(reporte='ref:operativo', tipo='operativo', nivel='sobrio', arquetipo='excepciones', direccion='moderno', heroe='estados',
         firmas=['lista_accion', 'columnas_hoy']),
    dict(reporte='ref:operativo_grafito', tipo='operativo', nivel='sobrio', arquetipo='excepciones', direccion='grafito',
         heroe='estados', firmas=['lista_accion', 'columnas_hoy']),
    dict(reporte='ref:analitico', tipo='analitico', nivel='sobrio', arquetipo='small_multiples', direccion='suizo',
         heroe='small_multiples', firmas=['small_multiples', 'dispersion', 'mapa_calor']),
    dict(reporte='ref:detalle', tipo='detalle', nivel='sobrio', arquetipo='detalle_tabla', direccion='suizo', heroe='tabla',
         firmas=['saldos']),
    dict(reporte='ref:comercial_realzado', tipo='comercial', nivel='realzado', arquetipo='heroe_tira', direccion='moderno',
         heroe='tira_kpi', firmas=['pestanas', 'pildora', 'bullet', 'columnas_hoy']),
    dict(reporte='ref:comite_aurora', tipo='comite', nivel='impactante', arquetipo='heroe_tira', direccion='aurora',
         heroe='cifra+anillo', firmas=['anillo', 'area_degradado', 'pildora', 'bullet']),
    dict(reporte='ref:ejecutivo_vidrio', tipo='ejecutivo', nivel='impactante', arquetipo='riel_lateral', direccion='vidrio',
         heroe='cifra+area', firmas=['area_degradado', 'contribucion', 'sparkline']),
]


def _ruta(r=None): return r or os.environ.get('PBIX_REGISTRO_DISENOS') or os.path.join(os.getcwd(), 'registro_disenos.json')

def cargar(r=None):
    p = _ruta(r)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {'_nota': __doc__.splitlines()[0], 'disenos': []}

def guardar(reg, r=None):
    json.dump(reg, open(_ruta(r), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def completar(f):
    """Rellena modo, capas, acento, fuente_titulo, tarjetas y radio desde los tokens (a la medida o de la skill)."""
    f = dict(f)
    try:
        from estilo_a_medida import cargar_tokens, oklch
        tk = cargar_tokens(extra=[f['tokens']] if f.get('tokens') else None)
    except Exception:
        return f
    d = tk['direcciones'].get(f.get('direccion', ''))
    if d is None and f.get('tokens'):
        n, d = next(iter(json.load(open(f['tokens'], encoding='utf-8'))['direcciones'].items())); f['direccion'] = n
    if d:
        L = oklch(d['superficie'])[0]
        f.setdefault('modo', 'claro' if L > 0.5 else 'oscuro'); f.setdefault('capas', d.get('capas', 1))
        f.setdefault('acento', d['acento']); f.setdefault('fuente_titulo', d.get('fuente_titulo'))
        f.setdefault('tarjetas', d.get('tarjetas', True)); f.setdefault('radio', d.get('radio', tk.get('radio', 8)))
        f.setdefault('caracter', d.get('caracter'))
    return f


def _acento_sim(a, b):
    """1 = mismo color; 0 = matiz distinto. Usa OKLCH (matiz y croma) y ΔE."""
    if not a or not b: return 0.0
    from estilo_a_medida import oklch, delta_e
    (La, Ca, Ha), (Lb, Cb, Hb) = oklch(a), oklch(b)
    if Ca < 0.04 and Cb < 0.04: return 1.0
    if min(Ca, Cb) < 0.04: return 0.0
    dh = abs(Ha - Hb) % 360; dh = min(dh, 360 - dh)
    return max(0.0, 1 - dh / 40) if delta_e(a, b) > 6 else 1.0


def similitud(p, q):
    """Devuelve (puntaje 0–1, lista de coincidencias)."""
    s, iguales = 0.0, []
    def suma(campo, v):
        nonlocal s
        s += PESOS[campo] * v
        if v >= 0.5: iguales.append(campo)
    suma('arquetipo', 1.0 if p.get('arquetipo') and p.get('arquetipo') == q.get('arquetipo') else 0.0)
    suma('direccion', 1.0 if p.get('direccion') and p.get('direccion') == q.get('direccion') else 0.0)
    suma('acento', _acento_sim(p.get('acento'), q.get('acento')))
    for c in ('modo', 'capas', 'fuente_titulo', 'tarjetas', 'nivel'):
        suma(c, 1.0 if p.get(c) is not None and p.get(c) == q.get(c) else 0.0)
    ra, rb = p.get('radio'), q.get('radio')
    suma('radio', 1.0 if ra is not None and rb is not None and abs(ra - rb) <= 2 else 0.0)
    suma('heroe', 1.0 if p.get('heroe') and p.get('heroe') == q.get('heroe') else 0.0)
    A, B = set(p.get('firmas', [])), set(q.get('firmas', []))
    suma('firmas', len(A & B) / len(A | B) if A | B else 0.0)
    return round(s / sum(PESOS.values()), 2), iguales


def comparar(ficha, reg, ultimos=6):
    p = completar(ficha)
    otros = [d for d in reg['disenos'] if not (p.get('familia') and d.get('familia') == p.get('familia'))]
    entregados = [d for d in otros if d.get('estado') != 'referencia'][-ultimos:]
    refs = [d for d in otros if d.get('estado') == 'referencia']
    res = sorted(((similitud(p, d), d) for d in entregados + refs), key=lambda x: -x[0][0])
    return p, res


def _sugerencias(iguales):
    s = []
    if 'arquetipo' in iguales: s.append('otro arquetipo (arquetipos.md) que responda la misma premisa')
    if 'direccion' in iguales or 'acento' in iguales: s.append('estilo a la medida con otras semillas o carácter (estilo_a_medida.py)')
    if 'heroe' in iguales or 'firmas' in iguales: s.append('otro héroe o visual firma (traductor_powerbi.md)')
    if 'modo' in iguales and 'capas' in iguales: s.append('cambiar modo (claro/oscuro) o nivel de capas si el medio lo permite')
    return s


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('accion', choices=['sembrar', 'listar', 'comparar', 'agregar', 'resumen'])
    ap.add_argument('--ficha'); ap.add_argument('--registro'); ap.add_argument('--ultimos', type=int, default=6)
    a = ap.parse_args(); reg = cargar(a.registro)
    if a.accion == 'sembrar':
        ya = {d['reporte'] for d in reg['disenos']}; n = 0
        for d in REFERENCIAS:
            if d['reporte'] in ya: continue
            d = completar(dict(d)); d.setdefault('estado', 'referencia'); d.setdefault('fecha', datetime.date.today().isoformat()); reg['disenos'].append(d); n += 1
        guardar(reg, a.registro); print(f'{n} diseños agregados → {_ruta(a.registro)}')
    elif a.accion == 'listar':
        for d in reg['disenos']:
            print(f"{d.get('fecha', ''):10} {d.get('estado', ''):10} {d.get('arquetipo', ''):18} {d.get('direccion', ''):12} "
                  f"{d.get('modo', ''):6} {d.get('acento', ''):8} {d['reporte']}")
    elif a.accion == 'resumen':
        from collections import Counter
        ent = [d for d in reg['disenos']]
        for campo in ('arquetipo', 'direccion', 'modo', 'heroe'):
            c = Counter(d.get(campo) for d in ent); print(f'{campo:10}', ', '.join(f'{k} {v}' for k, v in c.most_common()))
    elif a.accion in ('comparar', 'agregar'):
        if not a.ficha: ap.error('falta --ficha')
        ficha = json.load(open(a.ficha, encoding='utf-8'))
        p, res = comparar(ficha, reg, a.ultimos)
        peor = res[0] if res else ((0, []), {})
        print(f"Propuesta: {p.get('arquetipo')} · {p.get('direccion')} · {p.get('modo')} · acento {p.get('acento')} · héroe {p.get('heroe')}")
        for (pt, ig), d in res[:5]:
            print(f"  {pt:.2f}  {d['reporte']:42} iguales: {', '.join(ig) or '—'}")
        (pt, ig), d = peor
        if pt >= UMBRAL_REPITE:
            print(f'REPITE ({pt:.2f} ≥ {UMBRAL_REPITE}) con «{d["reporte"]}». Cambia: ' + '; '.join(_sugerencias(ig)))
        elif pt >= UMBRAL_PARECIDO:
            print(f'PARECIDO ({pt:.2f}) con «{d["reporte"]}»: justifícalo en la ficha o cambia ' + '; '.join(_sugerencias(ig)[:1]))
        else:
            print('DISTINTO: ningún diseño anterior se le parece (máx. %.2f)' % pt)
        if a.accion == 'agregar':
            p.setdefault('fecha', datetime.date.today().isoformat()); p.setdefault('estado', 'entregado')
            reg['disenos'].append(p); guardar(reg, a.registro); print('registrado →', _ruta(a.registro))
        sys.exit(1 if a.accion == 'comparar' and pt >= UMBRAL_REPITE else 0)


if __name__ == '__main__':
    main()
