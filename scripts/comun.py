"""Utilidades comunes: decodificación de partes del .pbix y resolución de expresiones del lenguaje
semántico de Power BI (campos, agregaciones, jerarquías, filtros). Probado con Layout clásico y PBIR."""
import json, collections

def decodificar(b: bytes) -> str:
    """Las partes JSON del Layout clásico van en UTF-16 LE (sin BOM); las de PBIR en UTF-8."""
    if b[:3] == b'\xef\xbb\xbf': return b[3:].decode('utf-8')
    if b[:2] in (b'\xff\xfe', b'\xfe\xff'): return b.decode('utf-16')
    if len(b) > 1 and b[1:2] == b'\x00': return b.decode('utf-16-le')
    return b.decode('utf-8')

def leer_json(z, nombre):
    return json.loads(decodificar(z.read(nombre)))

def formato_reporte(z):
    n = z.namelist()
    if any(x.startswith('Report/definition/') for x in n): return 'PBIR'
    if 'Report/Layout' in n: return 'Layout'
    return None

AGG = {0: 'Sum', 1: 'Avg', 2: 'DistinctCount', 3: 'Min', 4: 'Max', 5: 'Count', 6: 'Median',
       7: 'StandardDeviation', 8: 'Variance'}
CMP = {0: '=', 1: '>', 2: '>=', 3: '<', 4: '<=', 5: '<>'}
ARIT = {0: '+', 1: '-', 2: '*', 3: '/'}
DESCONOCIDOS = collections.Counter()   # nodos de expresión no reconocidos -> casos nuevos

def jload(s, default=None):
    if s is None or s == '': return default
    return json.loads(s) if isinstance(s, str) else s

def leer_layout(z):
    b = z.read('Report/Layout')
    t = b.decode('utf-16-le') if b[1:2] == b'\x00' else b.decode('utf-8-sig')
    return json.loads(t.lstrip('﻿'))

# ---------- resolución de expresiones ----------
def tabla_de(src, alias):
    sr = src.get('SourceRef', {})
    if 'Entity' in sr: return sr['Entity']
    if 'Source' in sr: return alias.get(sr['Source'], '?alias:' + sr['Source'])
    DESCONOCIDOS['SourceRef sin Entity/Source'] += 1
    return '?'

def resolver(e, alias):
    """Devuelve (texto, [campos_base]). Cada campo base: dict(tabla, campo, tipo, extra)."""
    if e is None: return ('', [])
    if 'Column' in e:
        c = e['Column']; t = tabla_de(c['Expression'], alias)
        return (f"{t}[{c['Property']}]", [dict(tabla=t, campo=c['Property'], tipo='Column')])
    if 'Measure' in e:
        m = e['Measure']; t = tabla_de(m['Expression'], alias)
        return (f"{t}[{m['Property']}]", [dict(tabla=t, campo=m['Property'], tipo='Measure')])
    if 'HierarchyLevel' in e:
        hl = e['HierarchyLevel']; h = hl['Expression']['Hierarchy']; inner = h['Expression']
        if 'PropertyVariationSource' in inner:      # jerarquía automática de fecha
            pvs = inner['PropertyVariationSource']; t = tabla_de(pvs['Expression'], alias)
            col = pvs['Property']
            return (f"{t}[{col}].{h['Hierarchy']}.{hl['Level']}",
                    [dict(tabla=t, campo=col, tipo='Column', extra=f"jerarquía fecha {h['Hierarchy']}.{hl['Level']}")])
        t = tabla_de(inner, alias)                   # jerarquía de usuario
        return (f"{t}.{h['Hierarchy']}.{hl['Level']}",
                [dict(tabla=t, campo=hl['Level'], tipo='HierarchyLevel', extra=f"jerarquía {h['Hierarchy']}")])
    if 'Aggregation' in e:
        a = e['Aggregation']; txt, base = resolver(a['Expression'], alias)
        f = AGG.get(a['Function'], f"Func{a['Function']}")
        for x in base: x['extra'] = (x.get('extra', '') + f' agg={f}').strip()
        return (f"{f}({txt})", base)
    if 'Arithmetic' in e:
        a = e['Arithmetic']; lt, lb = resolver(a['Left'], alias); rt, rb = resolver(a['Right'], alias)
        return (f"({lt} {ARIT.get(a['Operator'], '?')} {rt})", lb + rb)
    if 'ScopedEval' in e:
        s = e['ScopedEval']; txt, base = resolver(s['Expression'], alias)
        return (f"ScopedEval({txt}, scope={len(s.get('Scope', []))})", base)
    if 'SparklineData' in e:
        s = e['SparklineData']; txt, base = resolver(s['Measure'], alias)
        g = [resolver(x, alias) for x in s.get('Groupings', [])]
        for _, gb in g:
            for x in gb: x['extra'] = (x.get('extra', '') + ' sparkline-grouping').strip()
        return (f"Sparkline({txt} por {', '.join(t for t, _ in g)})", base + [x for _, gb in g for x in gb])
    if 'GroupRef' in e:                              # agrupación/bins definidos en el reporte
        g = e['GroupRef']; t = tabla_de(g['Expression'], alias)
        cols = [resolver(x, alias)[0] for x in g.get('GroupedColumns', [])]
        return (f"{t}[{g['Property']}]", [dict(tabla=t, campo=g['Property'], tipo='GroupColumn',
                                               extra='agrupa ' + ', '.join(cols))])
    if 'Literal' in e: return (str(e['Literal'].get('Value')), [])
    if 'SourceRef' in e: return (tabla_de(e, alias), [])
    for k in ('Hierarchy',):
        if k in e: return resolver({'HierarchyLevel': {'Expression': e, 'Level': '?'}}, alias)
    k = next(iter(e), '?'); DESCONOCIDOS['expr:' + k] += 1
    return (f'?{k}', [])

def literal(v):
    v = str(v)
    if v.startswith("'") and v.endswith("'"): return v[1:-1].replace("''", "'")
    if v.startswith('datetime'): return v[9:-1]
    if v[-1:] in 'LDM' and v[:-1].replace('.', '', 1).lstrip('-').isdigit(): return v[:-1]
    return v

def condicion(c, alias):
    if c is None: return ''
    if 'In' in c:
        i = c['In']; cols = [resolver(x, alias)[0] for x in i['Expressions']]
        if 'Values' in i:
            vals = [' & '.join(literal(x['Literal']['Value']) if 'Literal' in x else '?' for x in fila) for fila in i['Values']]
            return f"{', '.join(cols)} IN ({'; '.join(vals)})"
        if 'Table' in i: return f"{', '.join(cols)} IN tabla({tabla_de(i['Table'], alias)})"
    if 'Not' in c: return f"NOT ({condicion(c['Not']['Expression'], alias)})"
    if 'And' in c: return f"({condicion(c['And']['Left'], alias)}) AND ({condicion(c['And']['Right'], alias)})"
    if 'Or' in c: return f"({condicion(c['Or']['Left'], alias)}) OR ({condicion(c['Or']['Right'], alias)})"
    if 'Comparison' in c:
        k = c['Comparison']; return f"{expr_val(k['Left'], alias)} {CMP.get(k['ComparisonKind'], '?')} {expr_val(k['Right'], alias)}"
    for op in ('Contains', 'StartsWith', 'EndsWith', 'DoesNotContain', 'DoesNotStartWith'):
        if op in c: return f"{expr_val(c[op]['Left'], alias)} {op} {expr_val(c[op]['Right'], alias)}"
    if 'Between' in c:
        b = c['Between']; return f"{expr_val(b['Expression'], alias)} BETWEEN {expr_val(b['LowerBound'], alias)} AND {expr_val(b['UpperBound'], alias)}"
    if 'Exists' in c: return f"EXISTS({tabla_de(c['Exists']['Expression'], alias)})"
    k = next(iter(c), '?'); DESCONOCIDOS['cond:' + k] += 1
    return f'?{k}'

def expr_val(e, alias):
    if 'Literal' in e: return literal(e['Literal']['Value'])
    if 'DateSpan' in e: return f"DateSpan({expr_val(e['DateSpan']['Expression'], alias)}, unidad={e['DateSpan'].get('TimeUnit')})"
    if 'DateAdd' in e: d = e['DateAdd']; return f"DateAdd({expr_val(d['Expression'], alias)}, {d.get('Amount')}, unidad={d.get('TimeUnit')})"
    if 'Now' in e: return 'Now()'
    return resolver(e, alias)[0]

def leer_filtros(lista, ambito, pagina, visual_id, salida):
    for f in (jload(lista, []) if isinstance(lista, str) else (lista or [])):
        q = f.get('filter') or {}
        alias = {x['Name']: x.get('Entity', '?') for x in q.get('From', [])}
        expr = f.get('expression') or f.get('field')          # Layout clásico: expression | PBIR: field
        campo_txt, base = resolver(expr, {}) if expr else ('', [])
        conds = [condicion(w.get('Condition'), alias) for w in q.get('Where', [])]
        salida.append(dict(ambito=ambito, pagina=pagina, visual_id=visual_id, nombre=f.get('name'),
                           tipo=f.get('type'), how_created=f.get('howCreated'),
                           campo=campo_txt, tabla=base[0]['tabla'] if base else '',
                           oculto=bool(f.get('isHiddenInViewMode')), bloqueado=bool(f.get('isLockedInViewMode')),
                           activo=bool(conds), condicion=' AND '.join(conds)))


def ayuda(doc, minimo=1):
    """Para el bloque __main__ de cada script: con -h/--help, o si faltan argumentos, muestra el docstring y termina.
    También revisa que cada .pbix/.pbit indicado exista y sea un zip, con un mensaje claro en vez de un error de Python."""
    import os, sys, zipfile
    args = sys.argv[1:]
    if any(a in ('-h', '--help') for a in args):
        print((doc or '').strip()); sys.exit(0)
    pos = [a for a in args if not a.startswith('-')]
    if len(pos) < minimo:
        print((doc or '').strip()); print(f'\nFaltan argumentos: se esperan al menos {minimo}.', file=sys.stderr); sys.exit(2)
    for a in pos:
        if a.lower().endswith(('.pbix', '.pbit')):
            if not os.path.exists(a): continue
            if not zipfile.is_zipfile(a):
                print(f'«{a}» no es un .pbix válido (no es un archivo zip).', file=sys.stderr); sys.exit(2)

if __name__ == '__main__':
    print(__doc__.strip()); print('\n(módulo: se importa desde Python; ver SKILL.md)')
