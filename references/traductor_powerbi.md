# Traductor: intención de diseño → Power BI

Para pasar una idea (de una referencia externa o del HTML) a lo que Power BI dibuja de verdad. Orden de preferencia:
**nativo** (tema y propiedades) → **medida SVG** → **2 capas** (imagen de fondo) → **Deneb** → **otro visual de AppSource**
(`appsource.md`). Por defecto se usa solo lo marcado [probado] en la plataforma del usuario; lo [por validar] se ofrece como
opción y se dice. Detalle de propiedades: `efectos_powerbi.md`; plataformas: `report_server.md` y `plataformas.json`.
Capas: N = visual nativo · S = medida SVG · F = imagen de fondo (2 capas) · D = Deneb · A = otro visual de AppSource.

| Intención | Cómo | Capa | RS 2026.05 | Nube | Si no se puede |
|---|---|---|---|---|---|
| Paleta y neutros propios | tema desde tokens (`tema_powerbi.py <dirección>`; a la medida con `PBIX_TOKENS_EXTRA`) | N | [probado] tema en clásico | [probado] | — |
| Tipografía con carácter | fuente del sistema en el tema (Segoe UI y familia; Georgia solo títulos) | N | [probado] Segoe/Georgia | [probado] | peso y tamaño en vez de otra familia |
| Esquinas redondeadas | `border.radius` (uno para todo el reporte) | N | [probado] | [probado] | — |
| Tarjeta con sombra suave | `dropShadow` del contenedor o `shadowCustom` de cardVisual | N | [probado] sobre fondo claro | [probado] | 2 capas: sombra en la imagen |
| Resplandor (glow) | `glow` en actionButton/shape; `glowCustom` en cardVisual, **sin selector** | N | [probado] (tenue) | [probado] | luz en la imagen de fondo |
| Barra de color en la tarjeta | `accentBar` de cardVisual | N | [probado] | [probado] | shape de 4 px al lado |
| Pestañas / botones con hover | actionButton con estados (`selector: {id: 'hover'}`) | N | [probado] hover; presionado [por validar] | [probado] | botón sin estados |
| Degradado de fondo de página, luces, aurora | imagen de fondo (`capas_html.js` → `fondo_pagina.py`) | F | [probado] servidor y portal | [probado] | color plano del tema |
| Paneles de vidrio (blur, borde de luz) | panel dibujado en la imagen de fondo; visual encima transparente | F | [probado] | [probado] | tarjeta con sombra (N) |
| Textura, ilustración, forma grande de color | en la imagen de fondo, nunca detrás de cifras | F | [probado] (imagen) | [probado] | — |
| Riel lateral de color | shape con relleno (N) o en la imagen (F) | N/F | [probado] | [probado] | — |
| Píldora de variación ▲ 4.2 % | medida SVG `pildora` en tableEx; o texto ▲▼ con color por regla | S/N | [probado] SVG en tableEx | [probado] | card de texto con regla de color |
| Anillo de avance | SVG `anillo` como imagen de cardVisual (`cardImage.imageUrl`) o Deneb `anillo` | S/D | [probado] ambos | [probado] | gauge nativo simplificado |
| Bullet (avance vs meta) por fila | SVG `bullet` en tableEx; Deneb `bullet` por categoría | S/D | [probado] SVG; Deneb [probado] | [probado] | barra de datos del formato condicional |
| Sparkline por fila | SVG `sparkline` en tableEx; minigráficos nativos de tabla | S/N | [probado] SVG; nativos [por validar] | [probado] | columna de tendencia ▲▼ |
| Área con degradado | Deneb `area_degradado` | D | [probado] | [probado] | areaChart con transparencia |
| Mancuerna (antes → ahora) | Deneb `mancuerna` | D | [probado] Deneb | [probado] | dos barChart o barras agrupadas |
| Cifra monumental (36–96 pt) | card/cardVisual con fuente grande | N | [probado] 36 pt | [probado] | — |
| Titular-conclusión dinámico | medida de texto DAX en card de texto | N | [probado] | [probado] | textbox estático (solo si no hay filtros) |
| Anotación sobre el gráfico | textbox posicionado + línea de referencia rotulada | N | [probado] | [probado] | nota en el subtítulo |
| Mapa de calor | pivotTable con escala de color de fondo | N | [probado] | [probado] | — |
| Calendario | pivotTable semanas × días con escala | N | [probado] (matriz) | [probado] | — |
| Small multiples | small multiples nativo | N | [por validar] | [probado] | N gráficos con eje fijo |
| Iconos | caracteres Unicode (✓ ! ✕ ▲ ▼ ●) o SVG | N/S | [probado] | [probado] | — |
| Texto enriquecido / bloque HTML | visual HTML Content | A | observado en archivo RS; render [por validar] | AppSource | textbox |
| Animación, transición, hover en gráficos | no existe (salvo dentro de Deneb) | — | — | — | el reporte se lee quieto |
| Fuente web (Inter, Poppins…) | no existe | — | — | — | Segoe UI con peso y tamaño |
| Sombra de texto, interletrado | no existe | — | — | — | peso, tamaño y color |
| Degradado dentro de barras nativas | no existe | — | — | — | Deneb o SVG |

## Regla de traducción
1. Para cada rasgo tomado de la inspiración, busca la fila; si no está, decláralo **[sin traducción]** y no lo diseñes.
2. Lo decorativo va a la imagen de fondo (F) solo en nivel impactante; lo que cambia con los filtros nunca va a la imagen.
3. Máximo 1–2 visuales Deneb por página; SVG solo con forma (los números, en formato nativo: decisión de cultura C+A).
4. En la ficha, cada bloque del diseño dice su capa (N/S/F/D/A) y su estado en la plataforma.
