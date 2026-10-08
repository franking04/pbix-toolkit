# Catálogo de visuales nativos de Power BI

Cómo elegir el visual de Power BI según el trabajo del dato y quién lo lee. **Roles, objetos y propiedades (con tipo y valores
de enum) no se listan aquí: están en `references/catalogo/`** (57 visuales nativos, del CLI oficial de Microsoft
`@microsoft/powerbi-report-authoring-cli` 0.5.0 + `@microsoft/powerbi-core-visual-schema` 0.1.1). Consulta:
```
python scripts/catalogo.py propiedades <tipo> [objeto]     # objetos / propiedades con tipo y valores
python scripts/catalogo.py buscar <tipo> <regex>             # p. ej. buscar tableEx "width|wrap"
python scripts/catalogo.py plantilla <tipo>                  # esqueleto visual.json con sus roles
python scripts/catalogo.py validar archivo.pbix [--destino=rs:2026.05]
```
`_indice.json`: deprecado, nombre que guarda el Desktop (`table` → `tableEx`, `matrix` → `pivotTable`), si la skill lo usa,
soporte en servicio y en Report Server (`no` | `desde AAAA.MM` | `sí`). `_evidencia.json`: por propiedad, si el Desktop la
**guardó** (servicio/RS), si se **ve** en pantalla o si Power BI la **ignora**. Niveles de evidencia: esquema < guardado < se ve.
[probado] El catálogo da 0 errores sobre archivos escritos solo por el Desktop (Desktop de la nube 2025.01 con 578 objetos y Desktop para RS 2026.05
en Layout clásico): sirve también como referencia para Report Server.
[probado] El Desktop de la nube 2026.09 **borra al guardar** las propiedades de visual que no están en el esquema
(p. ej. `actionButton.outline.roundEdge`, `tableEx.columnHeaders.outline`), pero conserva las del tema.
`visuales_observados.json` queda como inventario histórico de lo leído en archivos reales.

## Tabla de decisión: trabajo del dato → visual

| Trabajo que hace el lector | Visual de Power BI (`visualType`) | Evitar |
|---|---|---|
| Ver un número y si va bien | `card` (clásica) · `cardVisual` (tarjeta nueva) · `kpi` | gráfico de una sola barra |
| Varios números titulares | fila de `card` o `cardVisual` con varias medidas | `multiRowCard` como KPI (ver notas) |
| Avance contra meta | `gauge` (con `target`) · barra + línea de referencia | gauge para series de tiempo |
| Comparar magnitudes entre categorías | `clusteredBarChart` (horizontal, nombres largos) · `clusteredColumnChart` | pie con > 5 porciones |
| Tendencia en el tiempo | `lineChart` · `areaChart` (una serie) · columnas si son pocos periodos | eje con fecha larga (ver formatos) |
| Destacar una serie entre varias | `lineChart`/barras con color por reglas (énfasis: una en color, resto gris) | muchas series a color |
| Parte de un todo | `stackedBarChart` / `hundredPercentStackedBarChart` · `donutChart` ≤ 4 partes | pie de muchas porciones |
| Puente entre dos totales (P&L, variaciones) | `waterfallChart` | columnas apiladas |
| Embudo o etapas | `funnel` | barras sin orden |
| Relación entre dos medidas | `scatterChart` (X, Y, Size, Play) | dos ejes Y |
| Dos medidas de distinta escala | dos visuales alineados o índice base 100 | `lineClusteredColumnComboChart` con eje Y2 (doble eje) |
| Detalle a nivel registro | `tableEx` | matriz para listas planas |
| Cruce filas × columnas, jerarquías, estados financieros | `pivotTable` (matriz) | tabla con columnas repetidas |
| Explicar qué compone un total | `decompositionTreeVisual` | 6 visuales de desglose |
| Navegar | `actionButton`, `image` con `visualLink`, `bookmarkNavigator`, `pageNavigator` | botones sin texto alternativo |
| Filtrar | `slicer` (lista, desplegable, entre fechas) · `advancedSlicerVisual` (botones) | más de 4 slicers visibles |
| Texto, títulos, explicación | `textbox` | títulos dentro de imágenes |
| Fondos y separadores | `textbox` vacío con fondo/borde, `basicShape`, `shape` | imágenes de fondo con texto |

## Notas de uso por visual (lo que el catálogo no dice)

- **`card` (clásica)**: valor centrado, sin alineación horizontal; acepta texto (medidas con `FORMAT()`); color por reglas en
  `labels.color` [probado]. Para KPI grandes en reportes ejecutivos. `labelDisplayUnits` con `dint(1)` = unidades completas [probado].
- **`multiRowCard`**: `dataLabels` existe en el esquema pero Power BI lo **ignora** en pantalla (tamaño y color) y pone barra de
  desplazamiento si no cabe [probado] → no para KPI ni títulos. No está deprecada en el catálogo.
- **`cardVisual`** (tarjeta nueva): alineación, varias medidas, referencia. En Report Server desde 2026.05. Nunca guardada por
  nuestros Desktop todavía: `horizontalAlignment`/`layout.alignment` son tipo `formatting` (valores por validar) [por validar].
- **Columnas/barras**: pon `showAxisTitle: false` explícito; `categoryAxis.show=false` fue ignorado [probado]. Barras horizontales
  para nombres largos; columnas para tiempo. Color por reglas en `dataPoint.fill` con `dataViewWildcard` [probado].
- **`lineClusteredColumnComboChart`**: doble eje → solo si comparten unidad o la línea es meta.
- **`tableEx`**: anchos con `columnWidth` (por queryRef) que sumen ≤ ancho − 20 px, o aparece barra horizontal [probado, captura]; encabezados legibles con `columnProperties.displayName`. Color por reglas en `values.fontColor` con selector
  `dataViewWildcard` + `metadata` [probado]. En `columnHeaders` no existe `outline` (es `outlineStyle`, número de banderas, valores
  por validar). `columnFormatting.styleHeader=false` para que el formato por columna no pinte el encabezado [por validar].
- **`pivotTable`**: `values.valuesOnRow` [probado]. Con valores en filas, las reglas de color en `values` (selector por medida)
  también pintaron los **encabezados de columna** [probado: captura]. Ancho fijo: `columnHeaders.autoSizeColumnWidth=false` +
  `defaultColumnWidth` [por validar].
- **`slicer`** (clásico): `slider.show=false` oculta el deslizador [probado]; en mosaico (`data.mode` `Basic` + `general.orientation`)
  se colorea con `items.background/fontColor` y `general.outlineColor`; **no tiene propiedad para el estado seleccionado**.
  `advancedSlicerVisual` (botones, RS desde 2026.05) sí tiene estados y `accentBar` (barra de color del ítem) [visto].
- **`textbox`**: contenedor redondeado con `background` + `border.radius` [probado]; altura mínima `componentes.alto_min()`;
  el CLI avisa con un piso más alto (`piso_cli`), 28–32 px con 8.6–9.4 pt no mostraron scroll [probado].
- **`actionButton`** + `visualLink` PageNavigation: botón de navegación con texto [probado: captura]. El redondeo va en
  `shape.roundEdge` (entero), no en `outline`.
- **Visuales personalizados** (`Report/CustomVisuals/`, p. ej. htmlContent): no están en el catálogo; prefiere nativos.

## Funciones de Power BI que cambian el diseño

| Función | Para qué | Nota |
|---|---|---|
| Página de información sobre herramientas (tooltip page) | detalle al pasar el mouse sin ocupar lienzo | `vcObjects.visualTooltip.section` [visto] |
| Obtener detalles (drillthrough) | de un resumen a una página de detalle | página con campo de drillthrough [conocido] |
| Marcadores + navegador | vistas alternas (tabla/gráfico), secciones | `bookmarkNavigator` [visto] |
| Parámetros de campo | el usuario elige la medida/dimensión del eje | requiere tabla de parámetros en el modelo [conocido] |
| Jerarquías y profundizar | año → trimestre → mes | `HierarchyLevel` en proyecciones [visto] |
| Formato condicional | semáforos, barras de datos, iconos, color por reglas | ver `edicion_reporte.md` |
| Diseño móvil | versión vertical para celular | por validar |
| Tema del reporte (JSON) | colores, fuentes y estilos por tipo de visual de una vez | `scripts/tema_powerbi.py` |
