# Power BI Report Server vs. servicio (nube)

La mayoría de los reportes de este usuario se publican en **Power BI Report Server (RS)**, on-premises; pocos en el servicio.
Cada archivo debe tratarse según la plataforma donde se va a publicar. Datos de releases y reglas: `plataformas.json`.

## Cómo saber para qué plataforma es un archivo [probado]

Las partes `Metadata` y `Version` del ZIP dicen qué Desktop lo guardó **por última vez** (no quién lo creó):

| Guardado por | `Metadata.CreatedFrom` | `CreatedFromRelease` | `Version` | Formato del reporte |
|---|---|---|---|---|
| Desktop para Report Server mayo 2026 | `OnPrem` | `2026.05` | `1.28` y `1.33`* | Layout clásico (tema base CY26SU05, config 5.73) |
| Desktop de la nube septiembre 2026 | `Cloud` | `2026.09` | `1.33` | PBIR |
| Desktop de la nube enero 2025 | `Cloud` | `2025.01` | `1.31` | Layout clásico |

\* El mismo Desktop para RS 2026.05 escribió `1.28` y, al volver a guardar el archivo tras usar consultas DAX y TMDL, `1.33`:
`Version` no indica el release; usa `CreatedFrom` y `CreatedFromRelease`. [probado]

`python scripts/plataforma.py archivo.pbix [rs:2026.05]` lo muestra y revisa la compatibilidad; `inspeccionar_pbix.py` y
`resumen.json` de `leer_reporte.py` lo incluyen como `plataforma`.

## Reglas para publicar en Report Server

1. **El Desktop para RS es otro programa** ("Power BI Desktop optimized for Power BI Report Server"). Sale 3 veces al año
   (enero, mayo, septiembre) con el servidor. Trabaja con el Desktop para RS del **mismo release del servidor**.
   **Observado**: el Desktop para RS 2026.05 **abre** un PBIR guardado por el Desktop de
   la nube 2026.09 (más nuevo) y, con «Guardar como», lo deja `OnPrem 2026.05` **sin convertirlo**: sigue en PBIR (Version 1.33),
   los 52 visuales, páginas, tema y report.json quedan idénticos en contenido, conserva las pestañas TMDL y agrega
   `SecurityBindings`. **Pero al publicarlo en el servidor RS 2026.05** («Guardar como › Power BI Report Server») dio «Ha habido un
   error al intentar guardar el informe en Power BI Report Server» [probado: la publicación de control de un archivo clásico
   en la misma carpeta, con el mismo usuario, subió y se ve en el portal] → **para Report Server, siempre Layout clásico**. `plataforma.revisar`: abrir/guardar = aviso; PBIR con destino RS = error.
2. **Nunca pases un archivo de RS por el Desktop de la nube.** Al guardarlo, queda `Cloud`, versión más nueva y en PBIR, y ya
   no sirve para RS. [probado: un archivo de RS 2026.05 guardado en la nube quedó `Cloud 2026.09`, versión 1.33, PBIR]
3. **Edita en Layout clásico** con `modificar_layout.py` sobre el archivo guardado por el Desktop para RS. El editor conserva
   `Version` y `Metadata` del original. No uses `pbir.py` ni `tema_powerbi.aplicar_tema_pbir` para RS.
4. **Un archivo de la nube** (más viejo o, según lo observado en 2026.05, incluso más nuevo que el servidor) se abre con el
   Desktop para RS del release del servidor y se guarda desde ahí («Guardar como»: queda OnPrem) antes de publicar. Si llegó en
   PBIR, sigue en PBIR: hasta confirmar que el servidor lo acepta, para un reporte nuevo es más seguro construir en Layout clásico
   sobre un archivo guardado por el Desktop para RS (regla 3).
5. **Cambios de modelo** (medidas, formatos) se hacen en el Desktop para RS sobre el archivo de RS, nunca copiando el
   `DataModel` de un archivo de la nube. El Desktop para RS 2026.05 **tiene vista de consultas DAX y vista TMDL** [probado]:
   medidas con `DEFINE MEASURE` + "Actualizar modelo con cambios"; formatos con un script TMDL (`tmdl_medidas.py`) y columnas de
   fecha arrastrándolas al editor. Entrega instrucciones con nombre `LEEME_*.txt`, nunca junto a un `.tmdl` con nombre parecido
   (el usuario pegó el .txt en la vista TMDL: "InvalidLineType … Línea 1").
6. **Verifica** con `python scripts/verificar_pbix.py nuevo.pbix base_RS.pbix modelo.json` (destino por defecto = release
   de la base). Marca: archivo de la nube, release más nuevo que el servidor, PBIR, visuales no soportados o que llegaron
   en un release posterior, marcadores y visuales personalizados por confirmar.

## Lo que Report Server no tiene (según Microsoft, revisado en octubre de 2026)

Dashboards y apps; suscripciones por correo de reportes Power BI (sí de paginados); alertas de datos; Q&A y Quick Insights;
visuales de R y Python; Key influencers; personalizar visuales; drillthrough entre reportes; parámetros M dinámicos;
modelos compuestos; actualización automática de página; exportar a PowerPoint; Analizar en Excel; exportar datos solo
resumidos; funciones en preview del Desktop. La tabla de Microsoft también marca **marcadores** como no disponibles:
[por validar] en el servidor del usuario antes de diseñar navegación con marcadores. Usa navegación entre páginas con botones.

Visuales por release: la tarjeta nueva (`cardVisual`) y el button slicer (`advancedSlicerVisual`, observado en un archivo RS
2026.05) llegaron a RS en mayo 2026. Los visuales personalizados funcionan si el administrador los permite.

## Diseño para Report Server

- Elige visuales por `plataformas.json` (no soportados / disponible desde) antes de proponer el diseño.
- Navegación con botones de página (`actionButton` + `visualLink` PageNavigation) [por validar en RS].
- Tema personalizado en clásico: `Pbix.tema_personalizado(tema_json)` [probado]: el Desktop para RS 2026.05 lo aplica (customTheme type 1 + item 201). Si Desktop no lo
  aplica, importa el JSON en Vista → Temas → Examinar temas con el Desktop para RS (camino seguro).
- Vista "ajustar al ancho" en clásico: `Pbix.vista_pagina(nombre, 'FitToWidth')` (= 2) [por validar].
- Exportar datos solo resumidos: si el público necesita el detalle, pon una tabla de detalle visible.

## Lo que se valida en cada release nuevo

1. Bajar el Desktop para RS del release y abrir un archivo de prueba; guardar; leer `Metadata`/`Version` y anotarlos aquí y
   en `plataformas.json` (`observado`).
2. Revisar novedades y cambios en learn.microsoft.com/power-bi/report-server/whats-new y /changelog.
3. Repetir las pruebas de visuales con el Desktop para RS y actualizar el catálogo (columna por plataforma).

## Visto en el servidor (portal web) [probado: RS 2026.05]

Un diseño de 2 capas publicado en clásico: se ven igual que en el Desktop la imagen de fondo, el tema personalizado,
los visuales transparentes, `cardVisual` (con `cardImage` SVG), las medidas SVG en tableEx, el areaChart y los slicers.
**Formatos**: el portal aplica los `formatString` con la configuración regional del NAVEGADOR/usuario («$152.430», «41,2%», eje
«$40.000» con un navegador en español), mientras el Desktop mostraba «$152,430». Los textos hechos con `FORMAT(…, "en-US")`
(píldoras SVG, medidas de texto) no cambian. Consecuencia: no se puede forzar un mismo locale para todos los lectores con
formatString. **Regla por defecto: cifras nativas** → toda cifra visible es una medida numérica con formatString; el texto que
no puede ser nativo usa la cultura del modelo y Deneb `pbiFormat`; locale fijo solo si se pide.
**Prueba de `USERCULTURE()` [probado: RS 2026.05] — NO da consistencia:**

| Dónde | `USERCULTURE()` | `FORMAT(1234.5, "$#,0.00", USERCULTURE())` | formatString `$#,0.00` |
|---|---|---|---|
| Desktop para RS (programa en español, Windows en inglés) | `es-ES` | `$1.234,50` | `$1,234.50` |
| Portal (navegador en español) | estilo inglés (la píldora salió «27.4 %») | estilo inglés | `$152.430`, `41,2%` |

Los formatString siguen la configuración regional (Windows en el Desktop, navegador en el portal) y `USERCULTURE()` sigue otra
cosa (idioma del Desktop; en el portal, aparentemente la cultura del servidor). Por eso las cifras van nativas y, para texto,
`svg_medidas` usa `cultura='modelo'` (FORMAT sin cultura); también acepta `'usuario'` (USERCULTURE) o una fija (`'en-US'`)
si el usuario la pide.
