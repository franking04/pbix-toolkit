# Diseños de referencia

> **No son plantillas.** Enseñan técnicas (2 capas, SVG, Deneb, reglas, tiras de KPI) y sirven de banco de pruebas para las
> puertas. Un reporte nuevo parte de su propia idea (`../guia_diseno.md` §2b): arquetipo de `../arquetipos.md`, estilo de
> `../../scripts/estilo_a_medida.py` e inspiración de `../inspiracion.md`. Los generadores aceptan cualquier dirección:
> `PBIX_TOKENS_EXTRA=estilos/x.json python -c "import d_ejecutivo; d_ejecutivo.build('x', 'salida.html')"` [probado:
> estilos a la medida, 0 errores en `revisar_html.js`]. Están en el registro de `registro_disenos.py` para que una propuesta no los copie.

Un HTML por tipo de reporte, lienzo **1280 × 720** (= página de Power BI), datos **ficticios**, con su **ficha de decisiones**
debajo del lienzo. Tecla **m** (o el botón): muestra sobre cada bloque el visual de Power BI que lo replica (`data-pbi`).
Tokens: `../tokens.json` (misma fuente que el tema). Fuente regenerable: `_fuente/` (`python d_ejecutivo.py`, …;
`node capturar.js x.html` para PNG). Puertas: `node ../../scripts/revisar_html.js *.html` → 0 errores en todos con Segoe UI real (Windows + Edge) [probado];
las puertas incluyen texto recortado, texto que se sale de su visual, etiquetas SVG cortadas y píldoras partidas en 2 líneas.
Sin navegador de playwright, los scripts usan Microsoft Edge (`channel: 'msedge'`). Tablas con `line-height: 1.3` fijo para que
la altura de fila no dependa de la fuente (con Segoe la fila Total de las tablas de 2 capas se salía 4–8 px de su caja).

| Tipo | Archivo | Dirección | Premisa (resumen) |
|---|---|---|---|
| Ejecutivo | `ejecutivo.html` | moderno | crecimiento vs costo: héroe Ventas + tira de secundarios, título-conclusión, tendencia vs año anterior con etiqueta final, ranking con énfasis |
| Financiero | `financiero.html` | editorial | desvíos vs presupuesto: tira de KPI sin cajas con Utilidad neta héroe, matriz de cuentas con favorabilidad ▲▼, cascada |
| Operativo | `operativo.html` / `operativo_grafito.html` | moderno / grafito (mural) | actuar sobre excepciones: franja de estados ícono+texto, lista de acción por urgencia, actividad con hoy destacado |
| Analítico | `analitico.html` | suizo | qué explica el cambio: filtros en columna, small multiples misma escala, dispersión con énfasis, matriz de un tono, ± con eje en cero |
| Detalle | `detalle.html` | suizo | conciliar movimientos: filtros en fila, saldos inicial/entradas/salidas/final, tabla protagonista legible |

### Por nivel de impacto (guía §11–§12)
No son plantillas para copiar: muestran **qué técnicas** usa cada nivel. Cada pedido parte de su premisa y su público.
| Nivel | Archivo | Dirección | Premisa y técnicas |
|---|---|---|---|
| Realzado (1 capa) | `comercial_realzado.html` | moderno | ¿llegamos a la meta del mes?: pestañas con estados, tarjetas con sombra y barra de acento, día actual resaltado, píldoras y bullets SVG por cliente |
| Impactante (2 capas) | `comite_aurora.html` + `_fondo.png` + `_visuales.json` | aurora | ¿vamos arriba del plan?: luces detrás del héroe y del cierre, paneles vidrio, cifra de impacto con anillo, área con degradado (Deneb), tabla de regiones con píldoras y bullets SVG |
| Impactante (2 capas) | `ejecutivo_vidrio.html` + `_fondo.png` + `_visuales.json` | vidrio | ¿mejoró la utilidad y por qué?: héroe vertical con área, contribución divergente en vez de cascada, sparklines SVG por unidad |
En los de 2 capas, `_fondo.png` es la imagen que va de fondo de la página (`fondo_pagina.py`) y `_visuales.json` la posición
exacta de cada visual (coordenadas de Power BI).

Todos llevan pie de confianza (fuente · actualizado · definiciones ⓘ). Reglas completas: `../guia_diseno.md`.

## Mapa HTML → Power BI
| Bloque | Visual (clásico y PBIR) | Notas |
|---|---|---|
| kicker, título, subtítulo | `textbox`; título-conclusión y periodo como `card` de texto con medida DAX | tipo oración; ≥ `alto_min` |
| filtros en caja | `slicer` Dropdown/Between; botones = `advancedSlicerVisual` (RS ≥ 2026.05) | mismo lugar en todas las páginas |
| KPI héroe | fondo (`shape` o fondo del visual) + `card` 27 pt + `card` de texto Δ con ícono y color por regla + `lineChart` mini | polaridad del KPI decide el color |
| tira de KPI | `card` + `card` de texto por KPI, separadores `shape` línea 1 px | sin cajas en editorial/suizo |
| línea actual vs anterior | `lineChart` 2 medidas (anterior en `contexto`), etiqueta solo en el último punto, sin leyenda | nunca eje Y2 |
| ranking con énfasis | `barChart` orden desc., etiquetas, sin eje X, color por regla (resto `contexto_suave`) | |
| matriz financiera | `pivotTable`, subtotales semibold con regla, Var con ícono y color por favorabilidad | |
| cascada | `waterfallChart` (aumento `bien`, disminución `mal`, total `tinta2`) | |
| estados | `card` de texto con ✓ ! ✕ y color por regla | nunca solo color |
| lista de acción | `tableEx` ordenada por urgencia, estado con ícono+texto | |
| columnas con hoy | `columnChart` + regla de color por fecha, etiqueta solo en hoy | |
| small multiples | `lineChart` small multiples (validar RS) o 3 `lineChart` con eje fijo | |
| dispersión | `scatterChart` con punto destacado por regla | |
| mapa de calor | `pivotTable` escala de fondo un tono (`secuencial`), texto blanco solo en los 2 tonos oscuros | |
| variación ± | `barChart` color por signo, eje en cero | |
| tabla de detalle | `tableEx` anchos fijos, `displayName` legibles, unidad en el encabezado, signo −, totales con regla | |
| pie de confianza | `textbox` + `card` de texto (Actualizado) + `actionButton` ⓘ → tooltip/página de definiciones | |
| decoración (luces, degradado, línea de luz) y paneles vidrio | **imagen de fondo de la página** (`capas_html.js` → `fondo_pagina.py`) | 2 capas; visual encima sin fondo ni borde |
| cifra de impacto 36 pt | `cardVisual` (o `card`) sin fondo; `glowCustom` se guarda pero aún no se vio [sin evidencia] | una por página |
| anillo de avance | medida SVG `svg_medidas.anillo` como **imagen** de cardVisual (`cardImage.imageUrl` = medida) o en `tableEx`; o Deneb `anillo.json` | [probado RS 2026.05 y nube]; nunca en `card` clásica ni como valor |
| píldora Δ, bullet, sparkline en tabla | `tableEx` con medidas SVG (`dataCategory: ImageUrl`) | tamaño de imagen = SVG |
| área con degradado | Deneb `area_degradado.json`; alternativa nativa `areaChart` con transparencia | 1–2 Deneb por página |
| contribución divergente | `barChart` con color por regla (verde suma, rojo resta), orden por impacto | más legible que una cascada con base alta |
| pestañas | 3 `actionButton` con estados (por defecto / al pasar / seleccionado) → navegación de página | |
| tarjeta con sombra y barra de acento | `cardVisual` (`shadowCustom`, `accentBar`) o `dropShadow` del contenedor | RS ≥ 2026.05 para cardVisual |
