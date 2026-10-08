# Pedidos tipo y el flujo que debe seguir cada uno

Cada ejemplo indica qué preguntar, qué correr y qué entregar. Si el pedido no encaja en ninguno, aplica el más parecido.

### 1. «¿Qué tablas y medidas usa este reporte?»
Lectura pura. Sin preguntas salvo confirmar que se puede procesar el archivo (información de la empresa).
`inspeccionar_pbix.py` → `leer_reporte.py` → `leer_modelo.py` (pbixray si está; si no, TMDL: pedir que arrastren «Modelo semántico»
a la vista TMDL y guarden) → `cruzar_reporte_modelo.py`.
Entrega: cifras (páginas, visuales, referencias, medidas, tablas, filtros), plataforma y release, hallazgos alta/media. Sin
cambios en el archivo.

### 2. «Haz el inventario para documentar el linaje»
Igual que 1, más `referencias.csv` y `campos.csv` por página/visual y, del modelo, el M de cada tabla (origen). Entrega:
tabla campo del reporte → tabla del modelo → consulta/origen. No inventes el origen si el M no lo dice.

### 3. «¿Puedo publicar este .pbix en nuestro Report Server?»
`plataforma.py archivo.pbix rs:<release>`. Responde con quién lo guardó (Desktop para RS o de la nube), release, formato y
qué lo impide (visuales no soportados, PBIR, release más nuevo). Si viene de la nube, explica cómo llevarlo a RS.

### 4. «Revisa los formatos» / «los números salen raros»
Cruce (`numero_como_texto`, fechas largas en ejes, medidas sin formato, meses sin ordenar) + formato regional del brief.
Entrega: hallazgos y una pestaña TMDL «Aplicar» dentro de una copia del archivo (`scripts_modelo.incrustar`); columnas de
fecha: indicar arrastrarlas al editor TMDL.

### 5. «Agrega una medida de variación vs año anterior»
Pregunta polaridad (¿subir es bueno?) y formato si no se deducen. Genera la medida con formato y carpeta con
`scripts_modelo.tmdl_medidas` + `incrustar` (y una pestaña DAX de comprobación con un total). Entrega la copia del .pbix y
los pasos: vista TMDL → Aplicar → guardar.

### 6. «Cambia solo la apariencia del dashboard»
Alcance = solo apariencia: no mover visuales ni tocar DAX. Pregunta dirección/marca y formato regional. Aplica tema
(`tema_powerbi.py`) y estilos; verifica (`verificar_pbix.py`). Si la disposición tiene problemas, propónlo aparte.

### 7. «Rediseña el reporte X para el comité»
Brief en una ronda (alcance, tipo, público, decisión y cifra de 5 s, medio, polaridad/meta, navegación, **nivel de impacto**,
dirección, plataforma, formato regional; marca solo si la quieren agregar) → premisa causal → 2–3 variantes HTML desde `references/disenos/<tipo>.html` → `revisar_html.js` + rúbrica →
réplica de la ganadora (`componentes.py`, tema) → medidas nuevas incrustadas → verificación y auditoría → entrega: .pbix nuevo,
HTML con ficha, anexo de variantes, lista de supuestos y nivel alcanzado (HTML / .pbix / verificado con captura).

### 8. «Créame un dashboard desde cero con este modelo»
Como 7, pero primero leer el modelo para saber qué medidas existen y cuáles hay que crear (incrustadas). La página se
construye sobre una copia del .pbix guardada por el Desktop de la plataforma de destino.

### 9. «Este dashboard es para la pantalla del almacén»
Medio = pantalla mural → dirección `grafito`, tipo operativo, tamaños mayores, sin depender de tooltips; avisar que el PDF y
las suscripciones saldrán oscuros.

### 10. «Pásame el reporte a la nube» / «a Report Server»
Detectar plataforma. A la nube: abrir y guardar con el Desktop de la nube (pasa a PBIR). A RS: solo si el release de origen
es igual o anterior y en formato clásico; si no, reconstruir sobre un archivo guardado por el Desktop para RS.

### 11. «Hazlo más llamativo» / «quiero algo impactante para la junta»
Preguntar el nivel (sugerir **impactante** para junta/comité/pantalla, **realzado** para ejecutivos en laptop) y si quieren
agregar recursos de marca. Impactante: dirección `aurora` (sala, oscuro) o `vidrio` (laptop, claro); variantes con al menos una
innovadora (guía §12); diseño en 2 capas → `capas_html.js` → `fondo_pagina.py`; visuales nativos transparentes en las cajas;
héroe con medida SVG (anillo) o Deneb (área con degradado); tabla con píldoras SVG. Referencias: `disenos/comite_aurora.html`,
`disenos/ejecutivo_vidrio.html`. Avisar: el fondo es una imagen, si se mueve un visual se regenera. En Report Server, decir qué
partes están [por validar] (`efectos_powerbi.md`).

### 12. «Que se vea moderno pero sin exagerar»
Nivel **realzado**: 1 capa, efectos nativos (sombra suave, barra de acento, botones con estados como pestañas), píldoras y
bullets SVG en tablas, máximo 1 Deneb. Referencia: `disenos/comercial_realzado.html`.

### 13. «No quiero que se vea igual que el anterior» / «inspírate en algo»
Guía §2b. Carácter en 3 adjetivos (p. ej. comité de una empresa de alimentos: «cálido, confiable, artesanal»); 2–4 referencias
(`inspiracion.md`: editorial + mundo físico, o el catálogo sin web: «diario financiero en papel») con qué se toma de cada una;
`estilo_a_medida.py --nombre cosecha --modo claro --semillas "#8C5A2B,#2E5E4E" --caracter calido --salida estilos/cosecha.json`;
arquetipo por la premisa (`titular_grafico` para «¿por qué bajó el margen?»; `puente` como variante B);
`registro_disenos.py comparar` → DISTINTO; HTML con `PBIX_TOKENS_EXTRA=estilos/cosecha.json` → puertas → réplica → registrar.

### 14. «¿Puedo usar este visual de AppSource?»
`appsource.md`: comprobar insignia de certificado y versión en el momento; en Report Server, nada con licencia de AppSource,
clave propia o Internet; importar el .pbiviz desde archivo y probarlo en el Desktop para RS y en el portal antes de prometerlo.
Siempre con la alternativa nativa o SVG anotada.

## Qué NO hace (redirigir)
Dashboards web o HTML que no van a Power BI, hojas de Excel, consultas que devuelven filas de datos, cambios en Power Query o
en el origen de datos, publicar en el servidor por el usuario.
