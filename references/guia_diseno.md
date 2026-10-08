# Guía de diseño de dashboards (reglas operativas)

Reglas adaptadas a Power BI a partir de skills de diseño front-end de bencium.io (`bencium-controlled-ux-designer`,
`bencium-impact-designer`, `bencium-innovative-ux-designer`, `design-audit`, `typography`, `relationship-design`), filtradas
para BI: se conserva lo que mejora la lectura del dato y Power BI puede replicar; se descarta movimiento, responsive, fuentes
web, texturas, pausas de aprobación y técnicas de interfaz conversacional. Redacción propia, no copia. Lecciones reales en
`lecciones.md`. Tokens en `tokens.json`; diseños de referencia en `disenos/`.

## 1. Brief: una sola ronda de preguntas cerradas
Todo lo visual se pregunta **antes** de diseñar, en una sola tanda, cada pregunta con una opción recomendada. Si no hay
respuesta, se usa la recomendada, se marca como **supuesto** en la ficha y se sigue (no hay pausa de aprobación).
| Pregunta | Recomendado si no responden | Qué decide |
|---|---|---|
| Alcance: solo apariencia / rediseño / desde cero | — (siempre preguntar) | qué se puede tocar |
| Tipo de reporte y público | — (siempre preguntar) | estructura, densidad, referencia en `disenos/` |
| ¿Qué decisión apoya y qué cifra debe quedar clara en 5 s? | la del primer KPI del brief | KPI héroe y título-conclusión |
| Medio: comité/proyector, escritorio diario, pantalla mural, PDF/impresión, móvil | escritorio | tamaños mínimos, dirección (grafito solo mural), si los tooltips cuentan |
| Comparación de referencia y **polaridad** de cada KPI (¿subir es bueno?) y meta/umbral | vs mismo periodo año anterior; subir = bueno salvo costos/gastos/días | Δ, color de estado, líneas de meta |
| Navegación: de dónde llega, a qué detalle va, cómo vuelve | botones de página; drillthrough al detalle | páginas, botones, drillthrough (en RS evitar marcadores) |
| **Nivel de impacto: sobrio / realzado / impactante** (ver §11) | — (siempre preguntar; sugerir el del público, §12) | capas, efectos, Deneb, direcciones posibles |
| Estilo: **a la medida** (inspiración + semillas, §2b) o dirección fija moderno / editorial / suizo / grafito / aurora / vidrio / marca | a la medida en rediseño y desde cero; fija en solo apariencia o si el usuario la pide | tema y tokens |
| ¿Quiere agregar recursos de marca? (logo, colores, tipografía, fotos) | no; solo si la persona los quiere agregar | dirección marca, logo en la cabecera o en la imagen de fondo |
| Plataforma y release; formato regional | Report Server del archivo; formato **del lector** = cifras nativas (formatString); fijo solo si se pide | visuales disponibles, formatos |

## 2. Premisa y variantes (variedad sin pausa)
1. Escribe la **premisa** de la página en forma causal: *«el público decide X, porque Y; por eso el héroe es Z y la ruta de
   lectura es …»*. Una decisión cuyo único argumento sea «se ve moderno» se rechaza.
2. En **rediseño y desde cero**, genera 2–3 variantes HTML internas desde premisas de lectura distintas (excepción vs meta,
   tendencia, contribución/puente, comparación entre entidades, flujo por etapas): cada una con héroe, rejilla y ruta propios;
   prohibido derivar B de A cambiando solo colores. En **solo apariencia**: como máximo 2 variantes, solo de tema.
3. Pasa las puertas (§7) y puntúa 1–5: ajuste a la decisión ×3, prueba de 5 s / miniatura 320×180 ×2, densidad para el público
   ×2, replicabilidad nativa ×2, distinta de la referencia y del último diseño entregado ×1. Empate → la más simple de replicar.
   En nivel **impactante** al menos una variante es una **propuesta innovadora** (§12): estructura que no está en `disenos/`
   ni en lo último entregado, con su premisa; suma +1 si sigue ganando en decisión y 5 s (si pierde ahí, no se elige por novedad).
4. Se replica solo la ganadora; las otras van en un anexo (miniatura + premisa). El usuario puede pedir «usa la B» después.

## 2b. Idea propia por reporte (no aplicar siempre los mismos estilos)
Las direcciones fijas (§4) y los diseños de `disenos/` son **material de aprendizaje**, no plantillas. Repetirlos es el fallo
más común: casi todo termina en `heroe_tira` si no se elige el arquetipo a propósito. Para cada reporte nuevo:
1. **Carácter** en 3 adjetivos desde público, medio y marca → un carácter de `estilo_a_medida.py` (neutro, cálido, frío,
   técnico, enérgico, sereno, premium, institucional).
2. **Inspiración** (`inspiracion.md`): 2–4 referencias de familias distintas (Power BI, visualización editorial, interfaz,
   mundo físico, marca del usuario) o el catálogo sin web. Se toman patrones (composición, color, tipografía, tratamiento del
   dato), nunca diseños ni marcas ajenas.
3. **Arquetipo** (`arquetipos.md`) por la premisa; las variantes usan arquetipos distintos.
4. **Estilo a la medida**: `estilo_a_medida.py` con 1–3 semillas de la inspiración o la marca → tokens con contraste, daltonismo
   y estados ya calculados (si mueve un color para cumplir, el original queda como `marca`, solo para decoración).
5. **Traducción** (`traductor_powerbi.md`): cada rasgo con su técnica y su estado en la plataforma; lo [sin traducción] se descarta.
6. **Anti-repetición**: `registro_disenos.py comparar` contra lo entregado a otros reportes; con REPITE (≥ 0.60) se cambia
   arquetipo, estilo o héroe; con PARECIDO (≥ 0.45) se justifica en la ficha. Al entregar, `registro_disenos.py agregar`.
Excepciones: «solo apariencia» con marca dada, suites donde el usuario pide continuidad con un reporte existente (misma
`familia`) y nivel sobrio de operación diaria, donde lo conocido es una virtud.

## 3. Ficha de decisiones (va en el HTML, fuera del lienzo)
Estilo (fijo o a la medida: carácter, semillas, archivo de tokens) y por qué, tipo/público, premisa, arquetipo, pregunta de 5 s,
rejilla, escala, mapa bloque → visual con su capa (N/S/F/D/A), inspiración (fuente · qué se toma · traducción · estado en RS),
resultado de `registro_disenos.py comparar`, supuestos tomados.
Es la especificación para replicar y para comprobar fidelidad HTML ↔ .pbix (rectángulos ±8 px, colores = tokens del tema).

## 4. Direcciones fijas (tokens en `tokens.json`; tema con `tema_powerbi.py <direccion>`) y a la medida
Las fijas son puntos de partida y respaldo; para un estilo propio usa `estilo_a_medida.py` (§2b) y `PBIX_TOKENS_EXTRA`.
| Dirección | Para | Rasgos | Riesgos |
|---|---|---|---|
| **moderno** (defecto) | ejecutivo, operativo de escritorio | tarjetas blancas borde fino, acento azul #2264C4, gris de contexto | genérica si se abusa de tarjetas iguales |
| **editorial** | comité, financiero, PDF/PowerPoint | papel cálido, sin tarjetas, reglas de 1 px, título en Georgia (solo el título), azul tinta | Georgia nunca en cifras (elzevirianas); título-conclusión estático miente al filtrar → dinámico por DAX |
| **suizo** | analítico, detalle, suites densas | blanco, sin cajas, alineación estricta, KPI en Segoe UI Light ≥ 18 pt, índigo | cualquier desalineación se nota; Light < 18 pt ilegible |
| **grafito** | pantalla mural, sala de operación | oscuro, acento celeste, estados claros | PDF/suscripciones salen oscuros; no para ejecutivos |
| **aurora** (impactante, 2 capas) | comité, sala, pantallas, presentaciones | azul noche con luces de color desenfocadas, paneles vidrio, acento cian + violeta, cifras claras | no para PDF impreso; las luces bajan el contraste: la puerta lo mide sobre la imagen |
| **vidrio** (impactante, 2 capas) | dirección en laptop, portadas, reportes para clientes | fondo claro con luces pastel, paneles blancos translúcidos con borde blanco, índigo | se ve plano si se quitan las luces; muchos paneles = ruido |
| **marca** | colores corporativos | sustituye acento y categóricos (validar con `dataviz`), conserva neutros y estructura; en 2 capas las luces toman los colores de marca | rojo/verde de marca chocan con estados |
| ~~corporativo~~ | no por defecto | banda azul marino + dorado | tiende a verse anticuada |

## 5. Composición
- Rejilla de 12 columnas en 1280: margen 24, medianil 16, columna 88; posiciones múltiplos de 8. Solo el héroe rompe la simetría.
- **No la rejilla de 4 tarjetas iguales**: KPI héroe (≈4 col, 27 pt) + secundarios en una tira con separadores de 1 px.
- Agrupar por espacio y reglas finas antes que por cajas; el «cromo» nunca supera al dato (sobrio: sin sombras, un solo radio;
  realzado/impactante: una sola sombra suave y un solo radio de panel; ver §11).
- Filtro de reducción: si se quita un elemento y no se pierde significado, se quita. Tope ~8 visuales con datos (ejecutivo).
- Mismo lugar y estilo de filtros en todas las páginas; texto con los filtros activos en el subtítulo.

## 6. Tipografía y texto
- Escala en **pt enteros**: nota/etiqueta/tabla 9 · título de visual 10 · subtítulo 12 · título de página 15 (editorial:
  Georgia 18) · KPI 21 · héroe 27 · impacto 36 (solo nivel impactante, una cifra por página). Mínimo 9 pt. Máximo 2 familias;
  contraste con tamaño, peso y color.
- Título de visual = qué muestra; subtítulo = unidad · periodo · comparación. En ejecutivo, título de página = conclusión
  dinámica (DAX). Tipo oración, sin «Suma de…».
- Kicker en tipo oración, semibold (Power BI no espacia letras: las mayúsculas se ven apretadas).
- Microtipografía en español: semirraya en intervalos («ene–sep 2026»), raya en incisos, signo menos − (U+2212) en formatos
  (`#,0;−#,0`) o paréntesis en financiero, «4.2×», «…» un carácter, comillas “ ”, meses en minúscula, unidad una sola vez en el
  subtítulo. **Nunca** tocar comillas rectas dentro de DAX, M, JSON o cadenas de formato.

## 7. Color y contraste
- Un acento + neutros + estados. El acento marca el foco; el gris, el contexto; el acento nunca es verde/ámbar/rojo.
- Texto ≥ 4.5:1 (incluidas notas y ejes); marcas y contexto ≥ 3:1. Las direcciones fijas están validadas en `tokens.json` y las a la medida las valida `estilo_a_medida.py` al generarlas;
  categóricos validados con `dataviz` (adyacentes). Estado = ícono + texto (✓ ! ✕ ▲ ▼), nunca solo color. Píldoras de fondo
  (medida SVG) solo en realzado/impactante, con flecha y SIN cifra dentro (la cifra va nativa al lado: sigue la configuración
  regional del lector; un texto en SVG no), fondo = estado al 10 % (claro) o 20 % (oscuro).
- Menos tinta que no es dato: etiqueta directa al final de la línea en vez de leyenda, cuadrícula tenue, metas como línea de
  referencia rotulada. Relleno de área: sobrio no; realzado/impactante solo en la serie protagonista y en degradado que se
  desvanece (Deneb), nunca en la de comparación.

## 8. Confianza en el dato (bloque obligatorio)
Pie en cada página: **Fuente · Actualizado al dd/mm/yyyy hh:mm** (medida DAX) · acceso a definiciones (botón ⓘ → tooltip de página
o página de definiciones). Aviso condicional de datos parciales/preliminares (DAX) y tramo parcial en línea discontinua.
Estados vacíos intencionales: «—» o «Sin datos para la selección».
**Cifras nativas**: toda cifra visible sale de una medida numérica con formatString (tarjeta, tabla, eje, etiqueta),
nunca de un texto con `FORMAT()` ni de un SVG: es lo único que el portal y el Desktop muestran con la configuración del lector.
Tablas sin barra: `LienzoV2.tabla_top` (top N = filas que caben); `auditoria.py` avisa de tablas sin top N.
**Variaciones con semántica comprobada** (error típico: ▲595 % por comparar el total del periodo contra UN mes): el texto («Δ último mes vs anterior») debe decir exactamente lo que calcula la medida, en el contexto
de cada fila. Antes de pedir la captura, una consulta DAX agregada por fila/categoría (`ADDCOLUMNS(VALUES(cat), "@d", [Δ])`):
si |Δ| > 200 % en la mayoría de las filas, es alarma de semántica, no un dato. Reusa la medida del modelo si existe (p. ej. la que
alimenta el KPI de último mes) en vez de inventar otra.

## 9. Accesibilidad en Power BI
Texto alternativo en cada visual informativo (dinámico con medida en KPI); decorativos sin él y fuera del orden de tabulación;
orden de tabulación: título → filtros → KPI → gráficos → tabla; títulos con unidad y periodo; marcadores en líneas.

## 10. Puertas objetivas y auditoría
- Antes de replicar: `node scripts/revisar_html.js <diseño>.html` (lienzo 1280×720 sin desborde, CSS replicable, fuentes de Power BI,
  texto ≥ 9 pt, contraste, tamaños en pt enteros, data-pbi en cada bloque, pie de confianza). En 2 capas el contraste se mide
  contra los píxeles reales de la imagen de fondo (percentil 10). Renderiza también en el equipo con Segoe UI real (Windows):
  en Linux el navegador sustituye la fuente.
- Después de replicar: `python scripts/auditoria.py nuevo.pbix --direccion=<dir>` hace la parte [P] (avisos, no errores; una página
  hecha con `componentes.LienzoV2` da 0/0/0). Auditoría en 3 fases (formato *qué está mal → qué debe ser → por qué* + propiedad y valor exactos);
  [P] automatizable desde el .pbix, [C] sobre la captura:
  - **Crítico**: el ojo cae primero en el KPI que responde la pregunta [C]; ejes truncados sin aviso, comparación sin referencia,
    estados invertidos [C]; unidad o periodo ausente [P]; filtros activos invisibles [C]; solapes o fuera del lienzo [P];
    contraste bajo AA [P]; referencias rotas [P].
  - **Refinamiento**: fuera de rejilla o desalineado 1–2 px [P]; márgenes desiguales [P]; > 6 tamaños o > 3 pesos [P]; hex fuera de
    tokens [P]; tarjetas con borde/radio/padding distintos [P]; más de un acento [C].
  - **Pulido**: texto alternativo [P]; orden de tabulación [P]; estados vacíos [P/C]; tooltips útiles [C]; estados de botón [P].
- Informar por niveles: **HTML diseñado** / **replicado en .pbix** / **verificado con captura**. Nunca «listo» con solo el HTML.

## 11. Niveles de impacto y efectos (siempre se pregunta el nivel)
| Nivel | Capas | Qué se permite | Para |
|---|---|---|---|
| **Sobrio** | 1 | solo nativo y tema; color para estado y foco | operación diaria, analistas, detalle, PDF/Excel, servidores viejos |
| **Realzado** | 1 | + sombra suave y barra de acento (cardVisual), glow nativo en botones/formas/cardVisual, botones con estados (hover, presionado, seleccionado), medidas SVG (píldoras, bullets, anillos, sparklines), 1 Deneb si aporta | ejecutivos en laptop, reportes de área, portadas y menús |
| **Impactante** | 2 | + capa de decoración como **imagen de fondo** (degradado base, luces desenfocadas, paneles vidrio, línea de luz) con visuales nativos **transparentes** encima; 1–2 Deneb firma; cifra de impacto 36 pt | comité, dirección, sala/pantalla, presentaciones, lanzamientos |

**Cómo funcionan las 2 capas** (`capas_html.js` → `fondo_pagina.py`):
1. En el HTML, la decoración va en `fondo(direccion, luces, trazos)` (`[data-capa="fondo"]`) y cada `.card` es un panel. La caja
   de cada `data-pbi` (fondo, borde, radio, sombra, desenfoque) se pinta en la imagen; su contenido lo dibuja el visual nativo.
   `data-caja="nativa"` = el visual pone su propia caja (p. ej. cardVisual con glow): no se pinta.
2. `node scripts/capas_html.js diseño.html` → `_fondo.png` (1920×1080, < 3 MB; baja a 1664/1280 si pesa más),
   `_visuales.json` (x, y, ancho, alto de cada visual en el lienzo 1280×720 = coordenadas de Power BI) y `_compuesto.png`.
3. `fondo_pagina.py` registra la imagen y la pone de fondo (clásico y PBIR, transparencia 0 %, ajuste Fill) y el papel tapiz
   del color base. El tema de aurora/vidrio deja los visuales sin fondo ni borde y las tablas sin relleno [por validar en RS].
4. **Costo**: el fondo es una imagen; si se mueve o cambia de tamaño un visual hay que regenerarla (pasos 2–3). Avísalo.
- Las luces guían la mirada: detrás del héroe y del cierre, en diagonal; nunca detrás de texto pequeño sin pasar la puerta.
- En el contenido de los visuales siguen las reglas nativas: nada de degradados CSS ni sombras de texto, salvo en visuales
  marcados Deneb/SVG (`data-pbi` con «Deneb» o «SVG»).
- Catálogo de efectos con la propiedad exacta y su estado en Report Server: `efectos_powerbi.md`.

## 12. Innovación alineada al público
El nivel lo decide el público, no el gusto: se propone el sugerido y se pregunta.
| Público / uso | Nivel sugerido | Direcciones | Firma que suele funcionar |
|---|---|---|---|
| Comité, junta, dirección en sala | impactante | aurora, editorial (sobrio) | héroe 36 pt con anillo de avance; área con degradado vs plan; tabla de excepciones con píldoras |
| Director en laptop, cierre mensual | impactante o realzado | vidrio, moderno | héroe vertical con área; contribución (barras divergentes) en vez de cascada larga; sparklines por unidad |
| Gerentes comerciales, seguimiento diario | realzado | moderno, marca | pestañas con estados, tarjetas con barra de acento, bullets contra objetivo por cliente |
| Operación, sala de control | realzado (mural: grafito) | grafito, moderno | semáforos con ícono, mancuerna antes→ahora, progreso por línea |
| Analistas, detalle, auditoría | sobrio | suizo, moderno | densidad, tablas limpias, filtros visibles; sin efectos |
| Clientes externos, portada, lanzamiento | impactante | vidrio, marca | portada con cifra de impacto y logo en la imagen de fondo |
Ideas de estructura para la variante innovadora: los 18 arquetipos de `arquetipos.md` (elegir por premisa, no por novedad).
Las direcciones de esta tabla son el respaldo; con inspiración y `estilo_a_medida.py` el estilo sale del carácter del público
(p. ej. comité de una empresa familiar de alimentos → cálido + titular con serifa; dirección comercial → enérgico con riel lateral).
