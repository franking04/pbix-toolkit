# EJEMPLO: construir una página en Layout clásico e inyectarla en un .pbix PBIR guardado por Power BI.
"""Genera la página 'Roadmap de ventas' con roadmap_pagina.py (formato clásico, en un temporal) y la inyecta en el mismo
reporte guardado por Power BI en PBIR, conservando el modelo con las medidas RV.
Uso: python roadmap_inyectar_pbir.py clasico.pbix guardado_pbir.pbix salida.pbix"""
import json, sys, runpy, zipfile, tempfile, os
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / 'scripts'))
from pbir import visual_layout_a_pbir, reemplazar_pagina, es_pbir

CLASICO = sys.argv[1] if len(sys.argv) > 1 else 'clasico.pbix'
GUARDADO = Path(sys.argv[2] if len(sys.argv) > 2 else 'guardado_pbir.pbix')
DESTINO = Path(sys.argv[3] if len(sys.argv) > 3 else 'salida.pbix')
tmp = Path(tempfile.gettempdir()) / '_roadmap_clasico.pbix'

sys.argv = ['x', CLASICO, str(tmp)]
runpy.run_path(str(AQUI / 'roadmap_pagina.py'), run_name='__main__')

L = json.loads(zipfile.ZipFile(tmp).read('Report/Layout').decode('utf-16-le'))
sec = next(s for s in L['sections'] if s['displayName'] == 'Roadmap de ventas')
z = zipfile.ZipFile(GUARDADO); assert es_pbir(z)
pages = json.loads(z.read('Report/definition/pages/pages.json'))
nombre = next(n for n in pages['pageOrder']
              if json.loads(z.read(f'Report/definition/pages/{n}/page.json'))['displayName'] == 'Roadmap de ventas')
viejo = json.loads(z.read(f'Report/definition/pages/{nombre}/page.json'))
cfg = json.loads(sec['config'])
page = {'$schema': viejo['$schema'], 'name': nombre, 'displayName': 'Roadmap de ventas', 'displayOption': 'FitToWidth',
        'height': sec['height'], 'width': sec['width'], 'objects': cfg['objects'],
        'visualInteractions': [{'source': r['source'], 'target': r['target'], 'type': 'NoFilter'}
                               for r in cfg.get('relationships', []) if r['type'] == 3]}
visuales = [visual_layout_a_pbir(v) for v in sec['visualContainers']]
reemplazar_pagina(str(GUARDADO), str(DESTINO), nombre, page, visuales)
os.remove(tmp)
print('página', nombre, '| visuales', len(visuales), '| ->', DESTINO.name)
