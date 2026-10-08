# EJEMPLO: el mismo rediseño de rediseno_dos_versiones.py, para Report Server en Layout clásico.
"""Rediseño para Power BI Report Server: misma estructura y diseño que rediseno_dos_versiones.py, pero en Layout clásico
sobre un archivo guardado por el Desktop para Report Server (sin pasar por PBIR ni por el Desktop de la nube).
Uso: python rediseno_report_server.py base_rs.pbix [marca|corporativo ...]
  base_rs = archivo guardado por el Desktop para RS que YA tenga las medidas RV. Salida: salida_rs_<versión>.pbix"""
import sys, json
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / 'scripts')); sys.path.insert(0, str(AQUI))
sys.dont_write_bytecode = True
import rediseno_dos_versiones as V                    # portada(), inventario(), roadmap(), VERSIONES, ID, tema
from modificar_layout import Pbix
from plataforma import detectar

def construir_rs(version, base):
    info = detectar(str(base))
    if info['plataforma'] != 'report_server' or info['formato_reporte'] != 'Layout':
        raise SystemExit(f'La base debe ser un archivo guardado por el Desktop para Report Server: {info}')
    T = V.VERSIONES[version]
    p = Pbix(str(base))
    V.portada(p, T, version); V.inventario(p, T); V.roadmap(p, T)
    p.ordenar_paginas([V.ID['portada'], V.ID['roadmap'], V.ID['inventario'], V.ID['html']], activa=V.ID['portada'])
    for k in ('portada', 'roadmap', 'inventario'): p.ocultar_pagina(V.ID[k], False)
    p.ocultar_pagina(V.ID['html'], True)
    p.vista_pagina(V.ID['roadmap'], 'FitToWidth')
    nombre_tema = 'marca_demo.json' if version == 'marca' else 'corporativo.json'
    p.tema_personalizado(V.tema('Tema ' + ('Marca Demo' if version == 'marca' else 'corporativo'), T), nombre_tema)
    destino = Path(f'salida_rs_{version}.pbix')
    p.guardar(str(destino))
    print(version, '->', destino.name, f"(base {base.name}: {info['guardado_por']} {info['release']})")
    return destino

if __name__ == '__main__':
    args = sys.argv[1:]
    base = Path(args.pop(0) if args and args[0].endswith('.pbix') else 'base_rs.pbix')
    for v in (args or ['marca', 'corporativo']): construir_rs(v, base)
