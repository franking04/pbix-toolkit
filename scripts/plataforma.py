"""Plataforma de un .pbix: Power BI Report Server (Desktop para RS, 'OnPrem') o servicio (Desktop de la nube, 'Cloud').
Uso: python plataforma.py archivo.pbix [rs:2026.05 | servicio]
Lee solo las partes Metadata y Version (quién guardó el archivo por última vez) y el formato del reporte.
Reglas de compatibilidad y releases en references/plataformas.json."""
import json, sys, zipfile, os

DATOS = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'references', 'plataformas.json'), encoding='utf-8'))

def _txt(z, n):
    b = z.read(n)
    if b[:2] == b'\xff\xfe' or (len(b) > 3 and b[1:2] == b'\x00'): return b.decode('utf-16-le').lstrip('﻿')
    return b.decode('utf-8-sig')

def detectar(ruta):
    z = zipfile.ZipFile(ruta); n = set(z.namelist())
    meta = json.loads(_txt(z, 'Metadata')) if 'Metadata' in n else {}
    origen = meta.get('CreatedFrom')
    formato = 'PBIR' if any(x.startswith('Report/definition/') for x in n) else ('Layout' if 'Report/Layout' in n else None)
    info = {'archivo': os.path.basename(ruta), 'guardado_por': {'OnPrem': 'Desktop para Report Server', 'Cloud': 'Desktop de la nube'}.get(origen, origen),
            'plataforma': {'OnPrem': 'report_server', 'Cloud': 'servicio'}.get(origen, 'desconocida'),
            'release': meta.get('CreatedFromRelease'), 'version_archivo': _txt(z, 'Version').strip() if 'Version' in n else None,
            'formato_reporte': formato, 'avisos': []}
    if info['plataforma'] == 'report_server' and formato == 'PBIR':
        info['avisos'].append('PBIR guardado por el Desktop para RS: no observado antes, revisar')
    if info['plataforma'] == 'servicio':
        info['avisos'].append('Guardado por el Desktop de la nube: no apto para Report Server sin reconstruirlo sobre un archivo del Desktop para RS')
    return info

def destino_por_defecto(info):
    """El destino natural de un archivo es la plataforma y release que lo guardó."""
    return f"rs:{info['release']}" if info['plataforma'] == 'report_server' else 'servicio'

def revisar(info, destino, tipos_visual=(), tiene_marcadores=False, visuales_personalizados=()):
    """Errores y avisos de compatibilidad para publicar en `destino` ('rs:AAAA.MM' o 'servicio')."""
    err, avisos = [], []
    if not destino or destino == 'servicio':
        return err, avisos
    rel = destino.split(':', 1)[1]
    rs = DATOS['report_server']
    if info['plataforma'] != 'report_server':
        # [observado] el Desktop para RS 2026.05 abrió un PBIR guardado por la nube 2026.09 y al «Guardar como» lo marcó
        # OnPrem 2026.05 sin cambiar el reporte (sigue en PBIR; 52/52 visuales idénticos). Antes era error («no lo abre»).
        avisos.append(f"guardado por el Desktop de la nube {info['release']}: ábrelo con el Desktop para RS {rel} y «Guardar como» "
                      f"(queda OnPrem {rel}) antes de publicar")
    elif info['release'] and info['release'] > rel:
        err.append(('archivo de un release más nuevo que el servidor', info['release'], '>', rel))
    if info['formato_reporte'] == 'PBIR':
        # el Desktop para RS 2026.05 conserva PBIR si el archivo llegó en PBIR (no lo convierte a Layout clásico) [observado]
        # [probado] publicar ese PBIR desde el Desktop para RS 2026.05 dio «Ha habido un error al intentar guardar el
        # informe en Power BI Report Server»; el control (archivo clásico, misma carpeta y usuario) subió y se ve en el portal
        (err if destino.startswith('rs') else avisos).append(
            ('formato PBIR: el Desktop para RS 2026.05 lo abre y lo guarda, pero el servidor RS 2026.05 dio error al publicarlo '
             '[probado con publicación de control]; reconstruye en Layout clásico sobre un archivo guardado por el Desktop para RS',))
    for t in sorted(set(tipos_visual)):
        if t in rs['visuales_no_soportados']:
            err.append(('visual no soportado en Report Server', t, rs['visuales_no_soportados'][t]))
        desde = rs['visuales_desde'].get(t)
        if desde and rel < desde:
            err.append(('visual disponible en Report Server desde', t, desde))
    if tiene_marcadores:
        avisos.append('el reporte tiene marcadores: comprobar que funcionan en el servidor (por validar)')
    if visuales_personalizados:
        avisos.append(f'visuales personalizados {sorted(visuales_personalizados)}: confirmar que el servidor los permite')
    if rel not in rs['releases']:
        avisos.append(f'release {rel} sin datos en references/plataformas.json: actualízalo')
    return err, avisos

if __name__ == '__main__':
    from comun import ayuda; ayuda(__doc__, 1)
    i = detectar(sys.argv[1])
    print(json.dumps(i, ensure_ascii=False, indent=1))
    if len(sys.argv) > 2:
        print(json.dumps(revisar(i, sys.argv[2]), ensure_ascii=False))
