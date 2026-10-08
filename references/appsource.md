# Visuales de AppSource (personalizados): cuándo y cuáles

Permitidos cuando lo nativo, el SVG o la imagen de fondo no alcanzan (`traductor_powerbi.md`). Cada visual personalizado suma peso,
mantenimiento y riesgo: **máximo 1–2 tipos por reporte**, y siempre con una alternativa nativa anotada en la ficha.

## Criterios (en este orden)
1. **Certificado** («Power BI Certified»): Microsoft prueba que no accede a servicios ni recursos externos. Con datos sensibles,
   solo certificados. Cómo verlo: en Power BI, *Obtener más objetos visuales* → filtro *Certificado de Power BI* (insignia azul);
   en AppSource, insignia amarilla «PBI Certified». La lista cambia: **comprobarlo al usarlo**, no de memoria.
2. **Sin licencia de AppSource**: los visuales con licencia (compra ligada a Entra ID) **no funcionan en Report Server**.
   Los que piden su propia clave o muestran marca de agua en la versión gratis, tampoco sirven para un reporte de empresa.
3. **Sin Internet**: nada que cargue teselas de mapas, fuentes, imágenes o API externas (en RS y con datos sensibles, no).
4. **Funciona en la plataforma**: Report Server trae una versión fija del API de visuales; un .pbiviz más nuevo puede no cargar.
   Se importa **desde archivo** en el Desktop para RS y viaja dentro del .pbix (`Report/CustomVisuals/`) [probado con Deneb].
   Probar en el Desktop para RS y en el portal antes de prometerlo; los visuales organizacionales no existen en RS.
5. **Accesible y legible**: contraste, tamaños ≥ 9 pt, colores del tema (muchos no heredan el tema: configurarlos con los tokens).

## Lista curada (candidatos; comprobar insignia y versión al usar)
| Visual | Autor | Para | Estado en este proyecto | Alternativa sin visual personalizado |
|---|---|---|---|---|
| **Deneb** | comunidad (certificado) | cualquier visual firma con Vega-Lite: área con degradado, anillo, bullet, mancuerna (`scripts/deneb.py`) | **[probado]** RS 2026.05 y nube | SVG / nativo |
| HTML Content | comunidad | bloques de texto enriquecido, tarjetas con formato | visto en un archivo RS; render [por validar] | textbox, card de texto |
| Sankey | Microsoft | flujos entre etapas o categorías | [por validar] | embudo por etapas con cardVisual + barras |
| Gantt | Microsoft | cronogramas y proyectos | [por validar] | matriz con formato condicional por fecha |
| Tornado | Microsoft | comparación de dos lados por categoría | [por validar] | dos barChart en espejo |
| Bullet Chart | Microsoft / OKViz | avance vs meta con rangos | [por validar] | SVG `bullet` [probado] |
| Power KPI / Multi KPI | Microsoft | KPI con tendencia y estado | [por validar] | cardVisual + sparkline SVG |
| Timeline Slicer | Microsoft | filtro de fechas tipo línea de tiempo | [por validar] | slicer «entre» o botones de periodo |
| Text Filter | Microsoft | búsqueda de texto libre | [por validar] | slicer con búsqueda |
| Radar, Word Cloud, Chord | Microsoft | — | evitar: se leen mal | barras ordenadas |

**No usar en Report Server**: visuales con licencia de AppSource (p. ej. suites comerciales de tablas y gráficos financieros),
visuales que piden clave propia o muestran marca de agua, mapas que cargan teselas de Internet o necesitan token, y cualquier
visual no certificado con datos sensibles sin aprobación de TI.

## Registro
Cuando un visual se pruebe en RS, anótalo aquí (estado + versión del .pbiviz + fecha) y en `plataformas.json`.
