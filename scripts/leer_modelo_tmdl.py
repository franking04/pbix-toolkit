"""Lee el modelo semántico desde TMDL (texto oficial de Microsoft) — sin pbixray, sin red, en cualquier sistema.

De dónde sale el TMDL (en este orden):
  1. Una pestaña de la vista TMDL guardada dentro del .pbix (TMDLScripts/*.tmdl) que tenga el modelo completo.
     Cómo la crea el usuario (una vez por archivo, ~30 s): vista TMDL → pestaña nueva (+) → panel Datos, pestaña Modelo →
     arrastrar «Modelo semántico» al editor → NO pulsar Aplicar → Ctrl+S.
     [probado: Desktop de la nube 2026.09 y Desktop para RS 2026.05: igual que pbixray]
  2. La carpeta de un proyecto .pbip (`<nombre>.SemanticModel/definition/`), que el Desktop de la nube escribe en TMDL.
  3. Un archivo .tmdl suelto.
Es una FOTO del modelo al momento de arrastrar: si después cambian medidas o columnas, hay que volver a arrastrar
(`verificar`/`cruzar` lo delatan como referencias rotas).

Salida: el mismo JSON que leer_modelo.py (clave "modelo" con columnas, medidas, tablas, variaciones, relaciones,
anotaciones) + power_query, expresiones, roles. Solo metadatos: los datos incrustados en M (Binary.FromText base64 de
«Especificar datos») se reemplazan por un marcador y nunca se decodifican.
Uso: python leer_modelo_tmdl.py archivo.pbix|carpeta.SemanticModel|script.tmdl carpeta_salida
Modelo grande [probado: guardado por el Desktop de la nube]: 512/512 columnas y 83/83 medidas iguales a pbixray (formato,
expresión, carpeta, lineageTag), 48/48 relaciones, 5/5 variaciones; además trae las tablas de fecha automáticas (pbixray no).
Casos cubiertos: nombre sin comillas terminado en ':' (`column Región:`) y sourceColumn entre comillas dobles.
"""
import json, os, re, sys, zipfile
from pathlib import Path

OBJETOS = {'model', 'database', 'table', 'column', 'measure', 'partition', 'relationship', 'hierarchy', 'level',
           'variation', 'annotation', 'culture', 'role', 'tablePermission', 'expression', 'perspective', 'calculationGroup',
           'calculationItem', 'dataSource', 'queryGroup', 'calendar', 'function', 'extendedProperty', 'member',
           'linguisticMetadata', 'refreshPolicy', 'columnPermission', 'perspectiveTable', 'perspectiveColumn',
           'perspectiveMeasure', 'perspectiveHierarchy'}
TIPO_DATO = {'string': 'String', 'int64': 'Int64', 'double': 'Double', 'dateTime': 'DateTime', 'decimal': 'Decimal',
             'boolean': 'Boolean', 'binary': 'Binary', 'variant': 'Variant', 'automatic': 'Automatic'}
RESUMIR = {'none': 'None', 'sum': 'Sum', 'min': 'Min', 'max': 'Max', 'count': 'Count', 'average': 'Average',
           'distinctCount': 'DistinctCount', 'default': 'Default'}
# Nombre sin comillas: puede terminar en ':' (el Desktop escribe `column Región:` sin comillas [probado])
_NOMBRE = r"'(?:[^']|'')*'|[^\s=:'][^=]*?"
RE_OBJ = re.compile(rf"^(?P<tipo>[A-Za-z]+)\s+(?P<nombre>{_NOMBRE})\s*(?:=\s*(?P<expr>.*))?$")
RE_OBJ_SOLO = re.compile(r"^(?P<tipo>[A-Za-z]+)\s*(?:=\s*(?P<expr>.*))?$")
RE_PROP = re.compile(r"^(?P<k>[A-Za-z][\w]*)\s*:\s*(?P<v>.*)$")
RE_PROP_EXPR = re.compile(r"^(?P<k>[A-Za-z][\w]*)\s*=\s*(?P<v>.*)$")
RE_B64 = re.compile(r'Binary\.FromText\(\s*"([A-Za-z0-9+/=]{120,})"')


def quitar_comillas(n):
    """'Nombre' (objetos) o "valor" (p. ej. sourceColumn con espacios al inicio/fin: `sourceColumn: " Monto "` [probado])."""
    n = n.strip()
    if len(n) >= 2 and n[0] == n[-1] and n[0] in "'\"":
        return n[1:-1].replace(n[0] * 2, n[0])
    return n


def ref_columna(v):
    """'Tabla con espacios'.Columna | Tabla.'Col' → (tabla, columna)."""
    m = re.match(r"^('(?:[^']|'')*'|[^.']+)\.('(?:[^']|'')*'|.+)$", v.strip())
    return (quitar_comillas(m.group(1)), quitar_comillas(m.group(2))) if m else (None, v.strip())


def _sangria(linea):
    return len(linea) - len(linea.lstrip('\t'))


class Nodo:
    def __init__(self, tipo, nombre, nivel, expr=None):
        self.tipo, self.nombre, self.nivel, self.expr = tipo, nombre, nivel, expr
        self.props, self.hijos, self.desc = {}, [], None

    def p(self, k, defecto=None): return self.props.get(k, defecto)


def parsear(texto):
    """TMDL → árbol de Nodo. Tolera scripts (createOrReplace + model) y archivos de carpeta (objetos en nivel 0)."""
    raiz = Nodo('raiz', None, -1)
    pila = [raiz]
    lineas = texto.replace('\r\n', '\n').split('\n')
    i, desc = 0, []

    def leer_expr(inicio, limite_nivel, primera):
        """Lee una expresión: lo que sigue a '=' en la línea + líneas más profundas que limite_nivel (o bloque ```)."""
        j = inicio
        if primera.strip().startswith('```'):
            partes = [primera.strip()[3:]]
            while j < len(lineas) and '```' not in lineas[j]:
                partes.append(lineas[j]); j += 1
            if j < len(lineas): partes.append(lineas[j].split('```')[0]); j += 1
            return '\n'.join(partes).strip('\n'), j
        partes = [primera] if primera.strip() else []
        while j < len(lineas):
            l = lineas[j]
            if l.strip() and _sangria(l) <= limite_nivel: break
            partes.append(l); j += 1
        while partes and not partes[-1].strip(): partes.pop()
        base = min((_sangria(x) for x in partes[1 if primera.strip() else 0:] if x.strip()), default=0)
        cuerpo = [x[base:] if _sangria(x) >= base else x.lstrip('\t') for x in partes[1 if primera.strip() else 0:]]
        return ('\n'.join(([primera.strip()] if primera.strip() else []) + cuerpo)).strip('\n'), j

    while i < len(lineas):
        l = lineas[i]; i += 1
        if not l.strip(): continue
        nivel, s = _sangria(l), l.strip()
        if s.startswith('///'):
            desc.append(s[3:].strip()); continue
        if s in ('createOrReplace', 'createOrReplace ', 'create', 'alter', 'delete') or s.startswith('ref '):
            if s.startswith('ref '):        # ref table X: contenedor parcial
                m = RE_OBJ.match(s[4:])
                if m:
                    while pila[-1].nivel >= nivel: pila.pop()
                    n = Nodo(m['tipo'], quitar_comillas(m['nombre']), nivel); n.props['_ref'] = True
                    pila[-1].hijos.append(n); pila.append(n)
            continue
        while len(pila) > 1 and pila[-1].nivel >= nivel: pila.pop()
        padre = pila[-1]
        m = RE_OBJ.match(s)
        if m and m['tipo'] in OBJETOS:
            expr = None
            if m['expr'] is not None:
                expr, i = leer_expr(i, nivel + 1, m['expr'])
            n = Nodo(m['tipo'], quitar_comillas(m['nombre']), nivel, expr)
            if desc: n.desc = '\n'.join(desc)
            desc = []
            padre.hijos.append(n); pila.append(n)
            continue
        m = RE_OBJ_SOLO.match(s)
        if m and m['tipo'] in OBJETOS and m['tipo'] in ('linguisticMetadata', 'model', 'database'):
            expr = None
            if m['expr'] is not None:
                expr, i = leer_expr(i, nivel, m['expr'])
            n = Nodo(m['tipo'], None, nivel, expr); padre.hijos.append(n); pila.append(n); desc = []
            continue
        m = RE_PROP.match(s)
        if m:
            padre.props[m['k']] = m['v'].strip(); desc = []
            continue
        m = RE_PROP_EXPR.match(s)
        if m:
            v, i = leer_expr(i, nivel, m['v'])
            padre.props[m['k']] = v; desc = []
            continue
        padre.props[s] = True                       # bandera: isHidden, isDefault, legacyRedirects…
        desc = []
    return raiz


def _todos(n, tipo):
    for h in n.hijos:
        if h.tipo == tipo: yield h
        yield from _todos(h, tipo)


def _limpiar_m(m):
    return RE_B64.sub(lambda x: f'Binary.FromText("<datos incrustados omitidos: {len(x.group(1))} caracteres>"', m or '')


def _bool(v): return 1 if v is True or str(v).lower() == 'true' else 0


def _tipo_medida(x):
    """TMDL no guarda el tipo de dato de una medida. Se infiere si devuelve texto (lo que usa el cruce para no marcar
    «medida sin formato» en medidas de texto): FORMAT, concatenación con &, UNICHAR, CONCATENATEX, un literal "…" o un IF
    que devuelve "…" en el RETURN. [probado: 34/34 iguales al tipo que da pbixray]. Lo demás queda None."""
    if x.p('dataCategory') in ('ImageUrl', 'WebUrl'): return 'String', True
    e = re.sub(r'//[^\n]*|--[^\n]*|/\*.*?\*/', '', x.expr or '', flags=re.S)
    ret = e.rsplit('RETURN', 1)[-1] if re.search(r'\bRETURN\b', e) else e
    if (re.search(r'\bFORMAT\s*\(|"\s*&|&\s*"|\bUNICHAR\s*\(|\bCONCATENATEX?\s*\(', ret) or re.match(r'\s*"', ret)
            or re.search(r'\bIF\s*\((?:[^()]|\([^()]*\))*,\s*"[^"]*"\s*[,)]', ret)):
        return 'String', True
    return None, True


def convertir(raiz, archivo):
    tablas = list(_todos(raiz, 'table'))
    auto = lambda t: t.startswith(('LocalDateTable_', 'DateTableTemplate_'))
    col, med, tab, var, rel, ann, pq, exprs, roles = [], [], [], [], [], [], [], [], []
    for t in tablas:
        tab.append(dict(tabla=t.nombre, oculta=_bool(t.p('isHidden')), lineage_tag=t.p('lineageTag'), system_flags=None,
                        solo_variaciones=_bool(t.p('showAsVariationsOnly')), privada=_bool(t.p('isPrivate')),
                        descripcion=t.desc, parcial=bool(t.p('_ref'))))
        for c in (h for h in t.hijos if h.tipo == 'column'):
            tipo_col = 'Calculated' if c.expr else ('CalculatedTableColumn' if c.p('type') == 'calculatedTableColumn' else 'Data')
            col.append(dict(tabla=t.nombre, columna=c.nombre, formato=c.p('formatString'),
                            tipo_dato=TIPO_DATO.get(c.p('dataType'), c.p('dataType')), oculta=_bool(c.p('isHidden')),
                            resumir_por=RESUMIR.get(c.p('summarizeBy'), c.p('summarizeBy')), categoria=c.p('dataCategory'),
                            ordenar_por=quitar_comillas(c.p('sortByColumn')) if c.p('sortByColumn') else None,
                            tipo_columna=tipo_col, columna_origen=quitar_comillas(c.p('sourceColumn')) if c.p('sourceColumn') else None,
                            expresion=c.expr, lineage_tag=c.p('lineageTag'), carpeta=c.p('displayFolder'),
                            descripcion=c.desc, tabla_automatica=auto(t.nombre)))
            for v in (h for h in c.hijos if h.tipo == 'variation'):
                th, jh = ref_columna(v.p('defaultHierarchy') or '')
                var.append(dict(variacion=v.nombre, tabla=t.nombre, columna=c.nombre, es_default=_bool(v.p('isDefault')),
                                relacion=v.p('relationship'), jerarquia=jh if th else None, tabla_jerarquia=th))
            for a in (h for h in c.hijos if h.tipo == 'annotation'):
                ann.append(dict(tipo_objeto='Column', objeto=f'{t.nombre}[{c.nombre}]', nombre=a.nombre, valor=a.expr))
        for x in (h for h in t.hijos if h.tipo == 'measure'):
            td, inferido = _tipo_medida(x)
            med.append(dict(tabla=t.nombre, medida=x.nombre, formato=x.p('formatString'), tipo_dato=td,
                            tipo_dato_inferido=inferido, oculta=_bool(x.p('isHidden')), carpeta=x.p('displayFolder'),
                            descripcion=x.desc, expresion=x.expr, lineage_tag=x.p('lineageTag'), categoria=x.p('dataCategory')))
            for a in (h for h in x.hijos if h.tipo == 'annotation'):
                ann.append(dict(tipo_objeto='Measure', objeto=f'{t.nombre}[{x.nombre}]', nombre=a.nombre, valor=a.expr))
        for p in (h for h in t.hijos if h.tipo == 'partition'):
            pq.append(dict(tabla=t.nombre, particion=p.nombre, tipo=p.expr, modo=p.p('mode'),
                           expresion=_limpiar_m(p.p('source') if isinstance(p.p('source'), str) else '')))
    for r in _todos(raiz, 'relationship'):
        if not r.p('fromColumn'): continue                  # 'relationship:' dentro de una variación es propiedad
        dt, dc = ref_columna(r.p('fromColumn')); ht, hc = ref_columna(r.p('toColumn') or '')
        rel.append(dict(nombre=r.nombre, desde_tabla=dt, desde_columna=dc, hacia_tabla=ht, hacia_columna=hc,
                        activa=0 if str(r.p('isActive', 'true')).lower() == 'false' else 1,
                        cardinalidad_desde=r.p('fromCardinality', 'many'), cardinalidad_hacia=r.p('toCardinality', 'one'),
                        filtro_cruzado=r.p('crossFilteringBehavior', 'oneDirection')))
    for e in _todos(raiz, 'expression'):
        exprs.append(dict(nombre=e.nombre, expresion=_limpiar_m(e.expr), parametro='IsParameterQuery=true' in (e.expr or '')))
    for ro in _todos(raiz, 'role'):
        for tp in (h for h in ro.hijos if h.tipo == 'tablePermission'):
            roles.append(dict(rol=ro.nombre, permiso=ro.p('modelPermission'), tabla=tp.nombre, filtro=tp.expr))
    modelo = next(_todos(raiz, 'model'), None)
    return {'archivo': archivo, 'fuente': 'tmdl', 'cultura': modelo.p('culture') if modelo else None,
            'aviso': 'Foto del modelo al arrastrarlo a la vista TMDL; si el modelo cambió, vuelve a arrastrarlo.',
            'modelo': dict(columnas=col, medidas=med, tablas=tab, variaciones=var, relaciones=rel, anotaciones=ann),
            'power_query': pq, 'expresiones': exprs, 'roles': roles, 'errores': {}}


def textos_tmdl(ruta):
    """Devuelve (texto, origen). .pbix → la pestaña TMDL con el modelo completo más grande; carpeta → todos los .tmdl."""
    p = Path(ruta)
    if p.is_dir():
        fs = sorted(p.rglob('*.tmdl'))
        if not fs: raise FileNotFoundError(f'{ruta}: sin archivos .tmdl')
        return '\n'.join(f.read_text(encoding='utf-8-sig') for f in fs), f'{len(fs)} archivos .tmdl'
    if p.suffix.lower() == '.tmdl':
        return p.read_text(encoding='utf-8-sig'), p.name
    z = zipfile.ZipFile(p)
    tabs = []
    for n in z.namelist():
        if n.startswith('TMDLScripts/') and n.endswith('.tmdl'):
            t = z.read(n).decode('utf-16-le').lstrip('﻿')
            completo = re.search(r'^\t?model\s', t, re.M) is not None and re.search(r'^\t+table\s', t, re.M) is not None
            tabs.append((completo, len(t), n, t))
    completos = [x for x in tabs if x[0]]
    if not completos:
        raise LookupError('El .pbix no tiene una pestaña TMDL con el modelo completo. En Power BI Desktop: vista TMDL → '
                          'pestaña nueva (+) → arrastra «Modelo semántico» (panel Datos, pestaña Modelo) → no apliques → Ctrl+S.')
    _, _, n, t = max(completos, key=lambda x: x[1])
    from urllib.parse import unquote
    return t, f'pestaña «{unquote(n.split("/")[-1][:-5])}»'


def leer(ruta):
    texto, origen = textos_tmdl(ruta)
    r = convertir(parsear(texto), Path(ruta).name)
    r['origen_tmdl'] = origen
    return r


if __name__ == '__main__':
    from comun import ayuda; ayuda(__doc__, 2)
    *entradas, salida = sys.argv[1:]
    os.makedirs(salida, exist_ok=True)
    for e in entradas:
        r = leer(e)
        destino = Path(salida) / f'modelo_{Path(e).stem}.json'
        destino.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
        m = r['modelo']
        print(f"== {Path(e).name} ({r['origen_tmdl']}): tablas {len(m['tablas'])}, columnas {len(m['columnas'])}, "
              f"medidas {len(m['medidas'])}, relaciones {len(m['relaciones'])}, variaciones {len(m['variaciones'])}, "
              f"consultas M {len(r['power_query'])}, roles {len(r['roles'])} → {destino}")
