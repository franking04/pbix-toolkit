"""Lee el modelo semántico de uno o varios .pbix. Dos caminos (misma salida para el resto de la skill):
  * pbixray  — descomprime el DataModel (XPress9) y consulta su SQLite: modelo ACTUAL, sin pasos del usuario.
               Necesita `pip install pbixray` (Windows, o cualquier entorno cuya red permita pypi.org y
               files.pythonhosted.org). Probado con pbixray 0.15.5.
  * tmdl     — lee el TMDL que el propio Power BI escribe (pestaña de la vista TMDL con el modelo arrastrado, o carpeta
               .pbip): sin dependencias ni red; es una foto del modelo (ver leer_modelo_tmdl.py).
Por defecto (--fuente auto) usa pbixray si está instalado y, si no, TMDL; si no hay ninguno, explica qué hacer.
Solo metadatos: NUNCA llama a get_table/iter_table.
Uso: python leer_modelo.py archivo.pbix [más.pbix ...] carpeta_salida [--fuente auto|pbixray|tmdl]
Salida: <carpeta_salida>/modelo_<archivo>.json  (pbixray: clave 'sqlite'; tmdl: clave 'modelo'; los lectores aceptan ambas)"""
import json, sys, os, traceback
from pathlib import Path
from importlib import metadata as md
try:
    from pbixray import PBIXRay
except ImportError:          # sin pbixray: se usa el camino TMDL
    PBIXRay = None
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TIPO_DATO = {1: 'Automatic', 2: 'String', 6: 'Int64', 8: 'Double', 9: 'DateTime', 10: 'Decimal', 11: 'Boolean',
             17: 'Binary', 19: 'Unknown', 20: 'Variant'}
RESUMIR = {1: 'Default', 2: 'None', 3: 'Sum', 4: 'Min', 5: 'Max', 6: 'Count', 7: 'Average', 8: 'DistinctCount'}
TIPO_COL = {1: 'Data', 2: 'Calculated', 3: 'RowNumber', 4: 'CalculatedTableColumn'}
TIPO_OBJ = {3: 'Table', 4: 'Column', 8: 'Measure', 9: 'Hierarchy', 7: 'Relationship', 1: 'Model'}
ATRIBUTOS = ['tables', 'metadata', 'schema', 'dax_measures', 'dax_columns', 'dax_tables', 'relationships',
             'power_query', 'm_parameters', 'rls', 'statistics', 'size']

def a_json(v):
    if hasattr(v, 'to_dict'):
        try: return v.to_dict(orient='records')
        except TypeError: return v.to_dict()
    if hasattr(v, 'tolist'): return v.tolist()
    return v

def conexion(modelo):
    """Ruta interna (pbixray 0.15.5): PBIXRay._metadata._meta._db.conn -> apsw.Connection en memoria."""
    return modelo._metadata._meta._db.conn

def filas(con, sql):
    cur = con.cursor(); cur.execute(sql)
    nombres = [d[0] for d in cur.getdescription()]
    return [dict(zip(nombres, r)) for r in cur]

def cols_de(con, tabla):
    return {r['name'] for r in filas(con, f'PRAGMA table_info([{tabla}])')}

def opt(con, tabla, alias, col, como=None):
    return f'{alias}.[{col}] AS [{como or col}]' if col in cols_de(con, tabla) else f'NULL AS [{como or col}]'

def consultas(con):
    sys_ok = 'SystemFlags' in cols_de(con, 'Table')
    usuario = 't.SystemFlags = 0' if sys_ok else '1=1'
    q = {}
    q['columnas'] = f"""SELECT c.ID AS id, t.Name AS tabla, COALESCE(c.ExplicitName, c.InferredName) AS columna,
        {opt(con,'Column','c','FormatString','formato')}, COALESCE(c.ExplicitDataType, c.InferredDataType) AS tipo_dato,
        {opt(con,'Column','c','IsHidden','oculta')}, {opt(con,'Column','c','SummarizeBy','resumir_por')},
        {opt(con,'Column','c','DataCategory','categoria')}, sc.ExplicitName AS ordenar_por,
        {opt(con,'Column','c','Type','tipo_columna')}, {opt(con,'Column','c','SourceColumn','columna_origen')},
        {opt(con,'Column','c','Expression','expresion')}, {opt(con,'Column','c','LineageTag','lineage_tag')},
        {opt(con,'Column','c','DisplayFolder','carpeta')}, {opt(con,'Column','c','Description','descripcion')}
        FROM [Column] c JOIN [Table] t ON c.TableID = t.ID LEFT JOIN [Column] sc ON c.SortByColumnID = sc.ID
        WHERE {usuario}"""
    q['medidas'] = f"""SELECT m.ID AS id, t.Name AS tabla, m.Name AS medida, {opt(con,'Measure','m','FormatString','formato')},
        {opt(con,'Measure','m','DataType','tipo_dato')}, {opt(con,'Measure','m','IsHidden','oculta')},
        {opt(con,'Measure','m','DisplayFolder','carpeta')}, {opt(con,'Measure','m','Description','descripcion')},
        m.Expression AS expresion, {opt(con,'Measure','m','LineageTag','lineage_tag')}
        FROM [Measure] m JOIN [Table] t ON m.TableID = t.ID"""
    q['tablas'] = f"""SELECT t.ID AS id, t.Name AS tabla, {opt(con,'Table','t','IsHidden','oculta')},
        {opt(con,'Table','t','LineageTag','lineage_tag')}, {opt(con,'Table','t','SystemFlags','system_flags')},
        {opt(con,'Table','t','ShowAsVariationsOnly','solo_variaciones')}, {opt(con,'Table','t','IsPrivate','privada')}
        FROM [Table] t"""
    q['variaciones'] = """SELECT v.Name AS variacion, tc.Name AS tabla, c.ExplicitName AS columna, v.IsDefault AS es_default,
        r.Name AS relacion, h.Name AS jerarquia, th.Name AS tabla_jerarquia
        FROM [Variation] v JOIN [Column] c ON v.ColumnID = c.ID JOIN [Table] tc ON c.TableID = tc.ID
        LEFT JOIN [Relationship] r ON v.RelationshipID = r.ID LEFT JOIN [Hierarchy] h ON v.DefaultHierarchyID = h.ID
        LEFT JOIN [Table] th ON h.TableID = th.ID"""
    q['relaciones'] = """SELECT r.Name AS nombre, tf.Name AS desde_tabla, cf.ExplicitName AS desde_columna,
        tt.Name AS hacia_tabla, ct.ExplicitName AS hacia_columna, r.IsActive AS activa
        FROM [Relationship] r JOIN [Table] tf ON r.FromTableID = tf.ID JOIN [Column] cf ON r.FromColumnID = cf.ID
        JOIN [Table] tt ON r.ToTableID = tt.ID JOIN [Column] ct ON r.ToColumnID = ct.ID"""
    q['anotaciones'] = """SELECT a.ObjectType AS tipo_objeto, a.ObjectID AS id_objeto, a.Name AS nombre, a.Value AS valor
        FROM [Annotation] a WHERE a.ObjectType IN (4, 8)"""
    return q

def procesar(pbix):
    res = {'archivo': Path(pbix).name, 'pbixray_version': md.version('pbixray'), 'pbixray': {}, 'sqlite': {}, 'errores': {}}
    m = PBIXRay(str(pbix))
    for a in ATRIBUTOS:
        try: res['pbixray'][a] = a_json(getattr(m, a))
        except Exception as e: res['errores'][a] = f'{type(e).__name__}: {e}'
    try:
        con = conexion(m)
        for k, sql in consultas(con).items():
            try: res['sqlite'][k] = filas(con, sql)
            except Exception as e: res['errores']['sqlite.' + k] = f'{type(e).__name__}: {e}'
    except Exception as e:
        res['errores']['sqlite'] = ''.join(traceback.format_exception_only(type(e), e)).strip()
    s = res['sqlite']
    for x in s.get('columnas', []):
        x['tipo_dato'] = TIPO_DATO.get(x['tipo_dato'], x['tipo_dato'])
        x['resumir_por'] = RESUMIR.get(x['resumir_por'], x['resumir_por'])
        x['tipo_columna'] = TIPO_COL.get(x['tipo_columna'], x['tipo_columna'])
        x['tabla_automatica'] = x['tabla'].startswith(('LocalDateTable_', 'DateTableTemplate_'))
    for x in s.get('medidas', []): x['tipo_dato'] = TIPO_DATO.get(x['tipo_dato'], x['tipo_dato'])
    for x in s.get('anotaciones', []): x['tipo_objeto'] = TIPO_OBJ.get(x['tipo_objeto'], x['tipo_objeto'])
    s['columnas'] = [c for c in s.get('columnas', []) if c['tipo_columna'] != 'RowNumber']
    return res

def leer(f, fuente='auto'):
    """Devuelve el dict del modelo por la fuente pedida. auto = pbixray si está instalado, si no TMDL."""
    if fuente == 'pbixray' or (fuente == 'auto' and PBIXRay is not None):
        if PBIXRay is None:
            raise SystemExit('pbixray no está instalado. Prueba: pip install pbixray (si la red lo bloquea, repórtalo; no lo '
                             'rodees) o usa --fuente tmdl.')
        return procesar(f)
    import leer_modelo_tmdl
    try:
        return leer_modelo_tmdl.leer(f)
    except LookupError as e:
        raise SystemExit(f'{Path(f).name}: sin pbixray y sin TMDL del modelo. {e}')

if __name__ == '__main__':
    from comun import ayuda; ayuda(__doc__, 2)
    args = sys.argv[1:]; fuente = 'auto'
    if '--fuente' in args:
        i = args.index('--fuente'); fuente = args[i + 1]; del args[i:i + 2]
    *archivos, salida = args
    os.makedirs(salida, exist_ok=True)
    for f in archivos:
        print(f'== {Path(f).name}')
        r = leer(f, fuente)
        if r.get('fuente') == 'tmdl':
            destino = Path(salida) / f'modelo_{Path(f).stem}.json'
            destino.write_text(json.dumps(r, ensure_ascii=False, indent=1, default=str), encoding='utf-8')
            m = r['modelo']
            print(f"   [TMDL, {r['origen_tmdl']}] columnas {len(m['columnas'])}, medidas {len(m['medidas'])}, "
                  f"relaciones {len(m['relaciones'])}, consultas M {len(r['power_query'])} -> {destino}")
            continue
        destino = Path(salida) / f'modelo_{Path(f).stem}.json'
        destino.write_text(json.dumps(r, ensure_ascii=False, indent=1, default=str), encoding='utf-8')
        s = r['sqlite']
        print(f"   columnas {len(s.get('columnas', []))}, medidas {len(s.get('medidas', []))}, "
              f"variaciones {len(s.get('variaciones', []))}, relaciones {len(s.get('relaciones', []))}, "
              f"errores {len(r['errores'])} -> {destino.name}")
        for k, v in r['errores'].items(): print(f'   ERROR {k}: {v}')
