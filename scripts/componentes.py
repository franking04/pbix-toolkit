"""Componentes de maqueta reutilizables para construir páginas de Power BI con modificar_layout.py, parametrizados
por los tokens de una dirección visual (tema_powerbi.DIRECCIONES o un dict propio con las mismas claves).
Todo lo de aquí está [probado] en pantalla salvo donde se indica.
Reglas incorporadas: alturas mínimas de texto (evitan la barra de desplazamiento), tarjeta clásica para valores
dinámicos (multiRowCard ignora tamaño/color), pila completa de fuentes, color por reglas sobre medidas.
v2 (LienzoV2, al final): estilo de guia_diseno.md con tokens.json, niveles y 2 capas."""
import json
from modificar_layout import lit, dnum, dint, color

REG = "'Segoe UI', wf_segoe-ui_normal, helvetica, arial, sans-serif"
SEMI = "'Segoe UI Semibold', wf_segoe-ui_semibold, helvetica, arial, sans-serif"
BOLD = "'Segoe UI Bold', wf_segoe-ui_bold, helvetica, arial, sans-serif"

def pt(px): return round(px * 0.75, 1)
def alto_min(px, lineas=1): return round(px * 1.45 * lineas + 14)      # textbox: menos que esto => scroll [probado]
def piso_cli(tam_pt, pad_sup=8, pad_inf=8):
    """Piso de altura de textbox del CLI de Microsoft (aviso PBIR_TEXTBOX_HEIGHT_BELOW_FLOOR): max(18, ceil(pt*25/16)) +
    padding (8+8 por defecto, o el de visualContainerObjects.padding). Es conservador: 28–32 px con 8.6–9.4 pt no
    mostraron scroll en pantalla [probado: captura]. Úsalo como aviso; el mínimo es alto_min()."""
    return max(18, -(-tam_pt * 25 // 16)) + pad_sup + pad_inf

def _padding(vco):
    """(sup, inf) de visualContainerObjects/vcObjects.padding, o (8, 8) por defecto (como el CLI)."""
    def num(v, d):
        try: return float(str(v['expr']['Literal']['Value']).rstrip('DL'))
        except (KeyError, TypeError, ValueError): return d
    p = ((vco or {}).get('padding') or [{}])[0].get('properties', {})
    return num(p.get('top'), 8), num(p.get('bottom'), 8)

def marco():
    return {'title': [{'properties': {'show': lit(False)}}], 'background': [{'properties': {'show': lit(False)}}],
            'border': [{'properties': {'show': lit(False)}}], 'visualHeader': [{'properties': {'show': lit(False)}}]}

def regla(entidad, medida, casos):
    """Color por reglas sobre una medida: casos = [(ComparisonKind, umbral, '#hex')] (0 =, 1 >, 2 >=, 3 <, 4 <=)."""
    left = {'Measure': {'Expression': {'SourceRef': {'Entity': entidad}}, 'Property': medida}}
    return {'solid': {'color': {'expr': {'Conditional': {'Cases': [
        {'Condition': {'Comparison': {'ComparisonKind': k, 'Left': left, 'Right': {'Literal': {'Value': f'{float(u)}D'}}}},
         'Value': {'Literal': {'Value': f"'{c}'"}}} for k, u, c in casos]}}}}}

def wild(q): return {'data': [{'dataViewWildcard': {'matchingOption': 1}}], 'metadata': q}

class Lienzo:
    """Dibuja sobre una página (nombre visible) de un Pbix clásico con los tokens T de una dirección."""
    def __init__(self, p, pagina, T, entidad_medidas=None):
        self.p, self.pag, self.T, self.E = p, pagina, T, entidad_medidas

    # --- primitivas ---
    def caja(self, x, y, w, h, fondo=None, borde='linea', radio=None):
        T = self.T; fondo = fondo or T['superficie']
        b = T.get(borde, borde) if borde else None
        vco = {'background': [{'properties': {'show': lit(True), 'color': color(fondo), 'transparency': dnum(0)}}],
               'visualHeader': [{'properties': {'show': lit(False)}}],
               'border': [{'properties': {'show': lit(b is not None), 'color': color(b or fondo),
                                          'radius': dnum(T['radio'] if radio is None else radio)}}]}
        return self.p.agregar_visual(self.pag, 'textbox', (x, y, w, h),
            objects={'general': [{'properties': {'paragraphs': [{'textRuns': [{'value': ''}]}]}}]}, vcObjects=vco)

    def texto(self, x, y, w, h, runs, alinear='left', lineas=1):
        """runs = [(texto, tamaño_px, '#hex' o clave de token, negrita)]. Ajusta la altura mínima automáticamente."""
        tam = max(r[1] for r in runs); h = max(h, alto_min(tam, lineas))
        par = {'textRuns': [{'value': t, 'textStyle': {'fontSize': f'{pt(px)}pt', 'color': self.T.get(c, c),
                'fontFamily': SEMI if b else REG}} for t, px, c, b in runs], 'horizontalTextAlignment': alinear}
        return self.p.agregar_visual(self.pag, 'textbox', (x, y, w, h),
            objects={'general': [{'properties': {'paragraphs': [par]}}]}, vcObjects=marco())

    def valor(self, x, y, w, h, medida, tam_pt, col='texto', fuente=BOLD, regla_color=None, entidad=None):
        """Valor dinámico (medida, a menudo texto con FORMAT) en tarjeta clásica centrada."""
        return self.p.agregar_visual(self.pag, 'card', (x, y, w, h),
            roles={'Values': [(entidad or self.E, medida, 'measure', ' ')]},
            objects={'labels': [{'properties': {'fontSize': dnum(tam_pt), 'color': regla_color or color(self.T.get(col, col)),
                                                'fontFamily': lit(fuente), 'labelDisplayUnits': dint(1)}}],
                     'categoryLabels': [{'properties': {'show': lit(False)}}]}, vcObjects=marco())

    def valor_columna(self, x, y, w, h, entidad, columna, agg, tam_pt, col='texto', decimales=0):
        """Valor de una columna agregada (sin medida): unidades 'ninguna' y decimales fijos."""
        return self.p.agregar_visual(self.pag, 'card', (x, y, w, h),
            roles={'Values': [(entidad, columna, agg, ' ')]},
            objects={'labels': [{'properties': {'fontSize': dnum(tam_pt), 'color': color(self.T.get(col, col)),
                                                'fontFamily': lit(BOLD), 'labelDisplayUnits': dint(1),
                                                'labelPrecision': lit(decimales)}}],
                     'categoryLabels': [{'properties': {'show': lit(False)}}]}, vcObjects=marco())

    # --- compuestos ---
    def kpi(self, x, y, w, h, etiqueta, medida=None, detalle=None, detalle_medida=None, regla_color=None,
            columna=None, tam_pt=22):
        """Tarjeta KPI: etiqueta arriba, valor grande, detalle abajo. columna=(entidad, col, agg, decimales) si no hay medida."""
        self.caja(x, y, w, h)
        self.texto(x + 8, y + 4, w - 16, 28, [(etiqueta.upper(), 11.5, 'texto2', True)], alinear='center')
        vy, vh = y + 28, h - 62
        if columna: self.valor_columna(x + 6, vy, w - 12, vh, *columna[:3], tam_pt, decimales=columna[3] if len(columna) > 3 else 0)
        else: self.valor(x + 6, vy, w - 12, vh, medida, tam_pt, regla_color=regla_color)
        if detalle_medida: self.valor(x + 6, y + h - 36, w - 12, 32, detalle_medida, 9.5, 'texto2', fuente=REG)
        elif detalle: self.texto(x + 8, y + h - 34, w - 16, 28, [(detalle, 12, 'texto2', False)], alinear='center')

    def seccion(self, x, y, w, h, titulo, subtitulo=None):
        """Contenedor con título y subtítulo; devuelve el rectángulo útil (x, y, w, h) para el contenido."""
        self.caja(x, y, w, h)
        self.texto(x + 14, y + 8, w - 28, 36, [(titulo, 16, 'texto', True)])
        if subtitulo:
            self.texto(x + 14, y + 40, w - 28, 30, [(subtitulo, 12.5, 'texto2', False)])
            return (x + 8, y + 76, w - 16, h - 84)
        return (x + 8, y + 48, w - 16, h - 56)

    def encabezado(self, x, y, w, h, kicker, titulo=None, titulo_medida=None, sub=None, sub_medida=None, ancho_texto=None):
        T = self.T; zw = ancho_texto or w - 32
        self.caja(x, y, w, h, fondo=T['enc_fondo'], borde=None, radio=T['radio'] + 2)
        self.p.agregar_visual(self.pag, 'basicShape', (x + 6, y + h - 4, w - 12, 3),
            objects={'general': [{'properties': {'shapeType': lit('rectangle')}}],
                     'fill': [{'properties': {'fillColor': color(T['enc_linea']), 'transparency': dnum(0)}}],
                     'line': [{'properties': {'weight': dnum(0), 'lineColor': color(T['enc_linea'])}}]}, vcObjects=marco())
        self.texto(x + 16, y + 6, zw, 30, [(kicker.upper(), 11.5, T['enc_kicker'], True)], alinear='left')
        if titulo_medida: self.valor_izq_titulo(x + 16, y + 30, zw, 46, titulo_medida)
        elif titulo: self.texto(x + 16, y + 30, zw, 46, [(titulo, 26, T['enc_texto'], True)])
        if sub_medida: self.valor(x + 16, y + h - 40, zw, 32, sub_medida, 11, T['enc_sub'], fuente=REG)
        elif sub: self.texto(x + 16, y + h - 40, zw, 32, [(sub, 13, T['enc_sub'], False)])

    def valor_izq_titulo(self, x, y, w, h, medida):
        """Título dinámico grande (tarjeta clásica: queda centrado en su caja)."""
        return self.valor(x, y, w, h, medida, 20, self.T['enc_texto'])

    def boton_nav(self, x, y, w, h, texto, page_id, activo=False):
        """Botón de navegación con texto (actionButton + visualLink PageNavigation) [por validar: combinación;
        actionButton y visualLink están vistos por separado]."""
        T = self.T
        fondo = T['enc_fondo'] if activo else T['superficie']
        letra = T['enc_texto'] if activo else T['texto']
        objs = {'icon': [{'properties': {'shapeType': lit('blank')}, 'selector': {'id': 'default'}}],
                'fill': [{'properties': {'show': lit(True)}},
                         {'properties': {'fillColor': color(fondo), 'transparency': dnum(0)}, 'selector': {'id': 'default'}}],
                'text': [{'properties': {'show': lit(True)}},
                         {'properties': {'text': lit(texto), 'fontColor': color(letra), 'fontSize': dnum(10),
                                         'fontFamily': lit(SEMI), 'horizontalAlignment': lit('center'),
                                         'verticalAlignment': lit('middle')}, 'selector': {'id': 'default'}}],
                'outline': [{'properties': {'show': lit(not activo), 'lineColor': color(T['linea'])},
                             'selector': {'id': 'default'}}],
                # roundEdge es de 'shape' (en 'outline' no existe y el Desktop de la nube lo borra al guardar [probado])
                'shape': [{'properties': {'roundEdge': lit(int(T['radio']))}, 'selector': {'id': 'default'}}]}
        vco = {'visualLink': [{'properties': {'show': lit(True), 'type': lit('PageNavigation'),
                                              'navigationSection': lit(page_id), 'tooltip': lit(f'Ir a {texto}')}}],
               'title': [{'properties': {'show': lit(False)}}], 'background': [{'properties': {'show': lit(False)}}],
               'border': [{'properties': {'show': lit(False)}}], 'visualHeader': [{'properties': {'show': lit(False)}}]}
        return self.p.agregar_visual(self.pag, 'actionButton', (x, y, w, h), objects=objs, vcObjects=vco)

    def barra_nav(self, paginas, activa, y=8, ancho=170, alto=30, derecha=1264, marca=None):
        """Fila de pestañas (mismo lugar en todas las páginas). paginas = [(texto, page_id)]."""
        if marca: self.texto(16, y - 2, 420, alto + 4, [(marca, 12, 'texto', True)])
        x = derecha - len(paginas) * (ancho + 8) + 8
        for i, (t, pid) in enumerate(paginas):
            self.boton_nav(x + i * (ancho + 8), y, ancho, alto, t, pid, activo=(pid == activa))


# ====================================================================== v2 (tokens.json, niveles, 2 capas)
def ancho_texto(texto, tam_pt, peso=None):
    """Ancho en px de un texto en Segoe UI: `powerbi-report-author text measure` (métricas reales de la fuente) si está instalado;
    si no, estimación 0.56 × px por carácter (+8 % en semibold). Sirve para dar a una card clásica (valor centrado) el ancho del
    texto y que quede alineada a la izquierda [probado]."""
    import shutil, subprocess
    exe = shutil.which('powerbi-report-author')
    if exe:
        try:
            r = subprocess.run([exe, 'text', 'measure', texto, '--size', str(tam_pt), '--hpad', '4', '--margin', '0.02']
                               + (['--weight', peso] if peso else []), capture_output=True, text=True, encoding='utf-8', timeout=30)
            return json.loads(r.stdout)['data']['minWidthPx']
        except Exception:
            pass
    return round(len(texto) * tam_pt / .75 * .56 * (1.08 if peso else 1) + 8)

FUENTES = {'Segoe UI': REG, 'Segoe UI Semibold': SEMI, 'Segoe UI Bold': BOLD, 'Georgia': "Georgia, 'Times New Roman', serif"}
DEF = {'id': 'default'}

def titulo_visual(t, sub=None, alt=None, T=None, transparente=True):
    """vcObjects con título + subtítulo (unidad y periodo, guía §9) y texto alternativo. transparente: sin fondo ni borde."""
    T = T or {}
    v = {'title': [{'properties': {'show': lit(True), 'text': lit(t), 'fontSize': dnum(T.get('escala', {}).get('titulo_visual', 10)),
                                   'fontFamily': lit(SEMI), **({'fontColor': color(T['texto'])} if 'texto' in T else {})}}],
         'visualHeader': [{'properties': {'show': lit(False)}}]}
    if sub: v['subTitle'] = [{'properties': {'show': lit(True), 'text': lit(sub), 'fontSize': dnum(9),
                                             **({'fontColor': color(T['texto2'])} if 'texto2' in T else {})}}]
    if alt: v['general'] = [{'properties': {'altText': lit(alt)}}]
    if transparente:
        v['background'] = [{'properties': {'show': lit(False)}}]; v['border'] = [{'properties': {'show': lit(False)}}]
    return v

class LienzoV2(Lienzo):
    """Estilo v2 (guia_diseno.md): encabezado claro sin banda oscura, KPI héroe + tira con separadores de 1 px, secciones con
    caja (direcciones con tarjetas) o con regla de 1 px (editorial, suizo), título + subtítulo de visual, estado ícono + texto,
    pie de confianza. Lee los tokens de la dirección (tema_powerbi.DIRECCIONES ← references/tokens.json). En 2 capas no dibuja
    cajas (están en la imagen de fondo) y los visuales van transparentes. Posiciones en múltiplos de 8 (rejilla).
    [probado: demos moderno y editorial en el Desktop para RS 2026.05 y en el portal RS; la v1 (Lienzo) sigue igual]"""
    def __init__(self, p, pagina, direccion='moderno', entidad_medidas=None):
        from tema_powerbi import DIRECCIONES
        super().__init__(p, pagina, DIRECCIONES[direccion], entidad_medidas)
        self.dir = direccion; self.E8 = self.T.get('escala', {})
        self.dos_capas = self.T.get('capas', 1) == 2

    def _pt(self, clave, defecto): return self.E8.get(clave, defecto)

    def texto(self, x, y, w, h, runs, alinear='left', lineas=1):
        """Como Lienzo.texto, con el alto redondeado hacia arriba a múltiplo de 8 (rejilla) sin bajar del mínimo."""
        tam = max(r[1] for r in runs); h = max(h, alto_min(tam, lineas)); h = -(-h // 8) * 8
        return super().texto(x, y, w, h, runs, alinear, lineas)

    def linea(self, x, y, w, h=1):
        """Regla o separador de 1 px (basicShape rectángulo relleno con el color de línea)."""
        return self.p.agregar_visual(self.pag, 'basicShape', (x, y, w, h),
            objects={'general': [{'properties': {'shapeType': lit('rectangle')}}],
                     'fill': [{'properties': {'fillColor': color(self.T['linea']), 'transparency': dnum(0)}}],
                     'line': [{'properties': {'weight': dnum(0), 'lineColor': color(self.T['linea'])}}]}, vcObjects=marco())

    def valor_card(self, x, y, w, h, medida, tam_pt, col='texto', fuente=SEMI, regla_color=None, alt=None):
        """card clásica (valor centrado): para medidas de TEXTO de una línea (títulos-conclusión, periodo, estado). cardVisual
        corta el texto en cajas bajas [probado RS 2026.05]. Para alinear casi a la izquierda, ancho = texto medido
        (`powerbi-report-author text measure`)."""
        v = self.valor(x, y, w, h, medida, tam_pt, col, fuente=fuente, regla_color=regla_color)
        if alt: v.propiedad('vcObjects', 'general', {'altText': lit(alt)})
        return v

    def encabezado_v2(self, x, y, w, kicker, titulo=None, titulo_medida=None, sub=None, sub_medida=None, ancho_titulo=None, regla=True,
                      titulo_ejemplo=None, sub_ejemplo=None):
        """Encabezado claro: kicker (acento, 9 pt) · título (15 pt) · subtítulo (10 pt) · regla de 1 px.
        Título o subtítulo dinámicos (medida de texto) → card clásica cuyo ancho = texto de ejemplo medido (`titulo_ejemplo`, el valor
        más habitual), así el texto centrado queda alineado a la izquierda. Textos más largos se cortan: da el ejemplo más largo."""
        T = self.T
        self.texto(x, y, w, 24, [(kicker, self._pt('etiqueta', 9) / .75, T['acento'], True)])
        tp = self._pt('titulo_pagina', 15)
        if titulo_medida:
            aw = ancho_titulo or (ancho_texto(titulo_ejemplo, tp, 'semibold') if titulo_ejemplo else 520)
            aw = -(-aw // 8) * 8   # rejilla
            self.valor_card(x, y + 24, min(aw, w), 40, titulo_medida, tp, 'texto', alt='Título de la página')
        elif titulo: self.texto(x, y + 24, w, 40, [(titulo, tp / .75, T['texto'], True)])
        if sub_medida: self.valor_card(x, y + 64, min(w, -(-ancho_texto(sub_ejemplo, 10) // 8) * 8 if sub_ejemplo else 320), 24, sub_medida, 10, 'texto2',
                                       fuente=REG, alt='Periodo')
        elif sub: self.texto(x, y + 64, w, 24, [(sub, 10 / .75, T['texto2'], False)])
        if regla: self.linea(x, y + 96, w)
        return y + 104

    def _tarjeta(self, x, y, w, h, medida, etiqueta, tam_pt, imagen=None, alto_img=64, alt=None):
        DEFS = {'value': [{'properties': {'fontSize': dnum(tam_pt), 'fontColor': color(self.T['texto']), 'fontFamily': lit(SEMI),
                                          'labelDisplayUnits': dint(1)}, 'selector': DEF}],   # «auto» sale en el idioma del Desktop
                'label': [{'properties': {'show': lit(True), 'text': lit(etiqueta), 'fontColor': color(self.T['texto2']), 'fontSize': dnum(10),
                                          'position': lit('aboveValue')}, 'selector': DEF}],
                'fillCustom': [{'properties': {'show': lit(False)}, 'selector': DEF}],
                'outline': [{'properties': {'show': lit(False)}, 'selector': DEF}],
                'divider': [{'properties': {'show': lit(False)}, 'selector': DEF}]}
        if imagen:   # medida SVG (ImageUrl) como imagen de la tarjeta [probado RS 2026.05 y nube]
            DEFS['cardImage'] = [{'properties': {'show': lit(True), 'imageType': lit('imageUrl'),
                                                 'imageUrl': {'expr': {'Measure': {'Expression': {'SourceRef': {'Entity': self.E}}, 'Property': imagen}}},
                                                 'imageUrlFit': lit('Normal'), 'imageHeight': lit(alto_img)}, 'selector': DEF}]
        vco = {**marco(), 'general': [{'properties': {'altText': lit(alt or etiqueta)}}]}   # texto alternativo por defecto = etiqueta
        return self.p.agregar_visual(self.pag, 'cardVisual', (x, y, w, h), roles={'Data': [(self.E, medida, 'measure', etiqueta)]},
                                     objects=DEFS, vcObjects=vco)

    def kpi_heroe(self, x, y, w, h, etiqueta, medida, imagen=None, alto_img=24, alt=None, delta_medida=None, delta_texto=None):
        """KPI principal (27 pt). Caja solo si la dirección usa tarjetas y es 1 capa.
        delta_medida: variación NUMÉRICA nativa (formatString de la medida, p. ej. `+0.0 %;-0.0 %;0.0 %`) en una card clásica abajo a la
        izquierda, color por regla (sube/baja) [probado: card con color por reglas] → sigue la configuración regional del lector, a
        diferencia de un texto dentro de un SVG. delta_texto: contexto fijo al lado («vs mes ant.»)."""
        if self.T.get('tarjetas', True) and not self.dos_capas: self.caja(x, y, w, h)
        alto_valor = h - 16 - (40 if delta_medida else 0)
        v = self._tarjeta(x + 8, y + 8, w - 16, alto_valor, medida, etiqueta, self._pt('kpi_heroe', 27), imagen, alto_img, alt)
        if delta_medida:
            yd = y + h - 48
            self.valor_card(x + 16, yd, 104, 32, delta_medida, 12, regla_color=regla(self.E, delta_medida,
                            [(2, 0, self.T['sube']), (3, 0, self.T['baja'])]), fuente=SEMI, alt='Variación')
            if delta_texto: self.texto(x + 128, yd, w - 144, 32, [(delta_texto, 10 / .75, self.T['texto2'], False)])
        return v

    def tira_kpi(self, x, y, w, h, items, alt=None):
        """Fila de KPI secundarios (21 pt) separados por reglas verticales de 1 px. items = [(etiqueta, medida[, imagen])]."""
        n = len(items); paso = w / n
        if self.T.get('tarjetas', True) and not self.dos_capas: self.caja(x, y, w, h)
        for i, it in enumerate(items):
            et, med = it[0], it[1]; img = it[2] if len(it) > 2 else None
            self._tarjeta(round(x + i * paso) + 8, y + 8, round(paso) - 16, h - 16, med, et, self._pt('kpi', 21), img, 48, alt and f'{alt}: {et}')
            if i: self.linea(round(x + i * paso), y + 16, 1, h - 32)

    def seccion_v2(self, x, y, w, h, titulo, subtitulo=None):
        """Sección: con caja (tarjetas) o con regla superior de 1 px (editorial, suizo). Devuelve el rectángulo útil."""
        if self.dos_capas: pass
        elif self.T.get('tarjetas', True): self.caja(x, y, w, h)
        else: self.linea(x, y, w)
        self.texto(x + 16, y + 8, w - 32, 32, [(titulo, self._pt('titulo_visual', 10) / .75 * 1.2, self.T['texto'], True)])
        if subtitulo:
            self.texto(x + 16, y + 40, w - 32, 24, [(subtitulo, 9 / .75, self.T['texto2'], False)])
            return (x + 8, y + 72, w - 16, h - 80)
        return (x + 8, y + 40, w - 16, h - 48)

    @staticmethod
    def filas_que_caben(alto, tam_pt=9, padding_fila=4, con_titulo=False, alto_imagen=0):
        """Filas de datos que caben en una tableEx de `alto` px sin barra (conservador: en la réplica, 10 pt + imagen de 20 px
        midió ~33 px por fila). alto_imagen = alto de la imagen SVG de la columna (grid.imageHeight), si hay."""
        fila = round(max(tam_pt / .75 * 1.5, alto_imagen) + 2 * padding_fila + 4)
        return max(1, int((alto - fila - (48 if con_titulo else 0)) // fila))

    def tabla_top(self, x, y, w, h, categoria, medidas, orden, n=None, prefijo='Top', anchos=None, alt=None):
        """tableEx SIN barra: muestra solo las n primeras categorías por `orden` (n = filas que caben si no se da). Devuelve las
        medidas a incrustar con scripts_modelo (rank + una medida «<prefijo> <medida>» por columna, en blanco fuera del top: la fila
        no aparece) [probado]. No hay filtro Top N guardado por el Desktop para copiar.
        categoria = (tabla, columna, encabezado); medidas = [(medida, encabezado)]; orden = medida que ordena."""
        n = n or self.filas_que_caben(h)
        t, c, enc = categoria; cat = f"'{t}'[{c}]" if ' ' in t else f'{t}[{c}]'
        rk = f'{prefijo} rank {orden}'
        nuevas = [{'nombre': rk, 'expr': f'IF(ISINSCOPE({cat}), RANKX(ALLSELECTED({cat}), [{orden}], , DESC, Dense))', 'formato': '0',
                   'carpeta': prefijo, 'descripcion': f'Posición por [{orden}] (para mostrar solo las {n} primeras).'}]
        roles = [(t, c, None, enc)]
        for m, e in medidas:
            nuevas.append({'nombre': f'{prefijo} {m}', 'expr': f'IF(ISINSCOPE({cat}) && [{rk}] <= {n}, [{m}])', 'carpeta': prefijo,
                           'descripcion': f'[{m}] solo para las {n} primeras categorías por [{orden}].'})
            roles.append((self.E, f'{prefijo} {m}', 'measure', e))
        objs = {'values': [{'properties': {'wordWrap': lit(False)}}], 'columnHeaders': [{'properties': {'wordWrap': lit(False)}}],
                'total': [{'properties': {'totals': lit(False)}}], 'grid': [{'properties': {'rowPadding': dnum(4)}}]}
        if anchos: objs['columnWidth'] = [{'properties': {'value': dnum(a)}, 'selector': {'metadata': q}} for q, a in anchos]
        self.p.agregar_visual(self.pag, 'tableEx', (x, y, w, h), roles={'Values': roles}, orden=(f'{self.E}.{prefijo} {orden}', 'desc')
                              if any(m == orden for m, _ in medidas) else None,
                              objects=objs, vcObjects={**marco(), **({'general': [{'properties': {'altText': lit(alt)}}]} if alt else {})})
        return nuevas

    def orden_lectura(self):
        """Orden de tabulación = orden de lectura (filas de 40 px de arriba abajo, de izquierda a derecha), guía §9. Llámalo al
        terminar la página: los visuales se crean en otro orden (cajas, valores, separadores)."""
        import json as _j
        conts = self.p.pagina(self.pag)['visualContainers']
        for i, c in enumerate(sorted(conts, key=lambda c: (round(c['y'] / 40), c['x'])), 1):
            cfg = _j.loads(c['config']); t = i * 1000
            c['tabOrder'] = t; cfg['layouts'][0]['position']['tabOrder'] = t; c['config'] = _j.dumps(cfg, ensure_ascii=False)

    def estado(self, x, y, w, h, medida_texto, medida_regla, casos=None, tam_pt=10):
        """Estado ícono + texto (sin píldora): medida de texto con ▲/▼/● y color por regla sobre una medida numérica.
        casos por defecto: >= 0 bien, < 0 mal."""
        casos = casos or [(2, 0, self.T['sube']), (3, 0, self.T['baja'])]
        return self.valor_card(x, y, w, h, medida_texto, tam_pt, regla_color=regla(self.E, medida_regla, casos), fuente=SEMI)

    def pie(self, x, y, w, fuente, medida_actualizado=None, ancho_medida=280):
        """Pie de confianza (guía §8): «Fuente: …» y, si hay, la medida «Actualizado al …» a la derecha."""
        T = self.T
        self.texto(x, y, w - (ancho_medida if medida_actualizado else 0), 24,
                   [('Fuente: ', 9 / .75, T['texto2'], False), (fuente, 9 / .75, T['texto'], True)])
        if medida_actualizado:
            self.valor_card(x + w - ancho_medida, y, ancho_medida, 24, medida_actualizado, 9, 'texto2', fuente=REG)

if __name__ == '__main__':
    print(__doc__.strip()); print('\n(módulo: se importa desde Python; ver SKILL.md)')
