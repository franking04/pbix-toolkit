"""Genera un script TMDL (vista TMDL de Power BI Desktop) que cambia propiedades de medidas existentes
—normalmente formatString— reescribiendo la DEFINICIÓN COMPLETA de cada medida desde leer_modelo.py.
`createOrReplace` reemplaza el objeto entero: lo que no se escriba se pierde (por eso se repiten expresión,
lineageTag, carpeta y descripción).
Uso: python tmdl_medidas.py modelo_<archivo>.json salida.tmdl "Tabla[Medida]=formato" "Tabla[Medida]:=nueva expresión DAX" ...
Probado: createOrReplace + ref table + medida de una línea con formatString.
Por validar: expresiones multilínea y conservar lineageTag (antes de esto, la medida recibía uno nuevo)."""
import json, re, sys
from collections import defaultdict

def nombre_tmdl(n):
    return n if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', n) else "'" + n.replace("'", "''") + "'"

def bloque_medida(m, formato):
    t2, t3, t4 = '\t\t', '\t\t\t', '\t\t\t\t'
    lineas = []
    if m.get('descripcion'):
        lineas += [f'{t2}/// {l}' for l in str(m['descripcion']).splitlines()]
    expr = (m.get('expresion') or '').strip('\n').rstrip()
    partes = [l.rstrip() for l in expr.splitlines() if l.strip()]
    if len(partes) <= 1:
        lineas.append(f"{t2}measure {nombre_tmdl(m['medida'])} = {expr.strip()}")
    else:                                            # expresión multilínea: un nivel más que las propiedades
        sangria = min(len(l) - len(l.lstrip()) for l in partes)
        lineas.append(f"{t2}measure {nombre_tmdl(m['medida'])} =")
        lineas += [t4 + l[sangria:] for l in partes]
    if formato: lineas.append(f'{t3}formatString: {formato}')
    if m.get('carpeta'): lineas.append(f"{t3}displayFolder: {m['carpeta']}")
    if m.get('lineage_tag'): lineas.append(f"{t3}lineageTag: {m['lineage_tag']}")
    return lineas

def generar(ruta_modelo, cambios):
    meds = {(x['tabla'], x['medida']): x for x in (lambda d: d.get('modelo') or d['sqlite'])(json.load(open(ruta_modelo, encoding='utf-8')))['medidas']}
    por_tabla = defaultdict(list)
    for c in cambios:
        mt = re.fullmatch(r'(.+?)\[(.+?)\](:?=)(.*)', c, re.S)
        if not mt: raise SystemExit(f'Cambio inválido: {c}  (use Tabla[Medida]=formato o Tabla[Medida]:=expresión DAX)')
        tabla, medida, op, valor = mt.groups()
        if (tabla, medida) not in meds: raise SystemExit(f'No existe la medida {tabla}[{medida}] en el modelo')
        m = dict(meds[(tabla, medida)])
        if op == ':=': m['expresion'] = valor; formato = m.get('formato')       # nueva expresión, conserva el formato
        else: formato = valor
        por_tabla[tabla].append(bloque_medida(m, formato))
    out = ['createOrReplace', '']
    for tabla, bloques in por_tabla.items():
        out += [f'\tref table {nombre_tmdl(tabla)}', '']
        for b in bloques: out += b + ['']
    return '\n'.join(out)

if __name__ == '__main__':
    from comun import ayuda; ayuda(__doc__, 2)
    texto = generar(sys.argv[1], sys.argv[3:])
    open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(texto)
    print(texto)
