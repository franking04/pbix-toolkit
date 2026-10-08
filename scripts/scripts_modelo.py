"""Deja los cambios de modelo LISTOS PARA EJECUTAR dentro del .pbix: el usuario solo abre la pestaña y pulsa un botón.
- Vista TMDL  (pestaña en TMDLScripts/): crear o reemplazar medidas con expresión, formato y carpeta EN UN SOLO PASO
  (createOrReplace + ref table) y formatos de medidas. Botón: Aplicar.  ← camino principal
- Vista de consultas DAX (pestaña en DAXQueries/): consultas de control (EVALUATE con conteos/totales) o, si hace falta,
  DEFINE MEASURE. Botones: Ejecutar → "Actualizar modelo con cambios".
Formato de las partes [probado: guardadas por Desktop nube 2026.09 y para RS 2026.05]: UTF-16 LE sin BOM; nombre de pestaña
con espacios como %20; índice `.pbi/tmdlScripts.json` / `.pbi/daxQueries.json` = {"version":"1.0.0","tabOrder":[...],"defaultTab":...};
[Content_Types].xml con <Default Extension="tmdl"/"dax">. Pestañas TMDL incrustadas por script: aparecen en la vista TMDL junto a las del usuario, Aplicar crea las medidas con
formato, carpeta, descripción y dataCategory (0 problemas) y la pestaña DAX de comprobación ejecuta [probado: Desktop para RS 2026.05 y Desktop de la nube 2026.09,];.
Columnas de fecha: NO generes su TMDL (necesitan su `variation`); pide arrastrar la columna al editor.

Uso:
  from scripts_modelo import incrustar, tmdl_medidas
  t = tmdl_medidas('FactVentas', [dict(nombre='Ventas netas', expr='SUM(FactVentas[Importe])', formato='\\$#,0', carpeta='KPI')])
  incrustar('base.pbix', 'base_con_scripts.pbix', tmdl={'1 Aplicar medidas': t}, dax={'2 Comprobar': 'EVALUATE ROW("n", [Ventas netas])'})
"""
import json, zipfile, urllib.parse

def _enc(s): return s.encode('utf-16-le')
def _dec(b): return b.decode('utf-16-le').lstrip('﻿')

def tmdl_medidas(tabla, medidas):
    """medidas: [{nombre, expr, formato?, carpeta?, descripcion?, categoria?}] → script TMDL createOrReplace (crea si no existe).
    categoria = dataCategory ('ImageUrl' para medidas SVG de svg_medidas.py)."""
    q = lambda n: n if n.replace('_', '').isalnum() else "'" + n.replace("'", "''") + "'"
    L = ['createOrReplace', '', f'\tref table {q(tabla)}', '']
    for m in medidas:
        if m.get('descripcion'): L.append(f"\t\t/// {m['descripcion']}")
        ex = m['expr'].strip().splitlines()
        if len(ex) == 1: L.append(f"\t\tmeasure {q(m['nombre'])} = {ex[0]}")
        else: L += [f"\t\tmeasure {q(m['nombre'])} ="] + [f'\t\t\t\t{x}' for x in ex]
        if m.get('formato'): L.append(f"\t\t\tformatString: {m['formato']}")
        if m.get('carpeta'): L.append(f"\t\t\tdisplayFolder: {m['carpeta']}")
        if m.get('categoria'): L.append(f"\t\t\tdataCategory: {m['categoria']}")   # ImageUrl para medidas SVG [probado: Desktop para RS 2026.05 y Desktop de la nube 2026.09,]
        L.append('')
    return '\n'.join(L)

def _cabecera_dax(texto):
    if 'EVALUATE' not in texto.upper():
        texto += '\nEVALUATE ROW("listo", 1)\n'          # la vista DAX exige al menos un EVALUATE para ejecutar
    return texto

def incrustar(origen, destino, tmdl=None, dax=None, por_defecto=None):
    """Agrega/reemplaza pestañas. tmdl/dax: {nombre_pestaña: texto}. No toca DataModel ni el reporte."""
    tmdl, dax = tmdl or {}, dax or {}
    zin = zipfile.ZipFile(origen); nombres = zin.namelist()
    nuevos, indices = {}, {}
    for carpeta, idx, ext, tabs in (('TMDLScripts', 'tmdlScripts.json', 'tmdl', tmdl), ('DAXQueries', 'daxQueries.json', 'dax', dax)):
        if not tabs: continue
        ruta_idx = f'{carpeta}/.pbi/{idx}'
        meta = json.loads(_dec(zin.read(ruta_idx))) if ruta_idx in nombres else {'version': '1.0.0', 'tabOrder': [], 'defaultTab': None}
        for nombre, texto in tabs.items():
            if ext == 'dax': texto = _cabecera_dax(texto)
            nuevos[f'{carpeta}/{urllib.parse.quote(nombre)}.{ext}'] = _enc(texto)
            if nombre not in meta['tabOrder']: meta['tabOrder'].append(nombre)
        meta['defaultTab'] = por_defecto if por_defecto in tabs else next(iter(tabs))
        indices[ruta_idx] = _enc(json.dumps(meta, ensure_ascii=False, separators=(',', ':')))
    reemplazos = {**nuevos, **indices}
    with zipfile.ZipFile(destino, 'w') as zout:
        for info in zin.infolist():
            n = info.filename
            if n in reemplazos or n == 'SecurityBindings': continue
            data = zin.read(n)
            if n == '[Content_Types].xml':
                t = data.decode('utf-8-sig').replace('<Override PartName="/SecurityBindings" ContentType="" />', '')
                for e in ('tmdl', 'dax'):
                    if f'Extension="{e}"' not in t: t = t.replace('<Override ', f'<Default Extension="{e}" ContentType="" /><Override ', 1)
                data = ('﻿' + t).encode('utf-8') if data.startswith(b'\xef\xbb\xbf') else t.encode('utf-8')
            zi = zipfile.ZipInfo(n, date_time=info.date_time); zi.compress_type = info.compress_type; zi.external_attr = info.external_attr
            zout.writestr(zi, data)
        for n, data in reemplazos.items():
            zi = zipfile.ZipInfo(n, date_time=zin.getinfo(nombres[0]).date_time); zi.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(zi, data)
    return sorted(reemplazos)

if __name__ == '__main__':
    import sys
    print(__doc__)
