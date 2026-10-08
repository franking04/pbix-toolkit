"""Cruza la salida de leer_reporte.py con la de leer_modelo.py: referencias rotas, objetos del modelo sin uso
y alertas de formato antes de construir o modificar visuales.
Uso: python cruzar_reporte_modelo.py carpeta_reporte modelo_<archivo>.json carpeta_salida"""
import csv, json, os, sys, collections

def leer_csv(d, n):
    p = os.path.join(d, n + '.csv')
    return list(csv.DictReader(open(p, encoding='utf-8-sig'))) if os.path.exists(p) else []

ROLES_CATEGORIA = {'Category', 'Rows', 'Columns', 'Axis', 'Series', 'Legend'}
FECHA_LARGA = {'Long Date', 'General Date', 'Long Time'}
PISTAS_PORCENTAJE = ('%', 'margen', 'var ', 'variación', 'variacion', 'cumplimiento', 'ratio', 'tasa')
PISTAS_MES = ('mes', 'month', 'nombremes')
PISTAS_NUMERO = ('saldo', 'costo', 'valor', 'precio', 'cantidad', 'monto', 'importe', 'total', 'unidades', 'promedio', 'amount', 'price', 'qty')
AGREGACIONES_NUMERICAS = ('Sum(', 'Avg(', 'Median(')    # Min/Max sobre texto es legítimo (primer código)

def cruzar(dir_rep, ruta_modelo, salida):
    refs = leer_csv(dir_rep, 'referencias'); fmt = leer_csv(dir_rep, 'formato')
    d = json.load(open(ruta_modelo, encoding='utf-8')); m = d.get('modelo') or d['sqlite']   # TMDL ('modelo') o pbixray ('sqlite')
    cols = {(c['tabla'], c['columna']): c for c in m.get('columnas', [])}
    meds = {(x['tabla'], x['medida']): x for x in m.get('medidas', [])}
    hallazgos = []
    def h(tipo, severidad, objeto, detalle, donde=''):
        hallazgos.append(dict(tipo=tipo, severidad=severidad, objeto=objeto, detalle=detalle, donde=donde))

    # 1. Referencias rotas (proyecciones y formato condicional)
    usados = collections.defaultdict(set)
    for origen, filas_ in (('proyección', refs), ('formato', fmt)):
        for r in filas_:
            k = (r['tabla'], r['campo']); usados[k].add(f"{r['pagina']} / {r.get('rol') or r.get('propiedad')}")
            existe = (k in meds) if r['tipo_campo'] == 'Measure' else (k in cols)
            if not existe and r['tipo_campo'] != 'HierarchyLevel':
                h('referencia_rota', 'alta', f'{k[0]}[{k[1]}]', f'{r["tipo_campo"]} usado en {origen} y ausente del modelo',
                  f"{r['pagina']} · {r['visual_id']}")
    # 2. Objetos del modelo sin uso en el reporte
    textos_dax = ' '.join((x.get('expresion') or '') for x in meds.values()) + ' ' + \
                 ' '.join((c.get('expresion') or '') for c in cols.values())
    for k, x in meds.items():
        if k in usados: continue
        if f'[{k[1]}]' in textos_dax:
            h('medida_intermedia', 'info', f'{k[0]}[{k[1]}]', 'no está en visuales, pero otras medidas o columnas la usan')
        else:
            h('medida_sin_uso', 'info', f'{k[0]}[{k[1]}]', 'no aparece en visuales, formato ni en otras expresiones DAX')
    tablas_usadas = {k[0] for k in usados}
    for t in sorted({c['tabla'] for c in cols.values() if not c['tabla_automatica']} - tablas_usadas):
        h('tabla_sin_uso', 'info', t, 'ninguna columna o medida de la tabla se usa en el reporte')
    # 3. Alertas de formato sobre lo que el reporte usa
    for r in refs:
        k = (r['tabla'], r['campo'])
        if r['tipo_campo'] == 'Measure' and k in meds:
            x = meds[k]
            if not x['formato'] and x['tipo_dato'] not in ('String',):
                sev = 'media' if any(p in k[1].lower() for p in PISTAS_PORCENTAJE) else 'baja'
                h('medida_sin_formato', sev, f'{k[0]}[{k[1]}]', f"tipo {x['tipo_dato']} sin formato" +
                  (' (el nombre sugiere porcentaje)' if sev == 'media' else ''), r['pagina'])
        elif k in cols:
            c = cols[k]
            if c['tipo_dato'] == 'DateTime' and r['rol'] in ROLES_CATEGORIA and (c['formato'] in FECHA_LARGA or not c['formato']):
                h('fecha_larga_en_eje', 'media', f'{k[0]}[{k[1]}]', f"formato '{c['formato']}' en rol {r['rol']}", r['pagina'])
            if c['tipo_dato'] == 'String' and any(p in k[1].lower() for p in PISTAS_MES) and not c['ordenar_por']:
                h('texto_mes_sin_orden', 'media', f'{k[0]}[{k[1]}]', 'texto de mes sin "ordenar por": saldrá alfabético', r['pagina'])
            if c['tipo_dato'] in ('Double', 'Decimal') and not c['formato'] and r['tipo_campo'] != 'HierarchyLevel':
                h('columna_sin_formato', 'baja', f'{k[0]}[{k[1]}]', f"{c['tipo_dato']} sin formato", r['pagina'])
            # número guardado como texto [probado: columnas de saldo y costo tipadas como texto salían crudas]
            if c['tipo_dato'] == 'String' and r['rol'] not in ROLES_CATEGORIA and r['tipo_campo'] != 'HierarchyLevel':
                agregada = (r.get('query_ref') or '').startswith(AGREGACIONES_NUMERICAS)
                nombre = any(p in k[1].lower() for p in PISTAS_NUMERO)
                if agregada or nombre:
                    h('numero_como_texto', 'media', f'{k[0]}[{k[1]}]',
                      'columna de texto ' + ('con agregación numérica' if agregada else 'con nombre numérico') +
                      f" en rol {r['rol']}: sale sin formato y no suma. Tipa en Power Query con cultura explícita; sin acceso al "
                      'origen, columna calculada con parseo independiente de la cultura [por validar]', r['pagina'])
    # sin duplicados
    unicos = list({(x['tipo'], x['objeto'], x['detalle']): x for x in hallazgos}.values())
    os.makedirs(salida, exist_ok=True)
    with open(os.path.join(salida, 'hallazgos.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=['tipo', 'severidad', 'objeto', 'detalle', 'donde']); w.writeheader(); w.writerows(unicos)
    resumen = dict(collections.Counter(x['tipo'] for x in unicos))
    json.dump(resumen, open(os.path.join(salida, 'hallazgos_resumen.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return resumen, unicos

if __name__ == '__main__':
    from comun import ayuda; ayuda(__doc__, 3)
    r, u = cruzar(*sys.argv[1:4])
    print(json.dumps(r, ensure_ascii=False, indent=1))
    for x in u:
        if x['severidad'] in ('alta', 'media'): print(f"[{x['severidad']}] {x['tipo']}: {x['objeto']} — {x['detalle']}")
