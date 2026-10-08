# Diseñar un reporte de Power BI: contexto, tipo, visuales y estilo

El diseño no empieza por los colores: empieza por la decisión que el reporte debe apoyar. Sigue los pasos en orden.
Un rediseño hecho sin preguntar el tipo de reporte, con banda de encabezado oscura y colores de marca fuertes, suele verse
**anticuado y mal distribuido**. Por eso: preguntas obligatorias, diseño primero en HTML y dirección `moderno`.

## 0. Alcance (pregunta obligatoria, antes que nada)
| Alcance | Qué se toca | Qué no |
|---|---|---|
| **Solo apariencia** | tema, colores, tipografía, bordes, espaciado, títulos, formatos de número | posición y tipo de visuales, páginas, medidas |
| **Rediseño** | además: disposición, tipo de visual, páginas, navegación, medidas nuevas si hacen falta | el modelo y sus fuentes |
| **Desde cero** | todo el reporte nuevo sobre el modelo existente (o uno nuevo) | — |
Si el usuario no lo dice, **pregúntalo** (no lo deduzcas). En "solo apariencia" no cambies la disposición aunque la mejorarías:
propónlo aparte.

## 1. Brief (preguntas obligatorias; nunca asumas el tipo de reporte)
El **tipo de reporte** (ejecutivo, operativo, analítico, financiero, detalle) y el **público** se preguntan siempre, junto con la
plataforma, el formato regional y la marca. Si de verdad no hay a quién preguntar, decláralo como supuesto en la primera línea
de la entrega. El resto de la tabla se pregunta si no se puede leer del archivo.

| Pregunta | Por qué importa |
|---|---|
| ¿Qué decisión o conversación apoya? (comité mensual, seguimiento diario, auditoría) | define el tipo de reporte |
| ¿Quién lo mira y cuánto tiempo? (director 2 min, responsable 10 min, analista horas) | densidad y nivel de detalle |
| ¿Dónde se publica? (Power BI Report Server y qué release, o servicio) | visuales y funciones disponibles (ver `report_server.md`), formato del archivo |
| ¿Dónde se ve? (laptop, proyector/sala, TV, celular, PDF impreso) | tamaño de letra, contraste, lienzo, modo oscuro |
| ¿Cada cuánto se actualiza y qué periodo compara? (mes vs mes anterior, vs presupuesto, YoY) | medidas de referencia y KPIs |
| 3–5 indicadores que deben verse primero | jerarquía visual |
| Marca: colores y fuente corporativos, logo | dirección visual / tema |
| ¿Qué filtros necesita realmente? | slicers vs. filtros ocultos de página |
| Configuración regional: separador de miles/decimal y formato de fecha (p. ej. `$1,234.56` y `dd/mm/yyyy`) | por defecto **el del lector**: formatString + `FORMAT(…, USERCULTURE())` en textos con cifras; locale fijo solo si se pide (ejes y tablas seguirán el navegador) [probado v5 y portal RS] |

Antes de elegir visuales, corre `leer_reporte.py` + `cruzar_reporte_modelo.py` sobre el .pbix: el diseño depende de qué
medidas existen, de sus formatos y de las referencias rotas.

## 2. Tipo de reporte → estructura y visuales

| Tipo | Lector | Estructura de página | Visuales preferidos | Funciones PB |
|---|---|---|---|---|
| **Ejecutivo** (comité, dirección) | decide en minutos | 1 página 16:9; fila de 3–5 KPI arriba, 1–2 gráficos de tendencia/comparación, una frase de lectura | `card`/`cardVisual` con delta, `lineChart`, `clusteredBarChart` ordenado, `gauge` de cumplimiento | tooltips de página para el detalle; marcadores para "vs presupuesto / vs año anterior" |
| **Operativo** (seguimiento diario) | actúa sobre excepciones | alertas arriba, lista de excepciones con semáforo, tendencia corta | `tableEx` con iconos/colores por reglas, `card` con estado, `lineChart` de 30 días | modo oscuro si va a TV; actualización frecuente; pocos clics |
| **Analítico** (analista) | explora y compara | panel de filtros a la izquierda o arriba, área grande de gráfico, detalle abajo | `scatterChart`, `decompositionTreeVisual`, `pivotTable`, `lineChart` con series | jerarquías y profundizar, drillthrough, parámetros de campo |
| **Financiero** (P&L, balance) | lee filas de un estado | matriz principal a ancho completo, KPIs de margen arriba | `pivotTable` con subtotales y formato condicional, `waterfallChart` para el puente | jerarquía de cuentas, filtros de periodo y compañía |
| **Detalle / Inventario** | consulta registros | filtros arriba, tabla grande, totales | `tableEx` con anchos fijos, `slicer` desplegables | exportar datos, drillthrough desde el resumen |

Reglas de Power BI que aplican a todos:
- Lienzo 1280 × 720 (16:9) para pantalla y proyector; páginas altas (1280 × 1400 aprox., `FitToWidth`) solo para lectura con scroll;
  PDF/impresión: 16:9 o Carta sin elementos interactivos imprescindibles.
- Lectura en Z: lo más importante arriba a la izquierda; filtros en una fila arriba o en una columna a la izquierda, siempre en el mismo lugar entre páginas.
- Máximo ~8 visuales con datos por página ejecutiva (rendimiento y foco); cada visual con título que diga qué responde.
- Un solo eje Y por gráfico (evita el doble eje del combo); ordena barras por valor salvo que el orden sea temporal.
- Tiempo: columnas si son ≤ 12 periodos, línea si son más; eje con formato de mes corto (`mmm yy`).
- Colores: identidad (categorías) con la paleta del tema en orden fijo; énfasis (una serie a color, resto gris); estado
  (bien/alerta/mal) solo con la paleta de estado y siempre con ícono o texto (▲▼, ✓, !), nunca solo color.

## 2b. Diseñar en HTML y replicar en Power BI (flujo por defecto para rediseño y desde cero)
1. **Lee el modelo** (`leer_reporte.py`, `leer_modelo.py`, `cruzar_reporte_modelo.py`): medidas, formatos, columnas, hallazgos.
2. **Diseña la página en HTML** a 1280 × 720 partiendo del diseño de referencia del tipo (`references/disenos/<tipo>.html`,
   generador en `disenos/_fuente/`): títulos y nombres reales de medidas/campos, **cifras ficticias** con la escala y forma
   reales (nunca datos del archivo). Solo bloques que existan en el mapa HTML → Power BI de `disenos/README.md`; cada bloque con
   `data-pbi`. Renderiza y míralo (Playwright/navegador): sin solapes, sin texto cortado, jerarquía clara. Revisa con la skill
   `dataviz` (forma, color, etiquetas) y, si está, `design:design-critique`.
3. **Sin pausa de aprobación** (preferencia del usuario): el HTML es la especificación; se entrega junto al .pbix
   (`<reporte>_diseno.html`) para comparar.
4. **Replica** bloque a bloque con `componentes.py` y el catálogo (`references/catalogo/`), mismas coordenadas (px HTML = px de
   página), tipografía px × 0.75 = pt, tema `moderno` (o `marca`). Lo que el catálogo marque como no soportado en la plataforma
   se sustituye por el equivalente del mapa y se dice en la entrega.
5. **Compara**: captura de Power BI contra la PNG del HTML; corrige diferencias de posición, tamaño y formato.
Antes del paso 4: premisa causal y 2–3 variantes con rúbrica, puertas `revisar_html.js`, ficha de decisiones y pie de
confianza (`guia_diseno.md` §2, §3, §8, §10).

## 3. Dirección visual (detalle en `guia_diseno.md` §4)
**Vigentes** (tokens en `tokens.json`): `moderno` (defecto), `editorial` (financiero/comité/PDF), `suizo` (analítico/detalle),
`grafito` (pantalla mural) y `marca`. Elige por tipo de reporte y medio, no al azar.
**Por defecto `moderno`** (tokens en `disenos/README.md`): claro, una sola tinta de acento, tarjetas blancas con borde fino,
sin bandas oscuras ni sombras, gris para el contexto. Variantes: **`marca`** (sustituye acento y categóricos por los colores
corporativos validados con `dataviz`, manteniendo neutros y estructura) y **`oscuro`** (TV/sala). La dirección `corporativo`
(encabezado azul marino con línea dorada) no se usa por defecto: tiende a verse anticuada. No ofrezcas varias direcciones salvo que el
usuario lo pida; propone la `moderno` bien hecha.

### Otras direcciones de `tema_powerbi.py`

Úsalas solo si el usuario las pide. Cada una es un **tema de Power BI** generado con
`scripts/tema_powerbi.py` (paleta validada con el validador de la skill `dataviz`) más unas pocas decisiones de maqueta.

| Dirección | Cuándo | Lienzo y superficies | Paleta (validada) | Tipografía y forma |
|---|---|---|---|---|
| `corporativo` | comité, dirección, marca sobria | fondo #F2F4F8, tarjetas blancas, encabezado azul marino con línea dorada | azul #2F5D9E, oro #D4A72C, rosa #D77FA3, verde #5E9A35, violeta #8466B8, naranja #E08A2E, verde azulado #1F8A70, terracota #C2553A | Segoe UI, títulos semibold, radio 8 |
| `minimalista` | analistas, documentación, impresión | fondo blanco, sin tarjetas (separación por espacio), líneas finas | referencia de `dataviz` (azul #2a78d6 primero) | Segoe UI, mucho aire, radio 4, sin sombras |
| `oscuro` | TV, sala de operaciones, monitoreo | fondo #111110, tarjetas #1a1a19 | variante oscura de `dataviz` (#3987e5 …) | Segoe UI, números grandes, contraste alto |
| `marca` | cuando el usuario da colores corporativos | según marca | **correr el validador** sobre los colores de marca y reordenar hasta pasar | según marca |

Paleta de estado (fija, no se tematiza): bien #0ca30c · alerta #fab219 · serio #ec835a · crítico #d03b3b.
Para una sola serie, usa el color principal de la dirección y gris #B7BDC7 para el contexto (énfasis).

Tipografía en Power BI (pt): KPI 22–28 negrita · título de página 18–20 · título de visual 11–13 semibold · ejes y etiquetas 9–10 ·
texto de apoyo 9–10 gris. En TV o proyector, +2 pt en todo.

### Paleta de marca: valídala siempre
Ejemplo (Marca Demo S.A., ficticia): el rojo de marca #D9381E y el caramelo #A0612B **fallan juntos** para daltonismo
(ΔE 3,3 protanopía). Solución: el caramelo sale de la paleta categórica y se usa solo como énfasis de una serie; la paleta
validada quedó #D9381E, #2F5D9E, #D4A72C, #1F8A70, #8466B8, #B5651D, #D77FA3, #5E9A35 (CVD ≥ 11,5; oro y rosa con etiqueta).
Tokens completos en `ejemplos/rediseno_dos_versiones.py` (`MARCA`).

### Coherencia entre páginas (revísala siempre en un reporte de varias páginas)
- Misma dirección visual en todas (error típico: la portada en rojo/amarillo y otra página en azul/oro).
- Misma barra de navegación con texto, en el mismo lugar, con la página activa resaltada; botones con texto, no solo íconos.
- Mismo encabezado (kicker, título, subtítulo o periodo) y mismos tamaños de KPI, títulos de sección y tablas.
- Páginas de destino visibles si se navega por pestañas; ocultas solo las de apoyo (tooltips, versiones viejas).
- Portada útil: qué es el reporte, periodo, 3 KPIs titulares y una tarjeta por página con para quién es y qué responde.

### Mostrar dos versiones
Cuando el usuario no decide la dirección, construye la misma estructura con dos `T` (tokens) distintos y entrega dos archivos;
la estructura no cambia, solo tema y tokens. Así la comparación es justa.

## 4. Construcción

1. Genera el tema: `python scripts/tema_powerbi.py corporativo tema_corporativo.json` (o `--marca "#hex,#hex,..."`).
2. Inyéctalo en PBIR con `tema_powerbi.aplicar_tema_pbir()` [probado] o que el usuario lo importe en **Vista → Temas →
   Examinar temas**.
3. Construye páginas con `modificar_layout.py` / `pbir.py` usando solo los visuales del catálogo (`visuales_powerbi.md`) y deja
   que el tema dé colores y fuentes; sobrescribe por visual solo lo necesario (énfasis, reglas de estado).
4. Verifica (`edicion_reporte.md`) y pide captura.

## 5. Revisión con criterio

Con la captura del usuario:
- usa la skill **design:design-critique** (jerarquía, consistencia, legibilidad) y **design:accessibility-review**
  (contraste, tamaño de texto, color como único indicador) si están instaladas;
- contrasta contra el brief: ¿los 3–5 KPIs se ven primero?, ¿cada visual responde una pregunta?, ¿hay scroll dentro de visuales?,
  ¿ejes legibles?, ¿estado con ícono + color?;
- registra los ajustes que funcionaron en `edicion_reporte.md` (patrones que Power BI respeta o ignora).
