---
name: pbix-toolkit
license: MIT
description: "Lee, audita, modifica y diseña reportes de Power BI (.pbix) a nivel de metadatos, para Power BI Report Server y el servicio de Power BI. Inventario de páginas, visuales, campos, filtros, medidas DAX, M, relaciones, RLS y formatos; referencias rotas y linaje de campos hacia las tablas de origen; cambios en visuales, páginas, temas y formatos; medidas y formatos listos para ejecutar dentro del archivo; diseño o rediseño de dashboards (ejecutivo, operativo, analítico, financiero, detalle) en HTML replicado con visuales nativos, con tres niveles de impacto (sobrio, realzado, impactante: fondo de capas, medidas SVG, Deneb) y estilos propios por reporte (inspiración externa, arquetipos, sin repetir diseños). Úsala cuando el usuario comparta o mencione un .pbix o un reporte o dashboard de Power BI, aunque no diga \"pbix\". No la uses para dashboards web que no van a Power BI, para Excel, ni para consultar o extraer filas de datos: nunca lee datos."
---

# pbix-toolkit

Autor: **Francisco J. Chacón R.** · Licencia MIT (ver `LICENSE`).

Versión 2.6.4 · ver `CHANGELOG.md`. Antes de entregar cualquier cosa, recorre `CHECKLIST.md`.

Toolkit probado para **leer** cualquier .pbix (solo metadatos) y, cuando el usuario lo pide, **modificarlo** de forma segura.
Cada regla lleva una etiqueta: **[probado]** (verificado con archivos reales) o **[por validar]** (razonable pero sin evidencia todavía).
Si te topas con un caso [por validar], dilo al usuario y confírmalo antes de darlo por bueno.

## Principios

- **Solo metadatos.** No llames nunca a `get_table` / `iter_table` de pbixray ni leas filas. Los reportes suelen contener información
  sensible de la empresa: confirma con el usuario que puede procesarlos antes de empezar.
- **Nunca edites el original.** Toda modificación se escribe en un archivo nuevo (`<nombre>_v2.pbix`, `<nombre>_prueba.pbix`).
  Si Power BI tiene abierto el archivo destino, la escritura falla con *Permission denied*: usa otro nombre.
- **No confíes en `queryRef`.** El nombre que el reporte guarda (`queryRef`, `Select.Name`) se queda viejo cuando se renombra una medida
  o se cambia una agregación. La verdad está en la expresión (`field` / `Select`). [probado]
- **El formato vive en el modelo**, no en el visual. Revísalo antes de diseñar (ver *Formatos*).
- **Ninguna propiedad sin catálogo.** Antes de escribir un objeto/propiedad de formato, búscalo en `references/catalogo/`
  (`python scripts/catalogo.py propiedades <tipo> <objeto>`): lo que no existe el Desktop de la nube lo borra al guardar o lo
  ignora en silencio. [probado]
- **Por defecto, solo lo [probado].** Lo que sigue [por validar] (estados de botón «presionado», glowCustom, sombra sobre fondo
  oscuro, formato de secciones ▲▼ en el portal, USERCULTURE) queda documentado pero fuera de los diseños por defecto; úsalo solo si
  el usuario lo pide, avisando.
- **Primero la plataforma.** Antes de editar, mira `plataforma` (Report Server o servicio, release). Un archivo para Report Server
  se edita en Layout clásico y nunca pasa por el Desktop de la nube (ver *Report Server*). [probado]
- **Un solo archivo de trabajo.** Los cambios de modelo (DAX, TMDL, formatos) se aplican en el archivo que el usuario abre y
  guarda; las siguientes versiones se construyen desde ese archivo. Antes de construir, confirma con `leer_modelo.py` (o el
  último JSON del modelo) que los cambios pedidos están ahí: en la práctica se pierden (se aplican en otra copia o no se guardan).

## Entorno y dónde corre cada script

| Script | Qué hace | Dónde corre |
|---|---|---|
| `scripts/inspeccionar_pbix.py` | Inventario del ZIP: partes, tamaños, codificación, formato del reporte | Cualquier Python 3 |
| `scripts/leer_reporte.py` | Lector unificado Layout/PBIR → CSV + `resumen.json` | Cualquier Python 3 |
| `scripts/leer_modelo.py` | Modelo: DAX, M, relaciones, RLS, formatos, variaciones, lineageTag (pbixray o, si no está, TMDL) | pbixray: Windows o red con PyPI · TMDL: cualquier Python 3 |
| `scripts/leer_modelo_tmdl.py` | Modelo desde el TMDL que escribe Power BI (pestaña de la vista TMDL o carpeta .pbip), sin dependencias | Cualquier Python 3 |
| `scripts/cruzar_reporte_modelo.py` | Referencias rotas, objetos sin uso, alertas de formato | Cualquier Python 3 |
| `scripts/modificar_layout.py` | Edición del reporte en formato clásico | Cualquier Python 3 |
| `scripts/pbir.py` | Conversión de visuales a PBIR y reemplazo de páginas en un PBIR | Cualquier Python 3 |
| `scripts/tmdl_medidas.py` | Genera script TMDL para cambiar formatos de medidas | Cualquier Python 3 |
| `scripts/tema_powerbi.py` | Temas de Power BI (JSON) por dirección visual; inyección en PBIR [probado] | Cualquier Python 3 |
| `scripts/revisar_html.js` | Puertas objetivas de un diseño HTML antes de replicarlo (node + playwright) | Node con playwright |
| `scripts/scripts_modelo.py` | Incrusta pestañas TMDL/DAX listas para ejecutar (medidas con formato en un paso) | Cualquier Python 3 |
| `scripts/capas_html.js` | Diseño de 2 capas → imagen de fondo (decoración), cajas de los visuales y vista compuesta | Node con playwright |
| `scripts/fondo_pagina.py` | Pone la imagen de fondo de página (clásico y PBIR) + papel tapiz | Cualquier Python 3 |
| `scripts/svg_medidas.py` | Medidas DAX que dibujan SVG (píldora Δ, bullet, anillo, sparkline, progreso) con su vista previa | Cualquier Python 3 |
| `scripts/deneb.py` | Plantillas Vega-Lite para Deneb con los tokens de la dirección | Cualquier Python 3 |
| `scripts/estilo_a_medida.py` | Dirección visual nueva desde 1–3 colores semilla + modo + carácter: neutros, acento, estados, categóricos (validados contra daltonismo) y secuencial con contraste calculado; se activa con `PBIX_TOKENS_EXTRA` en tema, HTML, LienzoV2 y Deneb | Cualquier Python 3 |
| `scripts/registro_disenos.py` | Registro de diseños entregados y comparación anti-repetición (arquetipo, estilo, acento, héroe, visuales firma) | Cualquier Python 3 |
| `scripts/componentes.py` | Maqueta reutilizable. **`LienzoV2`** (estilo v2 desde `tokens.json`): `encabezado_v2`, `kpi_heroe`, `tira_kpi`, `seccion_v2` (caja o regla), `tabla_top` (top N = filas que caben, sin barra), `estado`, `pie`, `titulo_visual`, `orden_lectura()`, `ancho_texto()`; `kpi_heroe(delta_medida=…)` con la variación nativa; posiciones en rejilla de 8. `Lienzo` (v1) sigue igual | Cualquier Python 3 |
| `scripts/auditoria.py` | Auditoría [P] de diseño (guía §10): unidad/periodo en títulos, solapes, contraste, rejilla, márgenes, tamaños/pesos, colores fuera de tokens, radios, texto alternativo, orden de tabulación, estados de botón. `verificar_pbix.py` muestra el resumen | Cualquier Python 3 |
| `scripts/plataforma.py` | Plataforma de un .pbix (Report Server / servicio, release, versión) y compatibilidad | Cualquier Python 3 |
| `scripts/catalogo.py` | Catálogo oficial de visuales (roles, objetos, propiedades, enums) + evidencia; valida visuales y temas | Cualquier Python 3 |
| `scripts/verificar_pbix.py` | Verificación antes de entregar (clásico o PBIR) + plataforma + catálogo; `--cli` = validate de Microsoft | Cualquier Python 3 (`--cli`: Node ≥ 20 + CLI) |
| `scripts/verificar_pbir.py` | Verificación estructural de un PBIR (la usa `verificar_pbix.py`) | Cualquier Python 3 |

**Leer el modelo: dos caminos, misma salida** (`leer_modelo.py --fuente auto|pbixray|tmdl`; `auto` = pbixray si está, si no TMDL):
1. **pbixray** (`pip install pbixray`): descomprime el DataModel (XPress9) y da el modelo **actual** sin pasos del usuario. Necesita
   Windows o un entorno cuya red permita `pypi.org` y `files.pythonhosted.org` (en claude.ai lo habilita un administrador de la
   organización). Si `import pbixray` falla, intenta `pip install pbixray` una vez; si la red lo bloquea, dilo y pasa al 2 (no lo rodees).
2. **TMDL** (sin dependencias, cualquier entorno): pide al usuario, una vez por archivo, *vista TMDL → pestaña nueva (+) →
   arrastrar «Modelo semántico» desde el panel Datos (pestaña Modelo) → no aplicar → Ctrl+S*; o usa la carpeta `.SemanticModel`
   de un .pbip. Es una **foto**: si el modelo cambió después, hay que volver a arrastrarlo. [probado: Desktop de la nube 2026.09
   y Desktop para RS 2026.05; mismo resultado que pbixray en columnas, medidas con formato y expresión, relaciones,
   variaciones y cruce]. Los datos incrustados en M («Especificar datos») no se leen.

## Flujo de lectura

1. **Inventario**: `python scripts/inspeccionar_pbix.py archivo.pbix`. Mira `formato_reporte`:
   - `Layout clásico` → parte `Report/Layout` (JSON en UTF-16 LE). Detalle en `references/estructura_layout.md`.
   - `PBIR` → carpeta `Report/definition/` (un JSON UTF-8 por página y por visual). Detalle en `references/estructura_pbir.md`.
   - El Desktop de la nube reciente **convierte a PBIR al guardar**; el Desktop para Report Server guarda en Layout clásico. [probado]
   - Mira también `plataforma`: quién guardó el archivo (Desktop para Report Server o de la nube), release y versión.
2. **Reporte**: `python scripts/leer_reporte.py archivo.pbix salida/`. Produce, igual para ambos formatos:
   `paginas.csv`, `objetos.csv`, `referencias.csv` (una fila por campo base distinto en cada proyección), `campos.csv`,
   `filtros.csv` (reporte/página/visual, con la condición traducida a texto), `formato.csv` (campos usados en formato condicional,
   títulos dinámicos, etc.), `estados_slicer.csv` (selección guardada de cada slicer) y `resumen.json`. [probado]
3. **Modelo**: `python scripts/leer_modelo.py archivo.pbix salida/` (pbixray o TMDL, ver arriba) → `modelo_<archivo>.json` con la salida de pbixray
   (tablas, `dax_measures`, `dax_columns`, `relationships`, `power_query` con el M completo, `rls`, `statistics`) y, por SQL directo,
   columnas y medidas con formato, oculta, resumir por, ordenar por, lineageTag, variaciones de fecha, relaciones con nombre y anotaciones.
   Ver `references/modelo_y_formatos.md`. [probado: pbixray y formatos; variaciones y relaciones por SQL coinciden con el TMDL del mismo modelo · por validar: anotaciones]
4. **Cruce**: `python scripts/cruzar_reporte_modelo.py salida/ salida/modelo_<archivo>.json salida/cruce/` → `hallazgos.csv`:
   referencias rotas (p. ej. una medida borrada que sigue en un formato condicional), medidas/tablas sin uso, medidas intermedias,
   fechas con formato largo en ejes, textos de mes sin "ordenar por", números sin formato, números guardados como texto
   (`numero_como_texto`). [probado]
5. **Reporta** al usuario con cifras, no con impresiones: páginas, objetos (con datos), referencias, campos (medidas), tablas,
   filtros (con condición), estados de slicer, hallazgos de severidad alta/media.

### Reglas de interpretación [probado]

- Referencias: una por entrada de proyección y por campo base distinto (`X / ScopedEval(X)` cuenta una vez).
- Nodos de expresión que deben resolverse: `Column`, `Measure`, `Aggregation` (0 Sum, 1 Avg, 2 DistinctCount, 3 Min, 4 Max,
  5 Count, 6 Median…), `HierarchyLevel` (con `PropertyVariationSource` = jerarquía automática de fecha), `Arithmetic`, `ScopedEval`,
  `SparklineData`, `GroupRef` (agrupaciones del reporte, existen en el modelo como columna). Si `resumen.json` trae
  `nodos_no_reconocidos`, es un caso nuevo: documéntalo.
- `formato.csv` encuentra campos que **solo** aparecen en formato condicional; cuentan para linaje y para referencias rotas.
- Los nombres de variaciones y jerarquías de fecha dependen del idioma del modelo ("Variation"/"Date Hierarchy" vs
  "Variación"/"Jerarquía de fechas"): léelos, no los supongas.

## Formatos de columnas y medidas

El formato (`FormatString`) es una propiedad del modelo; los visuales lo heredan. El reporte guarda copias parciales en caché que
**no sirven como fuente**. Léelo con `leer_modelo.py` (pbixray no lo expone en sus DataFrames públicos para medidas). [probado]

Antes de construir o modificar visuales, revisa en `hallazgos.csv` o en el modelo:
- fechas usadas como categoría con `Long Date` / `General Date` (ejes ilegibles: "lunes, 01 de diciembre de 2025");
- montos sin moneda, porcentajes sin `%`, medidas recién creadas sin formato (la vista de consultas DAX no les pone formato,
  salvo `0` a las enteras);
- textos de mes sin "ordenar por" (saldrían alfabéticos: usa la columna de fecha de mes como eje).

**Locale** [probado]: el formatString se muestra con la configuración regional del lector (Windows en el Desktop, navegador en el
portal de RS); `FORMAT()` sin cultura usa la del modelo y `USERCULTURE()` **no** coincide con ninguna de las dos en RS 2026.05
(Desktop: es-ES vs formatString en inglés; portal: al revés) [probado]. Regla:
**toda cifra visible va nativa** (medida numérica con formatString: tarjeta, tabla, eje) — es lo único que sigue al lector.
Las medidas SVG van **solo con forma** (`svg_medidas`: `cifras=False` por defecto: píldora = fondo + flecha, anillo sin %); la
variación del KPI va como cifra nativa con color por regla (`LienzoV2.kpi_heroe(delta_medida=…)`, formato `+0.0 %;-0.0 %`).
Texto que no puede ser nativo (título-conclusión dinámico, etiquetas de Deneb): cultura del modelo (`cultura='modelo'`,
`FORMAT` sin tercer argumento; Deneb `pbiFormat`). Un locale fijo (`'en-US'`) solo si el usuario lo pide. Columnas que llegan como texto desde
Power Query no toman formato: tipa en Power Query (ver `references/modelo_y_formatos.md`).

Cómo resolver, de mejor a peor: (1) cambiar el formato en el modelo vía TMDL (ver *Editar el modelo*) o pedirlo al usuario;
(2) fijar unidades y decimales en el propio visual (`labelDisplayUnits`, `labelPrecision`); (3) medida de texto con `FORMAT()`
(sirve para tarjetas y tablas, no para gráficos).

## Diseñar o rediseñar un reporte

Lee primero `references/lecciones.md` y `references/guia_diseno.md` (reglas operativas), luego `references/diseno_reportes.md`
(proceso) y `references/disenos/README.md` (referencias por tipo y mapa HTML → Power BI). Orden obligatorio:

1. **Brief en una sola ronda de preguntas cerradas** con opción recomendada (`guia_diseno.md` §1): alcance (solo apariencia /
   rediseño / desde cero) y tipo de reporte + público **siempre**; decisión y cifra de 5 s, medio, comparación y polaridad/meta de
   cada KPI, navegación, **nivel de impacto (sobrio / realzado / impactante) siempre**, estilo (a la medida —recomendado en
   rediseño y desde cero— o una dirección fija), plataforma, formato regional; recursos de marca (logo, colores, fotos) solo si la
   persona los quiere agregar. Lo no respondido = supuesto declarado, sin pausa. Sugiere el nivel según el público (§12).
2. **Idea propia, no plantilla** (`guia_diseno.md` §2b). Las direcciones fijas y los diseños de `references/disenos/` enseñan
   técnicas; **no se copian**. Para cada reporte nuevo:
   - carácter en 3 adjetivos + 2–4 referencias externas (`references/inspiracion.md`; sin web, su catálogo de ideas);
   - **arquetipo** de página por la premisa (`references/arquetipos.md`, 18 estructuras), distinto entre variantes;
   - **estilo a la medida**: `python scripts/estilo_a_medida.py --nombre <n> --modo claro|oscuro --semillas "#hex,#hex"
     --caracter <c> [--capas 2] --salida estilos/<n>.json` (contraste, daltonismo y estados calculados) y
     `PBIX_TOKENS_EXTRA=estilos/<n>.json` para que tema, HTML, LienzoV2 y Deneb lo usen;
   - cada rasgo pasa por `references/traductor_powerbi.md` (nativo → SVG → 2 capas → Deneb → AppSource, `references/appsource.md`)
     con su estado en la plataforma; lo [sin traducción] no se diseña;
   - `python scripts/registro_disenos.py comparar --ficha propuesta.json`: si dice REPITE frente a otro reporte, cambia arquetipo,
     estilo o héroe (las páginas de un mismo reporte comparten estilo a propósito).
3. **Premisa causal y variantes**: en rediseño/desde cero, 2–3 variantes HTML desde premisas y arquetipos distintos, puertas
   (`node scripts/revisar_html.js`) y rúbrica; se replica la ganadora, las otras van en anexo. Generador: `references/disenos/_fuente/base.py`
   con la dirección elegida (fija o a la medida), nombres reales del modelo, cifras ficticias.
   En **impactante** al menos una variante innovadora (§12) y el diseño va en 2 capas (§11): `fondo(...)` + paneles.
4. **Ficha de decisiones + pie de confianza** en el HTML (fuente · actualizado · definiciones); la ficha incluye la tabla de
   inspiración (fuente · qué se toma · traducción · estado en RS), el arquetipo y el estilo con sus semillas.
5. **Réplica en Power BI** bloque a bloque (`componentes.py`, catálogo, tema de la dirección con `tema_powerbi.py`, que lee
   `references/tokens.json` y los estilos de `PBIX_TOKENS_EXTRA`), respetando la plataforma (Report Server: clásico). En "solo apariencia": tema, formatos y estilos.
   **2 capas**: `node scripts/capas_html.js diseño.html` → `fondo_pagina.py` pone `_fondo.png` de fondo y los visuales van en las
   cajas de `_visuales.json`, transparentes (tema aurora/vidrio). Realzado/impactante: medidas SVG con `svg_medidas.py`
   (en el script TMDL, `dataCategory: ImageUrl`) y 1–2 Deneb con `deneb.py`. Efectos y su estado en RS: `efectos_powerbi.md`.
6. **Medidas y formatos nuevos** listos dentro del archivo con `scripts/scripts_modelo.py` (pestaña TMDL "Aplicar" + DAX de comprobación)
   [probado: Desktop para RS 2026.05 y Desktop de la nube 2026.09]: el usuario solo abre la vista TMDL, pulsa Aplicar y guarda. Nunca entregues DAX suelto para pegar a mano.
7. **Verifica, audita y registra**: `verificar_pbix.py`, auditoría en 3 fases (`guia_diseno.md` §10) y captura vs PNG del HTML. Informa por
   niveles (HTML / .pbix / verificado con captura). Al entregar: `registro_disenos.py agregar --ficha …`.

## Editar el reporte (solo si el usuario lo pide)

Lee primero `references/edicion_reporte.md`. Resumen:

- **Report Server** → siempre formato clásico sobre el archivo guardado por el Desktop para RS; lee `references/report_server.md`.
- **Formato clásico** → `scripts/modificar_layout.py` (clase `Pbix`): orden, vista y visibilidad de páginas, tema personalizado, mover/redimensionar, títulos y propiedades de formato,
  quitar/reordenar campos, renombrar `queryRef`, formato condicional, filtros, páginas, visuales nuevos, clonar visuales,
  agregar partes (p. ej. pestaña de consultas DAX). Reglas de empaquetado [probado]:
  `Report/Layout` en UTF-16 LE sin BOM; `DataModel` copiado byte a byte y sin compresión ZIP; quitar `SecurityBindings` y su
  `Override` en `[Content_Types].xml`; al cambiar campos de un visual, borrar sus cachés `query` y `dataTransforms`;
  la posición vive en dos sitios (contenedor y `config.layouts[0].position`).
- **PBIR** (solo servicio) → construye los visuales con `modificar_layout.py` sobre una copia clásica y conviértelos con
  `pbir.visual_layout_a_pbir`; luego `pbir.reemplazar_pagina` sobre el PBIR guardado por el usuario (conserva su modelo).
  Regla crítica [probado]: en PBIR cada campo debe nombrar su tabla con `SourceRef.Entity`; un alias (`Source`) hace que el archivo
  no abra, sin mensaje útil. Interacciones: `type: "NoFilter"` (en clásico `3`). Vista: `"FitToWidth"` para páginas altas.
- **Verifica siempre** antes de entregar (`python scripts/verificar_pbix.py nuevo.pbix base.pbix modelo.json [--destino=rs:2026.05]`):
  plataforma y release de destino (archivo de la nube, PBIR o visuales no soportados en Report Server), ZIP íntegro, mismo `DataModel`, todo campo existe en el modelo, sin selectores huérfanos,
  sin ids/z repetidos, nada fuera de la página, navegación a páginas existentes, y en PBIR comparación estructural contra los
  `visual.json` que el propio Power BI escribió (ninguna ruta JSON que Desktop no use).
  También avisa de textbox con altura menor a la mínima (provoca barra de desplazamiento) y del piso más conservador del CLI.
  Siempre valida con el catálogo (objetos, propiedades, enums, tipo de literal, tema, visuales no soportados en RS). Con `--cli`
  corre además `powerbi-report-author validate` sobre el PBIR extraído a una carpeta temporal (ver `references/estructura_pbir.md`).
  Literales: enums numéricos con `dint` (`1D`), enteros con `lit(int)` (`8L`), decimales con `dnum`. [probado]
- **Lo que no se puede desde el reporte:** crear medidas/columnas/tablas o cambiar M. **Preferido:** incrusta el script con
  `scripts_modelo.incrustar()` (pestaña TMDL que crea medidas con formato; el usuario solo pulsa Aplicar). Alternativa: un script
  `DEFINE MEASURE …` para la **vista de consultas DAX** y pide al usuario *Ejecutar* → *Actualizar modelo con cambios*.
  Puedes incrustarlo como pestaña (`DAXQueries/<nombre>.dax` en UTF-16 + `DAXQueries/.pbi/daxQueries.json`), pero entrega también
  el `.dax` suelto por si no aparece. [probado] Después, trabaja sobre el archivo que el usuario **guardó** (las medidas viven ahí).
- **Ciclo con el usuario:** genera versión → el usuario abre y manda captura → ajustas. Las propiedades que Power BI ignora no dan
  error; solo se ven en pantalla (ver lista en `references/edicion_reporte.md`).

## Editar el modelo (formatos, medidas) vía TMDL

Para Report Server: los cambios se hacen en el Desktop para RS sobre el archivo de RS (nunca copiando el `DataModel` de la nube).
El Desktop para RS 2026.05 tiene vista de consultas DAX y vista TMDL [probado] (ver `references/report_server.md`).

Lee `references/edicion_modelo.md`. Resumen [probado salvo donde se indica]:

1. Trabaja en una **copia** del .pbix.
2. Genera el script: `python scripts/tmdl_medidas.py modelo.json cambio.tmdl "Tabla[Medida]=formato" …`.
   Para **columnas**, pide al usuario que arrastre la columna al editor TMDL (Power BI genera la definición completa con variación,
   lineageTag y anotaciones), que guarde ese texto en un archivo y cambie solo la línea necesaria.
3. `createOrReplace` + `ref table <Tabla>` modifica objetos sin reemplazar la tabla, **pero reemplaza el objeto completo**:
   lo que no se escriba se pierde. Una columna de fecha sin su `variation` hace fallar el script
   ("Table 'LocalDateTable_…' with ShowAsVariationsOnly…") y no se aplica nada.
4. Una medida reescrita sin su `lineageTag` recibe uno nuevo (los visuales la siguen por nombre; herramientas de linaje la verían
   como nueva). `tmdl_medidas.py` lo incluye [por validar que lo conserve].
5. El usuario aplica en la vista TMDL, **guarda (Ctrl+S)** y vuelve a correr `leer_modelo.py`; compara antes/después y confirma que
   solo cambió lo pedido.

## Cifras de control (regresión)

Si cambias los scripts, regenera el demo sintético (`python demo/crear_demo.py`) y comprueba que la lectura da lo mismo:

| Archivo | Formato | Páginas | Objetos (con datos) | Referencias | Campos (medidas) | Tablas | Filtros | Estados slicer |
|---|---|---|---|---|---|---|---|---|
| `demo/demo_ventas.pbix` | Layout | 2 | 6 (6) | 12 | 10 (5) | 2 | 1 (1 pág.) | 0 |

Modelo (`leer_modelo.py … --fuente tmdl`): 9 columnas, 5 medidas, 1 relación. Cruce: 5 hallazgos sembrados a propósito —
`referencia_rota` Ventas[Medida borrada] (alta), `texto_mes_sin_orden` Ventas[Mes] y `numero_como_texto` Ventas[Costo] (media),
`medida_sin_formato` Ventas[Ventas sin formato] (baja) y `medida_sin_uso` Ventas[Ticket promedio] (info). El demo no se abre en
Power BI Desktop: su DataModel es un marcador vacío.

## Referencias

- `README.md` (para personas: qué hace, requisitos, instalación), `CHANGELOG.md` (versiones), `EXAMPLES.md` (pedidos tipo y
  el flujo que debe seguir cada uno) y `CHECKLIST.md` (brief, verificación antes de entregar y auditoría de diseño).
- `references/guia_diseno.md` — reglas operativas de diseño (brief, variantes, direcciones, tipografía, color, confianza, auditoría).
- `references/lecciones.md` — errores frecuentes y la regla que los evita; se lee en el brief.
- `references/tokens.json` — tokens de las direcciones (fuente única para HTML y tema).
- `references/disenos/` — diseños de referencia HTML por tipo de reporte y por nivel de impacto + mapa HTML → Power BI
  (los de 2 capas incluyen `_fondo.png` y `_visuales.json` de ejemplo).
- `references/efectos_powerbi.md` — efectos nativos, medidas SVG, Deneb/HTML Content y lo que Power BI no hace; estado en RS.
- `references/deneb/<dirección>/` — plantillas Vega-Lite listas para pegar (área con degradado, anillo, bullet, mancuerna).
- `references/report_server.md` — Report Server vs servicio: detección, reglas de compatibilidad, lo que RS no tiene, diseño.
- `references/plataformas.json` — releases de Report Server, visuales no soportados o por release, lo observado en archivos.
- `RECONOCIMIENTOS.md` — autoría, software, fuentes de diseño y referencias consultadas (consérvalo al compartir).
- `references/estructura_layout.md` — Layout clásico: doble parseo, alias, proyecciones, filtros, objetos, codificaciones.
- `references/estructura_pbir.md` — PBIR: archivos, equivalencias con Layout, lo validado y lo pendiente.
- `references/modelo_y_formatos.md` — DataModel, pbixray (API pública e interna), SQLite, lectura por TMDL, códigos TOM, formatos, M, DataMashup.
- `references/diseno_reportes.md` — brief, tipos de reporte, reglas de diseño en Power BI, direcciones visuales y revisión.
- `references/inspiracion.md` — cuándo y cómo buscar inspiración externa, fuentes por familia, catálogo de ideas sin web, ficha.
- `references/arquetipos.md` — 18 estructuras de página por premisa, con rejilla, héroe, visuales y estado en Report Server.
- `references/traductor_powerbi.md` — intención de diseño → técnica (nativo / SVG / 2 capas / Deneb / AppSource) y su estado.
- `references/appsource.md` — visuales personalizados: criterios (certificado, sin licencia, sin Internet, RS) y lista curada.
- `references/visuales_powerbi.md` — trabajo del dato → visual y notas de uso; apunta al catálogo.
- `references/catalogo/` — 57 visuales nativos del CLI oficial de Microsoft (0.5.0): `<tipo>.json` (roles, objetos, propiedades con
  tipo y valores), `_vcos.json` (contenedor), `_indice.json` (deprecado, nombre del Desktop, servicio / Report Server),
  `_evidencia.json` (guardado por el Desktop, se ve, ignorado).
- `references/edicion_reporte.md` — operaciones, empaquetado, patrones de formato que funcionan y los que Power BI ignora.
- `references/edicion_modelo.md` — vista de consultas DAX y vista TMDL: reglas y errores conocidos.
- `references/limitaciones.md` — lo que no se puede o no está validado.
- `references/ejemplos/` — scripts completos sobre un reporte de inventario (tabla FactMovimientos, medidas RV), para usar como
  plantilla: **`comite_aurora_rs_2capas.py`** (2 capas en Report Server, [probado] en Desktop y servidor RS), `catalogo_cambios.py`
  (catálogo de cambios en clásico), `roadmap_pagina.py` + `roadmap_medidas.dax` + `roadmap_inyectar_pbir.py` (réplica nativa de un
  dashboard HTML e inyección en PBIR), `rediseno_dos_versiones.py` y `rediseno_report_server.py` (rediseño de todas las páginas en
  dos direcciones con portada y navegación) y `columna_fecha_generada_por_powerbi.tmdl`. Ajusta archivos, páginas y campos.
- `demo/` — `demo_ventas.pbix` sintético y `crear_demo.py`, que lo genera (cifras de control arriba).
