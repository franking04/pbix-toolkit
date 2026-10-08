"""Inventario del ZIP de un .pbix/.pbit: partes, tamaños, codificación y formato del reporte.
Solo lee metadatos; DataModel se inspecciona por encabezado, nunca se descomprime aquí.
Uso: python inspeccionar_pbix.py archivo.pbix"""
import json, sys, zipfile, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def detectar_codificacion(head: bytes) -> str:
    if head.startswith(b'\xef\xbb\xbf'): return 'utf-8-bom'
    if head.startswith(b'\xff\xfe'): return 'utf-16-le-bom'
    if len(head) > 3 and head[1:2] == b'\x00' and head[3:4] == b'\x00': return 'utf-16-le'
    if head.startswith(b'PK\x03\x04'): return 'zip'
    if head.startswith(b'\x89PNG') or head.startswith(b'\xff\xd8'): return 'imagen'
    try: head.decode('utf-8'); return 'utf-8'
    except UnicodeDecodeError: return 'binario'

def leer_texto(z, nombre):
    b = z.read(nombre)
    enc = detectar_codificacion(b[:16])
    if enc == 'utf-8-bom': return b[3:].decode('utf-8')
    if enc.startswith('utf-16'): return b.decode('utf-16-le').lstrip('﻿')
    return b.decode('utf-8')

def inspeccionar(ruta):
    z = zipfile.ZipFile(ruta)
    nombres = z.namelist()
    partes = []
    for i in z.infolist():
        with z.open(i) as h: head = h.read(64)
        enc = detectar_codificacion(head)
        p = {'parte': i.filename, 'bytes': i.file_size, 'bytes_comprimido': i.compress_size,
             'metodo_zip': 'stored' if i.compress_type == 0 else 'deflate', 'codificacion': enc}
        if i.filename == 'DataModel':
            txt = head.decode('utf-16-le', errors='ignore')
            p['encabezado'] = txt.split('.')[0] + '.' if 'XPress9' in txt else head[:20].hex()
        partes.append(p)
    pbir = any(n.startswith('Report/definition/') for n in nombres)
    formato = 'PBIR (Report/definition/)' if pbir else ('Layout clásico (Report/Layout)' if 'Report/Layout' in nombres else 'sin reporte')
    info = {'archivo': os.path.basename(ruta), 'bytes': os.path.getsize(ruta), 'formato_reporte': formato,
            'tiene': {k: (k in nombres) for k in ['Report/Layout', 'DataModel', 'DataModelSchema', 'DataMashup',
                      'Connections', 'DiagramLayout', 'Report/LinguisticSchema', 'SecurityBindings', 'Settings', 'Metadata']},
            'version': leer_texto(z, 'Version') if 'Version' in nombres else None,
            'metadata': json.loads(leer_texto(z, 'Metadata')) if 'Metadata' in nombres else None,
            'settings': json.loads(leer_texto(z, 'Settings')) if 'Settings' in nombres else None,
            'connections': json.loads(leer_texto(z, 'Connections')) if 'Connections' in nombres else None,
            'custom_visuals': sorted({n.split('/')[2] for n in nombres if n.startswith('Report/CustomVisuals/')}),
            'dax_queries': [n for n in nombres if n.startswith('DAXQueries/') and n.endswith('.dax')],
            'pbir': ({'paginas': len([n for n in nombres if n.endswith('/page.json')]),
                      'visuales': len([n for n in nombres if n.endswith('/visual.json')]),
                      'bookmarks': len([n for n in nombres if '/bookmarks/' in n and n.endswith('.json')]),
                      'report_extensions': 'Report/definition/reportExtensions.json' in nombres} if pbir else None),
            'partes': partes}
    try:
        from plataforma import detectar
        info['plataforma'] = {k: v for k, v in detectar(ruta).items() if k != 'archivo'}
    except Exception as e:
        info['plataforma'] = {'error': str(e)}
    return info

if __name__ == '__main__':
    from comun import ayuda; ayuda(__doc__, 1)
    print(json.dumps(inspeccionar(sys.argv[1]), ensure_ascii=False, indent=1))
