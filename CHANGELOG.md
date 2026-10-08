# Cambios

## 2.6.4 · 2026-10-08 — versión pública

**Lectura (solo metadatos)**
- Inventario del .pbix y detección de plataforma: Power BI Report Server o servicio, release, versión y formato (Layout clásico o PBIR).
- Reporte: páginas, visuales, referencias, campos, filtros con su condición, formato condicional y estados de slicer, igual en
  Layout clásico y PBIR (`leer_reporte.py`).
- Modelo: DAX, M, relaciones, RLS, formatos, variaciones y lineageTag con pbixray o, sin dependencias, desde el TMDL que escribe
  Power BI (`leer_modelo.py`, `leer_modelo_tmdl.py`).
- Cruce reporte-modelo: referencias rotas, objetos sin uso, medidas sin formato, meses sin «ordenar por», fechas largas en ejes y
  números guardados como texto (`cruzar_reporte_modelo.py`).

**Edición**
- Layout clásico (`modificar_layout.py`): páginas, vista, tema personalizado, visuales, filtros, formato condicional y títulos.
- PBIR (`pbir.py`): conversión de visuales y reemplazo de páginas conservando el modelo.
- Medidas y formatos listos para aplicar dentro del .pbix: pestaña TMDL «Aplicar» y pestaña DAX de comprobación (`scripts_modelo.py`).
- Verificación antes de entregar (`verificar_pbix.py`) con catálogo de 57 visuales del CLI de Microsoft y evidencia por propiedad,
  compatibilidad con Report Server y validación opcional con el CLI.

**Diseño**
- Brief en una ronda, premisa causal, variantes en HTML con puertas automáticas (`revisar_html.js`) y réplica con visuales nativos.
- Niveles sobrio, realzado e impactante: diseño en 2 capas con imagen de fondo, medidas SVG y plantillas Deneb.
- Estilos a la medida con contraste WCAG y daltonismo calculados (`estilo_a_medida.py`), 18 arquetipos de página y registro
  anti-repetición de diseños (`registro_disenos.py`).
- Auditoría de diseño en 3 fases (`auditoria.py`) y 9 diseños de referencia con datos ficticios.

**Uso y distribución**
- `demo/demo_ventas.pbix` sintético con cinco fallas sembradas y `demo/crear_demo.py`; «Prueba en 2 minutos» en el README.
- Todos los scripts responden a `--help` y explican qué falta si se corren sin argumentos o con un archivo que no es .pbix.
- Instalable como skill (claude.ai o Claude Code) o como plugin/marketplace de Claude Code.
- Licencia MIT, `NOTICE.md` (contenido de terceros y aviso MIT de Microsoft) y `RECONOCIMIENTOS.md`.
