# Efectos visuales en Power BI: qué hay, dónde vive y si sirve en Report Server

Catálogo para los niveles **realzado** e **impactante** (`guia_diseno.md` §11). Los nombres de objeto y propiedad salen del
catálogo del CLI de Microsoft (`catalogo/`, que describe la nube y PBIR). Para Report Server vale lo que diga
`plataformas.json` y las pruebas en el Desktop para RS. Etiquetas: **[probado]** con archivo real · **[por validar]** sin evidencia en RS todavía.

## 1. Nativos (sin visuales personalizados)
Regla de selectores [probado]: `glow`/`glowCustom` van **sin** selector; `fill` de shape y `shadowCustom` de cardVisual,
**con** `selector: {id: 'default'}`; actionButton `fill`/`text`/`icon`: `show` sin selector + propiedades con `selector.id default`.
| Efecto | Dónde | Objeto · propiedades | Nivel | Report Server |
|---|---|---|---|---|
| Visual transparente (para 2 capas) | todos | `vcObjects.background.show = false`; `border.show = false` (lo pone el tema de aurora/vidrio) | impactante | sí [probado]: card, columnas y tabla transparentes sobre la imagen (RS y nube) |
| Sombra suave | todos | `vcObjects.dropShadow`: show, preset (Bottom…), color, transparency, shadowBlur, shadowDistance, shadowSpread, position | realzado | sí en RS 2026.05 y nube (sobre fondo claro; una sombra negra no se nota sobre fondo oscuro) [probado: ronda 2] |
| Radio de esquinas | todos | `vcObjects.border.radius` (un solo radio en todo el reporte) | realzado | sí [probado] |
| Glow (resplandor) | actionButton, shape, pageNavigator, bookmarkNavigator | `glow`: show, color, transparency, shadowBlur | realzado | sí, **sin selector** (`glow: [{properties: {show, color, …}}]`) en actionButton y shape [probado: ronda 2]; con `selector.id default` no se dibuja |
| Glow y sombra de tarjeta | cardVisual, advancedSlicerVisual, listSlicer | `glowCustom` / `shadowCustom` (color, transparency, shadowBlur, glowSpread, glowDistance…) | realzado | cardVisual: `glowCustom` **sin selector** sí (tenue) y `shadowCustom` con `selector.id default` sí [probado: ronda 2]; listSlicer [por validar] |
| Barra de acento | cardVisual | `accentBar`: show, position, color, width (selector id default) | realzado | sí en RS 2026.05 y nube [probado] |
| Imagen en tarjeta (p. ej. medida SVG) | cardVisual | `cardImage`: show, imageType `imageUrl`, imageUrl = `{expr: {Measure: …}}`, imageUrlFit (selector id default) | realzado | sí: la medida SVG se dibuja como imagen de la tarjeta en RS 2026.05 y nube [probado] |
| Botones con estados | actionButton | `fill`, `text`, `icon`, `outline`, `shadow`, `glow` por estado (por defecto / al pasar / presionado / seleccionado) | realzado | el Desktop para RS 2026.05 guarda el estado «al mantener el puntero» como `selector: {id: 'hover'}` (botón hecho a mano) [probado]; `fill.show` sin selector + `fillColor` por estado. Id de «presionado»: [por validar] |
| Degradado por valor | tableEx, pivotTable, barras/columnas | formato condicional de fondo o fuente con escala de colores | sobrio+ | [probado] (formato condicional existe en RS) |
| Degradado del trazo | lineChart, areaChart | `segmentGradient` | realzado | [por validar] qué dibuja y desde qué release |
| Fondo de página imagen | página | `objects.background.image` (ResourcePackageItem) + `transparency`; `outspace` = papel tapiz | impactante | sí: imagen 1920×1080 con ajuste Fill en página 1280×720, nítida y sin recorte, en RS 2026.05 y nube [probado] |

## 2. Medidas SVG (sin visuales personalizados) — `scripts/svg_medidas.py`
Medida que devuelve `data:image/svg+xml;utf8,<svg…>` con categoría de datos **ImageUrl** (va en el script TMDL; crear la medida
con esa categoría desde la pestaña incrustada [probado: Desktop para RS 2026.05 y Desktop de la nube 2026.09]).
Se dibuja en tableEx/pivotTable (columna de imagen; tamaño en Cuadrícula → Imágenes), card, cardVisual (imagen) e image.
**Por defecto sin cifras** (`cifras=False`): la píldora es fondo + flecha y el anillo no lleva %; la cifra va nativa
al lado (formatString), porque un texto dentro del SVG no sigue la configuración regional del lector (`USERCULTURE()` no coincide con
los formatString en RS [probado]). `cifras=True` pone el texto con la cultura del modelo (`cultura='modelo'`).
Generadores: `pildora` (Δ con flecha, polaridad), `bullet` (avance vs meta), `anillo` (avance; % al centro solo con cifras=True),
`sparkline` (tendencia por fila sobre los periodos visibles), `progreso`. La vista previa usa la misma plantilla que el DAX
y la misma codificación (`%`→`%25`, `#`→`%23`) [probado en navegador: 0 imágenes rotas].
Dónde se dibuja [probado], igual en RS 2026.05 y nube: **tableEx** (columna de imagen; alto/ancho en `grid.imageHeight/imageWidth`) y **cardVisual con `cardImage.imageUrl` = medida**. **No** se dibuja en la `card` clásica ni como valor (`Data`) de cardVisual: muestra el texto `data:image/svg+xml…`. Los colores del SVG salen de la dirección con que se generó: usa la misma dirección que el tema (un SVG de `moderno` sobre `aurora` deja el texto invisible).

## 3. Visuales personalizados (permitidos: Deneb incluido)
| Visual | Para | Reglas | Report Server |
|---|---|---|---|
| **Deneb** (certificado) | 1–2 visuales firma: área con degradado, anillo, bullet por categoría, mancuerna | plantillas Vega-Lite en `deneb/<dirección>/` generadas con `scripts/deneb.py` (compilan y se dibujan con vega-lite 6.4.3 [probado]; formato de números con `pbiFormat` por defecto (sigue la cultura, como el resto del reporte; exige `config.customFormatTypes: true`); `--formato d3` fija estilo US (`$,.1f`, `,.0f`, `.0%`) solo si se pide un locale fijo); campos renombrados en el visual como pide la plantilla; textos con `formatType: pbiFormat`; fondo del visual apagado en 2 capas | sí [probado]: área con degradado en RS 2026.05 (pbiviz importado desde archivo; viaja en `Report/CustomVisuals/`) y en la nube (AppSource). Se guarda como `visualType` `deneb7E15AEF80B9E4D4F8E12924291ECE89A` con `objects.vega.jsonSpec`. `pbiFormat` usa la cultura del modelo |
| **HTML Content** | bloques de texto enriquecido, tarjetas HTML | sin recursos externos; contraste igual que lo nativo | observado en un archivo guardado por el Desktop para RS 2026.05; render en el servidor [por validar] |

## 4. Lo que Power BI no hace (y cómo se logra)
| Deseo | En Power BI | Alternativa |
|---|---|---|
| Desenfoque tipo vidrio, degradados de página, luces | no | capa de decoración como imagen de fondo (`capas_html.js` + `fondo_pagina.py`) |
| Sombra de texto, espaciado de letras | no | peso y tamaño; nunca en la imagen detrás de cifras |
| Animaciones y transiciones | no (salvo dentro de Deneb) | nada; el reporte se lee quieto |
| Fuentes web | no | fuentes del sistema (Segoe UI y familia) |
| Degradado dentro de barras nativas | no | Deneb o medida SVG |

## 5. Cómo validar un efecto [por validar]
Antes de usar un efecto [por validar] en un diseño por defecto: aplícalo en una copia, ábrela en el Desktop del release de
destino, guarda, vuelve a abrir (si la propiedad desaparece, no es válida) y publica en el servidor si el destino es RS. Según
el resultado, cambia aquí su etiqueta a [probado] o a «no soportado».
