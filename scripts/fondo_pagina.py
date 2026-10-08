"""Fondo de página por capas (nivel de impacto «impactante»).

La capa de decoración del diseño HTML (degradados, brillos, paneles tipo vidrio, sombras, formas) se exporta como imagen
con `capas_html.js` y se pone como imagen de fondo de la página; los visuales nativos van encima con fondo transparente
(el tema de las direcciones de 2 capas ya los deja transparentes). Así Power BI muestra efectos que no tiene de forma nativa
sin perder interactividad: los datos siguen siendo visuales reales.

Estructura usada (copiada de archivos guardados por Power BI Desktop):
  * Clásico [probado]: Layout.resourcePackages → RegisteredResources (type 1) item {type: 100, path, name};
    sección.config.objects.background = [{properties: {image: {image: {name, url: ResourcePackageItem, scaling}}, transparency}}].
  * PBIR [probado]: report.json resourcePackages → RegisteredResources item {name, path, type: "Image"};
    page.json objects.background igual que en clásico.
  * El archivo va en Report/StaticResources/RegisteredResources/<item>; [Content_Types].xml necesita Default Extension png/jpg.
  * outspace (papel tapiz, lo que rodea al lienzo) = color sólido [probado].
[probado] Report Server 2026.05 y el Desktop de la nube muestran una imagen 1920x1080 con ajuste 'Fill' en 1280x720 nítida y sin recorte (en el
servicio es la técnica habitual). Recomendación de tamaño: 1280x720, 1664x936 o 1920x1080 (16:9), transparencia 0 %,
PNG < 3 MB (Power BI rechaza imágenes más pesadas al importarlas a mano; aquí se comprueba igual).

Uso:
  from fondo_pagina import fondo_clasico, fondos_pbir
  p = Pbix('base.pbix'); fondo_clasico(p, 'Resumen', open('fondo.png','rb').read(), 'fondo_resumen.png', papel='#0A0F1E')
  p.guardar('salida.pbix')
  fondos_pbir('entrada_pbir.pbix', 'salida.pbix', {'<page_id>': (png_bytes, 'fondo_resumen.png')}, papel='#0A0F1E')
Regla: si cambias la posición o el tamaño de un visual, vuelve a generar el fondo (los paneles están pintados en la imagen)."""
import json, os, random, re, zipfile

LIMITE_BYTES = 3 * 1024 * 1024
RUTA = 'Report/StaticResources/RegisteredResources/'

def _lit(v): return {'expr': {'Literal': {'Value': "'" + str(v).replace("'", "''") + "'"}}}
def _num(v): return {'expr': {'Literal': {'Value': f'{int(v)}D'}}}

def nombre_item(nombre):
    """Como lo hace Desktop: nombre base + dígitos aleatorios + extensión ('Fondobi2.jpg' -> 'Fondobi29181214502735944.jpg')."""
    base, ext = os.path.splitext(os.path.basename(nombre))
    base = re.sub(r'[^A-Za-z0-9_]', '_', base) or 'fondo'
    return f'{base}{random.randint(10**15, 10**17 - 1)}{(ext or ".png").lower()}'

def revisar_imagen(datos, nombre):
    """Devuelve avisos (no bloquea salvo peso > 3 MB). Lee el tamaño del PNG sin dependencias."""
    if len(datos) > LIMITE_BYTES:
        raise ValueError(f'{nombre}: {len(datos)/1048576:.1f} MB > 3 MB; exporta a 1280x720 o 1664x936, o usa JPG')
    av = []
    if datos[:8] == b'\x89PNG\r\n\x1a\n':
        w, h = int.from_bytes(datos[16:20], 'big'), int.from_bytes(datos[20:24], 'big')
        if abs(w / h - 16 / 9) > 0.01: av.append(f'{nombre}: {w}x{h} no es 16:9; con ajuste Fill se recorta')
        if w < 1280: av.append(f'{nombre}: {w}px de ancho se verá borroso; usa ≥ 1280 (mejor 1920)')
    return av

def objeto_fondo(item, nombre_visible, transparencia=0, ajuste='Fill', color=None):
    """objects.background de la página (igual en clásico y PBIR). ajuste: 'Fill' (observado), 'Fit', 'Normal'."""
    p = {}
    if color: p['color'] = {'solid': {'color': _lit(color)}}
    p['image'] = {'image': {'name': _lit(nombre_visible),
                            'url': {'expr': {'ResourcePackageItem': {'PackageName': 'RegisteredResources', 'PackageType': 1,
                                                                     'ItemName': item}}},
                            'scaling': _lit(ajuste)}}
    p['transparency'] = _num(transparencia)
    return [{'properties': p}]

def objeto_papel(color):
    return [{'properties': {'color': {'solid': {'color': _lit(color)}}, 'transparency': _num(0)}}]

def _ext(nombre): return os.path.splitext(nombre)[1].lstrip('.').lower() or 'png'

# ---------------------------------------------------------------- clásico
def fondo_clasico(pbix, pagina, imagen, nombre='fondo.png', transparencia=0, ajuste='Fill', color=None, papel=None):
    """pbix = modificar_layout.Pbix. Registra la imagen y la pone de fondo en `pagina` (displayName o name).
    Si la página ya tenía una imagen de fondo que nadie más usa, se quita del paquete. Devuelve (item, avisos)."""
    av = revisar_imagen(imagen, nombre)
    item = nombre_item(nombre)
    s = pbix.pagina(pagina); cfg = json.loads(s.get('config') or '{}'); objs = cfg.setdefault('objects', {})
    anterior = _item_de(objs.get('background'))
    objs['background'] = objeto_fondo(item, os.path.basename(nombre), transparencia, ajuste, color)
    if papel: objs['outspace'] = objeto_papel(papel)
    s['config'] = json.dumps(cfg, ensure_ascii=False)
    pks = pbix.layout.setdefault('resourcePackages', [])
    pk = next((x['resourcePackage'] for x in pks if x['resourcePackage']['name'] == 'RegisteredResources'), None)
    if pk is None:
        pk = {'name': 'RegisteredResources', 'type': 1, 'items': [], 'disabled': False}; pks.append({'resourcePackage': pk})
    pk['items'].append({'type': 100, 'path': item, 'name': item})
    if anterior and anterior not in json.dumps(pbix.layout['sections'], ensure_ascii=False) + pbix.layout.get('config', ''):
        pk['items'] = [i for i in pk['items'] if i['name'] != anterior]
        pbix.quitar_partes = getattr(pbix, 'quitar_partes', set()) | {RUTA + anterior}
    pbix.agregar_parte(RUTA + item, imagen, extension=_ext(item))
    pbix.log.append(f'fondo de página "{pagina}" = {item} ({len(imagen)//1024} KB)')
    return item, av

def _item_de(bg):
    try: return bg[0]['properties']['image']['image']['url']['expr']['ResourcePackageItem']['ItemName']
    except (TypeError, KeyError, IndexError): return None

# ---------------------------------------------------------------- PBIR
def fondos_pbir(origen, destino, fondos, transparencia=0, ajuste='Fill', color=None, papel=None,
                quitar_partes=('SecurityBindings',)):
    """fondos = {page_id: (bytes_imagen, nombre_visible)}. Escribe `destino` = `origen` + imágenes de fondo.
    Úsalo después de pbir.reemplazar_paginas (sobre su salida). Devuelve {page_id: item} y avisos."""
    zin = zipfile.ZipFile(origen)
    if 'Report/definition/report.json' not in zin.namelist(): raise ValueError('no es PBIR; usa fondo_clasico')
    rep = json.loads(zin.read('Report/definition/report.json'))
    pk = next((p for p in rep.setdefault('resourcePackages', []) if p['name'] == 'RegisteredResources'), None)
    if pk is None:
        pk = {'name': 'RegisteredResources', 'type': 'RegisteredResources', 'items': []}; rep['resourcePackages'].append(pk)
    nuevos, paginas, avisos, exts, viejos = {}, {}, [], set(), set()
    for pid, (img, nombre) in fondos.items():
        n = f'Report/definition/pages/{pid}/page.json'
        if n not in zin.namelist(): raise KeyError(f'página {pid} no existe')
        avisos += revisar_imagen(img, nombre)
        item = nombre_item(nombre); nuevos[pid] = item; exts.add(_ext(item))
        pj = json.loads(zin.read(n)); objs = pj.setdefault('objects', {})
        ant = _item_de(objs.get('background'))
        if ant: viejos.add(ant)
        objs['background'] = objeto_fondo(item, os.path.basename(nombre), transparencia, ajuste, color)
        if papel: objs['outspace'] = objeto_papel(papel)
        paginas[n] = pj
        pk['items'].append({'name': item, 'path': item, 'type': 'Image'})
    # quitar imágenes anteriores que ya nadie usa
    resto = ''.join(zin.read(x).decode('utf-8', 'ignore') for x in zin.namelist()
                    if x.startswith('Report/definition/pages/') and x.endswith('.json') and x not in paginas)
    resto += json.dumps(list(paginas.values()))
    huerfanos = {v for v in viejos if v not in resto}
    pk['items'] = [i for i in pk['items'] if i['name'] not in huerfanos]
    with zipfile.ZipFile(destino, 'w') as zout:
        for info in zin.infolist():
            n = info.filename
            if n in quitar_partes or n[len(RUTA):] in huerfanos and n.startswith(RUTA): continue
            data = zin.read(n)
            if n == 'Report/definition/report.json':
                data = json.dumps(rep, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
            elif n in paginas:
                data = json.dumps(paginas[n], ensure_ascii=False, separators=(',', ':')).encode('utf-8')
            elif n == '[Content_Types].xml':
                t = data.decode('utf-8-sig')
                for q in quitar_partes: t = t.replace(f'<Override PartName="/{q}" ContentType="" />', '')
                for e in exts:
                    if f'Extension="{e}"' not in t: t = t.replace('<Override ', f'<Default Extension="{e}" ContentType="" /><Override ', 1)
                data = (('﻿' + t) if zin.read(n).startswith(b'\xef\xbb\xbf') else t).encode('utf-8')
            zi = zipfile.ZipInfo(n, date_time=info.date_time); zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zout.writestr(zi, data)
        dt = zin.getinfo('Report/definition/report.json').date_time
        for pid, (img, _) in fondos.items():
            zi = zipfile.ZipInfo(RUTA + nuevos[pid], date_time=dt); zi.compress_type = zipfile.ZIP_STORED
            zout.writestr(zi, img)
    return nuevos, avisos

if __name__ == '__main__':
    import argparse, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    a = argparse.ArgumentParser(description='Pone una imagen como fondo de una página (clásico o PBIR).')
    a.add_argument('entrada'); a.add_argument('salida'); a.add_argument('pagina', help='displayName/name (clásico) o page_id (PBIR)')
    a.add_argument('imagen'); a.add_argument('--papel', help='color del papel tapiz, p. ej. #0A0F1E')
    x = a.parse_args(); img = open(x.imagen, 'rb').read()
    if 'Report/definition/report.json' in zipfile.ZipFile(x.entrada).namelist():
        it, av = fondos_pbir(x.entrada, x.salida, {x.pagina: (img, os.path.basename(x.imagen))}, papel=x.papel)
    else:
        from modificar_layout import Pbix
        p = Pbix(x.entrada); it, av = fondo_clasico(p, x.pagina, img, os.path.basename(x.imagen), papel=x.papel); p.guardar(x.salida)
    print('listo:', x.salida, it); [print('aviso:', v) for v in av]
