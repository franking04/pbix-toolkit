"""Primitivas para modificar Report/Layout (formato clásico) de un .pbix y reempaquetarlo.
Solo toca el reporte: el DataModel (XPress9) se copia byte a byte; no se pueden crear medidas ni columnas.
Reglas de empaquetado (para que Power BI Desktop lo abra):
  * Report/Layout se escribe en UTF-16 LE sin BOM.
  * DataModel se guarda sin compresión ZIP (stored), igual que el original.
  * Se elimina SecurityBindings y su Override en [Content_Types].xml.
  * En visuales cuyos campos cambian se borran los cachés 'query' y 'dataTransforms' (Desktop los regenera)."""
import json, zipfile, secrets, copy

AGG_FUNC = {'Sum': 0, 'Avg': 1, 'Count': 2, 'Min': 3, 'Max': 4, 'CountNonNull': 5}

# ---------- literales del lenguaje de expresiones del Layout ----------
def lit_value(v):
    if isinstance(v, bool): return 'true' if v else 'false'
    if isinstance(v, int): return f'{v}L'
    if isinstance(v, float): return f'{v}D'
    if v is None: return 'null'
    return "'" + str(v).replace("'", "''") + "'"
def lit(v): return {'expr': {'Literal': {'Value': lit_value(v)}}}
def dnum(v): return {'expr': {'Literal': {'Value': f'{float(v)}D'}}}
def dint(v):
    """Enum numérico (labelDisplayUnits, orientation, ...): entero con sufijo D, como lo escribe Desktop ('0D', '1000D')
    [probado]. Con dnum ('1.0D') Power BI lo acepta, pero el validador del CLI de Microsoft lo marca como enum inválido."""
    return {'expr': {'Literal': {'Value': f'{int(v)}D'}}}
def color(hexa): return {'solid': {'color': lit(hexa)}}
def nuevo_id(): return secrets.token_hex(10)

# ---------- carga y guardado ----------
class Pbix:
    def __init__(self, ruta):
        self.ruta = ruta
        self.zip = zipfile.ZipFile(ruta)
        self.layout = json.loads(self.zip.read('Report/Layout').decode('utf-16-le').lstrip('﻿'))
        self.log = []

    def agregar_parte(self, nombre, datos: bytes, extension=None):
        self.extras = getattr(self, 'extras', {}); self.extras[nombre] = datos
        if extension: self.extensiones = getattr(self, 'extensiones', set()) | {extension}
        self.log.append(f'parte nueva {nombre} ({len(datos)} bytes)')

    def guardar(self, destino):
        quitar = {'SecurityBindings'} | getattr(self, 'quitar_partes', set())
        extras = getattr(self, 'extras', {}); exts = getattr(self, 'extensiones', set())
        with zipfile.ZipFile(destino, 'w') as out:
            for info in self.zip.infolist():
                if info.filename in quitar: continue
                data = self.zip.read(info.filename)
                if info.filename == 'Report/Layout':
                    data = json.dumps(self.layout, ensure_ascii=False, separators=(',', ':')).encode('utf-16-le')
                elif info.filename == '[Content_Types].xml':
                    t = data.decode('utf-8-sig')
                    t = t.replace('<Override PartName="/SecurityBindings" ContentType="" />', '')
                    for e in exts:
                        if f'Extension="{e}"' not in t:
                            t = t.replace('<Override ', f'<Default Extension="{e}" ContentType="" /><Override ', 1)
                    data = ('﻿' + t).encode('utf-8') if data.startswith(b'\xef\xbb\xbf') else t.encode('utf-8')
                zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                zi.compress_type = info.compress_type          # DataModel queda STORED
                zi.external_attr = info.external_attr
                out.writestr(zi, data)
            for nombre, data in extras.items():
                if nombre in self.zip.namelist(): continue
                zi = zipfile.ZipInfo(nombre, date_time=self.zip.getinfo('Report/Layout').date_time)
                zi.compress_type = zipfile.ZIP_DEFLATED
                out.writestr(zi, data)
        self.log.append(f'guardado {destino} (sin SecurityBindings)')

    # ---------- navegación ----------
    def pagina(self, nombre):
        for s in self.layout['sections']:
            if s['displayName'] == nombre or s['name'] == nombre: return s
        raise KeyError(nombre)

    def visual(self, pagina, vid=None, tipo=None, titulo=None):
        for v in self.pagina(pagina)['visualContainers']:
            c = json.loads(v['config']); sv = c.get('singleVisual', {})
            if vid and c.get('name') != vid: continue
            if tipo and sv.get('visualType') != tipo: continue
            if titulo:
                t = (sv.get('vcObjects', {}).get('title') or [{}])[0].get('properties', {}).get('text', {})
                if titulo not in json.dumps(t, ensure_ascii=False): continue
            return Visual(self, v, c)
        raise KeyError((pagina, vid, tipo, titulo))

    # ---------- páginas ----------
    def agregar_pagina(self, nombre, ancho=1280, alto=720, fondo=None, oculta=False):
        cfg = {}
        if fondo: cfg['objects'] = {'background': [{'properties': {'color': color(fondo), 'transparency': dnum(0)}}]}
        if oculta: cfg['visibility'] = 1
        s = {'name': nuevo_id(), 'displayName': nombre, 'filters': '[]',
             'ordinal': len(self.layout['sections']), 'visualContainers': [],
             'config': json.dumps(cfg, ensure_ascii=False), 'displayOption': 1, 'width': ancho, 'height': alto}
        self.layout['sections'].append(s)
        self.log.append(f'página nueva "{nombre}" ({s["name"]})')
        return s

    # Tipos de item en resourcePackages (clásico): 100 imagen, 202 tema base y 201 tema personalizado [probado: RS 2026.05 lo aplica].
    ITEM = {'Image': 100, 'CustomTheme': 201, 'BaseTheme': 202}

    def tema_personalizado(self, tema_json, nombre_archivo=None):
        """[probado] Registra un tema JSON como tema personalizado en formato clásico (equivalente a Vista → Temas →
        Examinar). Reemplaza el tema personalizado anterior. Si Desktop no lo aplica, importa el JSON a mano.
        nombre_archivo por defecto = derivado de tema['name'] (como lo nombra el Desktop al importar)."""
        if nombre_archivo is None:
            from tema_powerbi import nombre_archivo_tema
            nombre_archivo = nombre_archivo_tema(tema_json['name'])
        tema_json = dict(tema_json, name=nombre_archivo)      # igual que en PBIR (regla del CLI)
        cfg = json.loads(self.layout.get('config') or '{}'); tc = cfg.setdefault('themeCollection', {})
        tc['customTheme'] = {'name': nombre_archivo, 'version': tc.get('baseTheme', {}).get('version'), 'type': 1}
        self.layout['config'] = json.dumps(cfg, ensure_ascii=False)
        pks = self.layout.setdefault('resourcePackages', [])
        pk = next((x['resourcePackage'] for x in pks if x['resourcePackage']['name'] == 'RegisteredResources'), None)
        if pk is None:
            pk = {'name': 'RegisteredResources', 'type': 1, 'items': [], 'disabled': False}; pks.append({'resourcePackage': pk})
        viejos = [i['path'] for i in pk['items'] if i.get('type') == self.ITEM['CustomTheme']]
        pk['items'] = [i for i in pk['items'] if i.get('type') != self.ITEM['CustomTheme']] + \
                      [{'type': self.ITEM['CustomTheme'], 'path': nombre_archivo, 'name': nombre_archivo}]
        self.quitar_partes = getattr(self, 'quitar_partes', set()) | {'Report/StaticResources/RegisteredResources/' + v for v in viejos}
        self.agregar_parte('Report/StaticResources/RegisteredResources/' + nombre_archivo,
                           json.dumps(tema_json, ensure_ascii=False, indent=1).encode('utf-8'), extension='json')
        self.log.append(f'tema personalizado {nombre_archivo} (formato clásico)')

    VISTAS = {'FitToPage': 1, 'FitToWidth': 2, 'ActualSize': 3}   # 1 observado; 2 y 3 por validar en clásico

    def vista_pagina(self, nombre, vista):
        self.pagina(nombre)['displayOption'] = self.VISTAS[vista]; self.log.append(f'vista {nombre} = {vista}')

    def ocultar_pagina(self, nombre, oculta=True):
        s = self.pagina(nombre); cfg = json.loads(s.get('config') or '{}')
        if oculta: cfg['visibility'] = 1          # [probado] así la guarda Desktop (clásico)
        else: cfg.pop('visibility', None)
        s['config'] = json.dumps(cfg, ensure_ascii=False); self.log.append(f'{nombre} oculta={oculta}')

    def ordenar_paginas(self, nombres, activa=None):
        """Orden de pestañas (displayName o name); las no nombradas quedan al final. `activa` = página que abre."""
        elegidas = [self.pagina(n) for n in nombres]
        resto = [x for x in self.layout['sections'] if x not in elegidas]
        self.layout['sections'] = elegidas + resto
        for i, x in enumerate(self.layout['sections']): x['ordinal'] = i
        if activa:
            cfg = json.loads(self.layout.get('config') or '{}')
            cfg['activeSectionIndex'] = self.layout['sections'].index(self.pagina(activa))
            self.layout['config'] = json.dumps(cfg, ensure_ascii=False)
        self.log.append(f'orden de páginas {[x["displayName"] for x in self.layout["sections"]]}')

    def agregar_filtro(self, pagina, entidad, columna, excluir_vacios=True, oculto=False, visual=None):
        """Filtro categórico 'no está en blanco' a nivel de página (o de visual si se pasa visual)."""
        f = {'name': 'Filter' + nuevo_id(),
             'expression': {'Column': {'Expression': {'SourceRef': {'Entity': entidad}}, 'Property': columna}},
             'filter': {'Version': 2, 'From': [{'Name': 'x', 'Entity': entidad, 'Type': 0}],
                        'Where': [{'Condition': {'Not': {'Expression': {'In': {
                            'Expressions': [{'Column': {'Expression': {'SourceRef': {'Source': 'x'}}, 'Property': columna}}],
                            'Values': [[{'Literal': {'Value': 'null'}}]]}}}}}]},
             'type': 'Categorical', 'howCreated': 1,
             'objects': {'general': [{'properties': {'isInvertedSelectionMode': lit(True)}}]},
             'isHiddenInViewMode': oculto}
        dueño = visual.cont if visual else self.pagina(pagina)
        lista = json.loads(dueño.get('filters') or '[]'); f['ordinal'] = len(lista); lista.append(f)
        dueño['filters'] = json.dumps(lista, ensure_ascii=False)
        self.log.append(f'filtro {"visual" if visual else "página"} "{pagina}": {entidad}[{columna}] no en blanco')

    # ---------- visuales nuevos ----------
    def agregar_visual(self, pagina, tipo, pos, roles=None, titulo=None, objects=None, vcObjects=None, orden=None):
        """roles: {'Values': [campo, ...]}; campo = (entidad, propiedad, agregacion|None|'measure', nombre_visible)."""
        s = self.pagina(pagina)
        x, y, w, h = pos; z = (max([v.get('z', 0) for v in s['visualContainers']] or [0]) + 1000)
        sv = {'visualType': tipo, 'drillFilterOtherVisuals': True}
        if roles:
            alias, frm, sel, proy, cprops = {}, [], [], {}, {}
            for rol, campos in roles.items():
                proy[rol] = []
                for ent, prop, agg, visible in campos:
                    if ent not in alias:
                        a = ent[0].lower(); n = 1
                        while a in alias.values(): a = ent[0].lower() + str(n); n += 1
                        alias[ent] = a; frm.append({'Name': a, 'Entity': ent, 'Type': 0})
                    src = {'SourceRef': {'Source': alias[ent]}}
                    if agg == 'measure':
                        e = {'Measure': {'Expression': src, 'Property': prop}}; qn = f'{ent}.{prop}'
                    elif agg:
                        e = {'Aggregation': {'Expression': {'Column': {'Expression': src, 'Property': prop}}, 'Function': AGG_FUNC[agg]}}
                        qn = f'{agg}({ent}.{prop})'
                    else:
                        e = {'Column': {'Expression': src, 'Property': prop}}; qn = f'{ent}.{prop}'
                    if qn not in [x_['Name'] for x_ in sel]:
                        sel.append(dict(e, Name=qn, NativeReferenceName=visible or prop))
                    primero = rol in ('Category', 'Rows', 'Columns') and not proy[rol]
                    proy[rol].append({'queryRef': qn, **({'active': True} if primero else {})})
                    if visible: cprops[qn] = {'displayName': visible}
            pq = {'Version': 2, 'From': frm, 'Select': sel}
            if orden:                                    # (queryRef, 'asc'|'desc')
                qn, d = orden; e = {k: v for k, v in next(x_ for x_ in sel if x_['Name'] == qn).items()
                                    if k not in ('Name', 'NativeReferenceName')}
                pq['OrderBy'] = [{'Direction': 1 if d == 'asc' else 2, 'Expression': e}]
            sv.update(projections=proy, prototypeQuery=pq)
            if cprops: sv['columnProperties'] = cprops
        sv['objects'] = objects or {}
        vco = vcObjects or {}
        if titulo is not None:
            vco.setdefault('title', [{'properties': {}}])[0]['properties'].update(show=lit(True), text=lit(titulo))
        sv['vcObjects'] = vco
        vid = nuevo_id()
        cfg = {'name': vid, 'layouts': [{'id': 0, 'position': {'x': x, 'y': y, 'z': z, 'width': w, 'height': h, 'tabOrder': z}}],
               'singleVisual': sv}
        cont = {'x': x, 'y': y, 'z': z, 'width': w, 'height': h, 'config': json.dumps(cfg, ensure_ascii=False),
                'filters': '[]', 'tabOrder': z}
        s['visualContainers'].append(cont)
        self.log.append(f'visual nuevo {tipo} en "{pagina}" ({vid}) {titulo or ""}')
        return Visual(self, cont, cfg)

    def clonar_visual(self, origen, pagina_destino, pos=None):
        c = copy.deepcopy(origen.cfg); c['name'] = nuevo_id()
        cont = copy.deepcopy(origen.cont); cont.pop('query', None); cont.pop('dataTransforms', None)
        s = self.pagina(pagina_destino)
        z = max([v_.get('z', 0) for v_ in s['visualContainers']] or [0]) + 1000   # z y tabOrder únicos
        cont['z'] = z; cont['tabOrder'] = z; c['layouts'][0]['position'].update(z=z, tabOrder=z)
        cont['config'] = json.dumps(c, ensure_ascii=False); s['visualContainers'].append(cont)
        v = Visual(self, cont, c)
        if pos: v.mover(*pos)
        self.log.append(f'visual clonado {origen.tipo} -> "{pagina_destino}" ({c["name"]})')
        return v

class Visual:
    def __init__(self, pbix, cont, cfg):
        self.p, self.cont, self.cfg = pbix, cont, cfg
    @property
    def sv(self): return self.cfg['singleVisual']
    @property
    def tipo(self): return self.sv['visualType']
    @property
    def id(self): return self.cfg['name']
    def _sync(self): self.cont['config'] = json.dumps(self.cfg, ensure_ascii=False)
    def _sin_cache(self):
        for k in ('query', 'dataTransforms'): self.cont.pop(k, None)

    def mover(self, x=None, y=None, w=None, h=None):
        pos = self.cfg['layouts'][0]['position']        # la posición vive en DOS sitios
        for k, v in (('x', x), ('y', y), ('width', w), ('height', h)):
            if v is not None: self.cont[k] = v; pos[k] = v
        self._sync(); self.p.log.append(f'{self.tipo} {self.id}: posición {x},{y},{w},{h}')

    def propiedad(self, zona, objeto, props, selector=None):
        """Fusiona props en sv[zona][objeto] (zona = 'objects' | 'vcObjects')."""
        lista = self.sv.setdefault(zona, {}).setdefault(objeto, [])
        item = next((i for i in lista if i.get('selector') == selector), None)
        if item is None:
            item = {'properties': {}}; lista.append(item)
            if selector is not None: item['selector'] = selector
        item['properties'].update(props); self._sync()
        self.p.log.append(f'{self.tipo} {self.id}: {zona}.{objeto} <- {", ".join(props)}')

    def titulo(self, texto, mostrar=True, tamaño=None, color_fondo=None, color_letra=None):
        props = {'show': lit(mostrar), 'text': lit(texto)}
        if tamaño: props['fontSize'] = dnum(tamaño)
        if color_fondo: props['background'] = color(color_fondo)
        if color_letra: props['fontColor'] = color(color_letra)
        self.propiedad('vcObjects', 'title', props)

    def renombrar_ref(self, viejo, nuevo):
        """Cambia un queryRef/Name en todo el visual (projections, Select, columnProperties, selectores)."""
        def r(o):
            if isinstance(o, dict): return {(nuevo if k == viejo else k): r(v) for k, v in o.items()}
            if isinstance(o, list): return [r(v) for v in o]
            return nuevo if o == viejo else o
        self.cfg['singleVisual'] = r(self.sv); self._sin_cache(); self._sync()
        self.p.log.append(f'{self.tipo} {self.id}: queryRef "{viejo}" -> "{nuevo}"')

    def quitar_campo(self, qref):
        sv = self.sv
        for rol in sv['projections']: sv['projections'][rol] = [i for i in sv['projections'][rol] if i['queryRef'] != qref]
        sv['prototypeQuery']['Select'] = [s for s in sv['prototypeQuery']['Select'] if s['Name'] != qref]
        sv.get('columnProperties', {}).pop(qref, None)
        for obj in sv.get('objects', {}).values():
            obj[:] = [i for i in obj if (i.get('selector') or {}).get('metadata') != qref]
        self._sin_cache(); self._sync(); self.p.log.append(f'{self.tipo} {self.id}: quitado {qref}')

    def ordenar_rol(self, rol, orden):
        actual = {i['queryRef']: i for i in self.sv['projections'][rol]}
        assert set(orden) == set(actual), (set(orden) ^ set(actual))
        self.sv['projections'][rol] = [actual[q] for q in orden]
        self._sin_cache(); self._sync(); self.p.log.append(f'{self.tipo} {self.id}: nuevo orden de {rol}')

    def gradiente(self, qref, entidad, columna, agg, minimo='#FFFFFF', maximo='#F0391D'):
        """Formato condicional: color de fondo en escala sobre una columna agregada."""
        entrada = {'Aggregation': {'Expression': {'Column': {'Expression': {'SourceRef': {'Entity': entidad}}, 'Property': columna}},
                                   'Function': AGG_FUNC[agg]}}
        regla = {'solid': {'color': {'expr': {'FillRule': {'Input': entrada, 'FillRule': {'linearGradient2': {
            'min': {'color': {'Literal': {'Value': f"'{minimo}'"}}}, 'max': {'color': {'Literal': {'Value': f"'{maximo}'"}}},
            'nullColoringStrategy': {'strategy': {'Literal': {'Value': "'asZero'"}}}}}}}}}}
        self.propiedad('objects', 'values', {'backColor': regla},
                       selector={'data': [{'dataViewWildcard': {'matchingOption': 1}}], 'metadata': qref})

if __name__ == '__main__':
    print(__doc__.strip()); print('\n(módulo: se importa desde Python; ver SKILL.md)')
