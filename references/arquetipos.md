# Arquetipos de página (estructura, no estilo)

El estilo (colores, tipografía, forma) sale de una dirección fija o de `estilo_a_medida.py`; **la estructura sale de aquí**.
Dos diseños con el mismo arquetipo y distinto color se perciben iguales: para que un reporte se sienta distinto, cambia el
arquetipo antes que el color. Se elige por la **premisa** (qué decide el público), no por gusto. `registro_disenos.py` avisa si el
arquetipo y el estilo repiten los últimos diseños.

Rejilla 1280×720 (`tokens.json`): margen 24, 12 columnas de 88, medianil 16 → ancho de n columnas = 104·n − 16
(3 = 296, 4 = 400, 6 = 608, 8 = 816, 9 = 920, 12 = 1232). Cabecera y = 16–96, pie y = 688–712. Posiciones múltiplos de 8.
Report Server: lo que dice cada fila vale para RS 2026.05 en formato clásico; «nativo» = sin visuales personalizados.

| # | Arquetipo (slug) | Premisa: el público decide… | Héroe y ruta de lectura | Rejilla (cuerpo y = 112–672) | Visuales | RS |
|---|---|---|---|---|---|---|
| 1 | **Héroe + tira** (`heroe_tira`) | si el negocio va bien en general | cifra héroe → tira de 3–4 KPI → tendencia → ranking | héroe 4 col + tira 8 col (alto 112) · tendencia 7 · ranking 5 | cardVisual, lineChart, barChart | nativo [probado] |
| 2 | **Titular + gráfico** (`titular_grafico`) | si una conclusión concreta es cierta | titular-conclusión 21–27 pt → UN gráfico anotado de 9–12 col → 2–3 notas al margen | titular 12 (alto 96) · gráfico 9 × 480 · notas 3 col | lineChart/columnChart + textbox con anotaciones, línea de referencia rotulada | nativo |
| 3 | **Excepciones** (`excepciones`) | qué atender hoy | franja de estados (✓ ! ✕) → lista de acción ordenada por urgencia → contexto | franja 12 (alto 72) · lista 8 · contexto 4 | card de texto con ícono, tableEx con formato condicional | nativo [probado] |
| 4 | **Puente** (`puente`) | por qué cambió una cifra de A a B | A y B grandes a los lados → cascada o contribución divergente en medio → tabla de rubros | A 2 col · puente 8 · B 2 col; tabla debajo | waterfallChart o barChart divergente, pivotTable | nativo |
| 5 | **Small multiples** (`small_multiples`) | qué entidad se comporta distinto | rejilla de 6–12 mini gráficos con misma escala → la anómala resaltada con acento | 3×2 o 4×3 celdas iguales; filtros en columna izquierda 2 col | lineChart small multiples (o N lineChart con eje fijo) | small multiples [por validar] en RS; N visuales sí |
| 6 | **Mapa de calor** (`mapa_calor`) | dónde y cuándo se concentra algo | matriz tiempo × entidad de un tono → totales al margen → nota del patrón | matriz 9 col × 480 · margen 3 col con ranking | pivotTable con escala `secuencial` | nativo [probado: formato condicional] |
| 7 | **Embudo por etapas** (`embudo_etapas`) | en qué etapa se pierde | etapas de izquierda a derecha con conversión entre ellas → detalle de la etapa crítica | 4–6 bloques en fila (alto 200) · detalle 12 abajo | cardVisual por etapa + flechas (shape), funnel o barChart, tableEx | nativo |
| 8 | **Riel lateral** (`riel_lateral`) | lo mismo que 1, con aspecto de aplicación | riel 3 col (KPI apilados y filtros) → lienzo 9 col con 1 gráfico grande + 1 secundario | riel 3 × 576 · lienzo 9 | cardVisual, slicers, lineChart/areaChart | nativo; riel con color = forma o 2 capas |
| 9 | **Cuadro de metas** (`scorecard`) | qué metas se cumplen | tabla protagonista: una fila por KPI con real, meta, bullet, tendencia y estado | tabla 12 × 480 · resumen 12 (alto 72) arriba | tableEx con medidas SVG (`bullet`, `sparkline`, `pildora`) | [probado] SVG en tableEx |
| 10 | **Ranking** (`ranking`) | quién lidera y quién cae | barras largas top N con posición y cambio de puesto → resto agrupado → ficha del seleccionado | ranking 7 col × 528 · ficha 5 col | barChart ordenado, card de texto ▲▼ puestos, tooltip de página | nativo |
| 11 | **Espejo A vs B** (`ab_espejo`) | entre dos opciones/periodos/regiones | dos columnas simétricas con las mismas cifras → diferencia al centro | 5 col · centro 2 col · 5 col | cardVisual, barChart espejo (dos barChart, uno invertido) o mancuerna Deneb | nativo; mancuerna con Deneb [probado Deneb en RS] |
| 12 | **Calendario** (`calendario`) | qué días/semanas fallan | calendario mensual o año (semanas × días) con color → lista de días críticos | calendario 8 col · lista 4 | pivotTable días × semanas con escala de color | nativo |
| 13 | **Bento** (`bento`) | resumen variado para dirección | mosaico asimétrico: 1 bloque grande, 2 medianos, 3 chicos, cada uno con una idea | bloques 6×2 + 3×1 + 3×1 + … (sin dos iguales en fila) | cardVisual, gráficos mini, medidas SVG | nativo; con 2 capas para paneles |
| 14 | **Portada / menú** (`portada_menu`) | a dónde ir y el estado general | frase de impacto → 3 cifras → mosaicos de navegación con estado | frase 8 col · cifras 4 · 3–5 mosaicos abajo | textbox, cardVisual, actionButton con estados → páginas | [probado] botones con hover |
| 15 | **Narrativa vertical** (`narrativa_vertical`) | entender una historia completa | página alta que se desplaza: secciones conclusión → gráfico → nota, como un artículo | ancho 1280, alto 1600–2400; vista «ajustar al ancho» | cualquiera nativo | alto de página personalizado [por validar en RS] |
| 16 | **Detalle protagonista** (`detalle_tabla`) | conciliar o buscar registros | filtros en fila → saldos (inicial, entradas, salidas, final) → tabla grande | filtros 12 (alto 56) · saldos 12 (alto 88) · tabla 12 | slicers, card, tableEx | nativo [probado] |
| 17 | **Cifra única** (`cifra_unica`) | una sola cosa, de lejos (TV/mural) | número de 60–96 pt + estado + una línea de contexto | cifra centrada 8 col · contexto debajo | card/cardVisual con fuente grande | nativo |
| 18 | **Territorio** (`territorio`) | dónde está el problema geográficamente | mapa coroplético o de mosaicos → ranking lateral | mapa 8 · ranking 4 | filledMap/shapeMap; sin Internet: mosaicos (matriz) o Deneb | mapas con teselas de Internet **no recomendados en RS** [por validar]; mosaicos sí |

## Cómo elegir
1. Escribe la premisa (guía §2). Busca en la columna «Premisa» la que la responde; si caben dos, genera una variante con cada una.
2. Descarta los que el medio impide: mural/TV → 3, 17, 13; PDF/impresión → 2, 9, 15 se leen bien, evita 8 (riel oscuro) y 2 capas
   oscuras; celular → diseño de página móvil aparte.
3. `python scripts/registro_disenos.py comparar …`: si el arquetipo coincide con los últimos 3 diseños del registro **de otro
   reporte**, elige otro salvo que el brief lo justifique (anótalo en la ficha). Las páginas de un mismo reporte sí comparten estilo,
   pero no necesitan el mismo arquetipo: una suite típica = portada (14) + resumen (1, 8 o 13) + análisis (4, 5 o 6) + detalle (16).
4. `heroe_tira` es el arquetipo más usado: elígelo solo si de verdad es el que mejor responde, no por costumbre.

## Combinaciones con estilo y nivel (ideas, no reglas)
- `titular_grafico` + carácter `calido` o `premium` + Georgia en el titular → informe de comité con aire editorial.
- `riel_lateral` + 2 capas oscuras (riel con luz del acento) → producto/app para dirección comercial.
- `bento` + `energico` claro con radios amplios → resumen de campaña o lanzamiento.
- `scorecard` + `tecnico` (Light en cifras, sin tarjetas) → seguimiento de metas para analistas.
- `cifra_unica` + oscuro `sereno` → pantalla de sala sin estridencia.
- `portada_menu` + 2 capas claras con una luz detrás de la frase → portada de suite.
