# Editar el reporte

## API de `scripts/modificar_layout.py` (formato clásico) [probado]

```python
from modificar_layout import Pbix, lit, dnum, dint, color   # dint: enums numéricos ('1D'); lit(int): enteros ('8L')
p = Pbix('original.pbix')                        # lee Report/Layout
v = p.visual('Inventario', tipo='tableEx')           # buscar por página + tipo / vid / texto de título
v.titulo('Inventario – Movimientos', mostrar=True, tamaño=12, color_fondo='#F0391D', color_letra='#FFFFFF')
v.propiedad('vcObjects', 'border', {'show': lit(True), 'radius': dnum(8)})       # cualquier propiedad de formato
v.mover(y=206, h=504)                            # sincroniza contenedor y config.layouts
v.quitar_campo('FactMovimientos.DocumentoFiscal')
v.renombrar_ref('Sum(F.CostoUnitario)', 'Avg(F.CostoUnitario)')                  # corrige queryRef viejos
v.ordenar_rol('Values', [...queryRefs...])
v.gradiente('Sum(F.Cantidad)', 'F', 'Cantidad', 'Sum', minimo='#FFFFFF', maximo='#FFCD00')
p.agregar_filtro('Inventario', 'F', 'CodigoProducto')                                # "no está en blanco"; visual=v para nivel visual
s = p.agregar_pagina('Resumen', ancho=1280, alto=720, fondo='#FFF8E7')
p.agregar_visual('Resumen', 'card', (x, y, w, h), roles={'Values': [('F', 'Entrada', 'Sum', 'Entradas')]},
                 titulo='Entradas', objects={...}, vcObjects={...}, orden=('Sum(F.Entrada)', 'desc'))
                 # campo = (entidad, propiedad, agregación | None | 'measure', nombre visible)
p.clonar_visual(v, 'Intro', pos=(x, y, None, None))                              # z/tabOrder únicos
p.agregar_parte('DAXQueries/Medidas%20X.dax', texto.encode('utf-16-le'), extension='dax')
p.guardar('copia.pbix')                          # UTF-16 LE, DataModel STORED, sin SecurityBindings
```

## Páginas, vista y tema en clásico (sirve para Report Server)

```python
p.ordenar_paginas(['Portada', 'Roadmap de ventas', 'Inventario de movimientos', 'Roadmap - Ventas'], activa='Portada')
p.ocultar_pagina('Roadmap - Ventas')            # config.visibility = 1 [probado]
p.vista_pagina('Roadmap de ventas', 'FitToWidth')  # displayOption 1 FitToPage [probado], 2 FitToWidth, 3 ActualSize [por validar]
p.tema_personalizado(tema_json)                 # archivo = name del tema; customTheme + item 201 en RegisteredResources [probado RS 2026.05]
```

## PBIR [probado]

1. Construye la página con la API anterior sobre una copia **clásica** (el original sin convertir), en un temporal.
2. `pbir.visual_layout_a_pbir(contenedor)` convierte cada visual (resuelve alias → `Entity`).
3. Arma `page.json` (conserva `$schema` y `name` de la página existente para que los botones de navegación sigan válidos;
   `visualInteractions` con `"NoFilter"`).
4. `pbir.reemplazar_pagina(guardado.pbix, destino.pbix, page_id, page_json, visuales)` copia todo lo demás (modelo incluido).
Ver `ejemplos/roadmap_inyectar_pbir.py`.

## Patrones de formato que funcionan [probado en pantalla]

- Contenedor redondeado: `textbox` vacío con `vcObjects.background` + `border` (`radius` 8 se aprecia; 4 se ve cuadrado; 12–14 exagerado).
- Texto estático: `textbox` con `paragraphs[].textRuns[].textStyle` (`fontSize` en pt, `color`, `fontFamily`). Altura ≈ 1,6 × tamaño en px
  + 10, o aparece barra de desplazamiento.
- Valor dinámico grande: **`card` clásica** (`objects.labels`: fontSize, color, fontFamily; `categoryLabels.show=false`). Centrado.
- Color por reglas: `{"expr": {"Conditional": {"Cases": [{"Condition": {"Comparison": {...Measure...}}, "Value": {"Literal": ...}}]}}}`
  funciona en `card.labels.color`, en `values.fontColor` de tablas (selector `dataViewWildcard` + `metadata`) y en `dataPoint.fill`
  de columnas (selector `dataViewWildcard`).
- Barras de datos: `columnFormatting[].dataBars` (positiveColor, negativeColor, axisColor, reverseDirection, hideText).
- Matriz con valores en filas: `values.valuesOnRow = true`; sin subtotales: `subTotals.rowSubtotals/columnSubtotals = false`.
- Ocultar el deslizador del slicer de fechas: `objects.slider.show = false`.
- Fuentes: usar la pila completa, p. ej. `'Segoe UI Bold', wf_segoe-ui_bold, helvetica, arial, sans-serif`.
  `'Segoe UI Bold'` solo cae en una fuente con serifa.
- Interacción "ninguna" entre un slicer y un visual: `relationships` type 3 / `"NoFilter"`.

## Temas y páginas múltiples [probado]

- Tema inyectado con `tema_powerbi.aplicar_tema_pbir`: Desktop lo abre, lo aplica y lo conserva al guardar.
  `tema_powerbi.validar(tema)` lo revisa contra el catálogo (el CLI de `tema_powerbi.py` lo hace antes de escribir).
- **No pongas `padding` (ni `title.show`) en `visualStyles['*']['*']`**: el relleno global reduce el área de textbox y tarjetas y
  Power BI les pone barra de desplazamiento (los "cuadritos" a la derecha del texto). `tema_powerbi.py` ya lo evita.
- Varias páginas a la vez: `pbir.reemplazar_paginas(guardado, destino, {page_id: (page_json, visuales)}, orden, activa)`;
  `page_json_desde_seccion(..., oculta=True)` escribe `"visibility": "HiddenInViewMode"` (así la guarda Desktop).
- Para reutilizar un id de página del PBIR al construir en clásico, asigna `seccion['name'] = <id>` justo después de crearla.
- Los visuales que se conservan de una página deben subir de `z` si dibujas cajas/encabezados después (o quedan tapados).
- `displayOption: "FitToWidth"` escrito por nosotros volvió como `"FitToPage"` tras guardar en Desktop [observado, por validar
  si Desktop lo cambia o lo ignora].
- Botón de navegación con texto: `componentes.Lienzo.boton_nav` (actionButton + visualLink `PageNavigation`) [probado en
  pantalla, nube 2026.09; RS por validar].

## Antes de escribir una propiedad: el catálogo [probado]

`python scripts/catalogo.py propiedades <tipo> <objeto>` dice si existe, su tipo y sus valores. Lo que no está en el catálogo
el Desktop de la nube lo **borra al guardar** (visuales) o lo ignora (tema). `verificar_pbix.py` valida siempre con el catálogo.
Casos corregidos en v6: `actionButton.outline.roundEdge` → `shape.roundEdge`; `columnHeaders.outline`/`rowHeaders.outline` no
existen (es `outlineStyle`, por validar); en temas, `scatterChart` no tiene `labels` (usa `categoryLabels`).

## Lo que el Desktop borra al guardar [probado: nube 2026.09 y RS 2026.05]

El Desktop de la nube y el Desktop para Report Server 2026.05 **eliminan al guardar** las propiedades de visual que no están en el esquema (sin aviso), y conserva las
del tema. Visto con `actionButton.outline.roundEdge` y `tableEx.columnHeaders.outline` (un archivo generado comparado con el mismo
archivo vuelto a guardar). **Síntoma útil**: si una propiedad que escribiste desaparece tras guardar, es inválida;
compara antes/después con `catalogo.py validar`. Queda como
`borrado_al_guardar` en `catalogo/_evidencia.json`.

## Título o texto dinámico de una línea [probado: RS 2026.05]

`cardVisual` con una medida de texto en una caja baja (36–48 px) sale **cortada** (solo asoma el borde superior de las letras),
aun con `padding` Custom 0. Usa la `card` clásica (valor centrado) con el ancho del texto medido
(`powerbi-report-author text measure "…" --size 16 --weight semibold`) para que quede casi alineada a la izquierda.
`cardVisual.value.customFormatString` lo **ignoró** el Desktop para RS 2026.05: el formato sale de la medida (usa una medida
de presentación con `formatString` si el modelo no la trae).

## Unidades de visualización [probado: Desktop para RS 2026.05 en español]

`labelDisplayUnits` en «auto» (0) abrevia con el idioma del Desktop: «$152 mil», «21 mil», ejes «$40 mil», aunque el formato
acordado sea `$1,234.56`. Usa unidades «ninguna» (`dint(1)`) y el formato de la medida o `customFormatString` (cardVisual:
`value.customFormatString`). Si hay que compactar, una medida de presentación con `$#,0.0,,"M"` o `#,0,"K"`.

## Lo que Power BI ignoró en pantalla (aunque lo conserva en el archivo)

- `multiRowCard.dataLabels` (tamaño y color del valor) → usar `card` clásica.
- `categoryAxis.show = false` en `clusteredColumnChart`.
- `showAxisTitle` debe ponerse explícito; si no, aparecen "Mes" y el nombre de la medida.
- Texto que no cabe en su caja (textbox, tarjeta de varias filas) → barra de desplazamiento; usa `componentes.alto_min()`.

## Verificación antes de entregar

ZIP íntegro (`testzip`), DataModel idéntico, cada `Measure`/`Column` existe en el modelo (o en el script DAX pendiente), selectores
con queryRef presente, ids y z únicos por página, visuales dentro de la página, `navigationSection` a páginas existentes,
interacciones con ids existentes y, en PBIR, ninguna ruta JSON que Desktop no escriba. Luego pide captura al usuario.
