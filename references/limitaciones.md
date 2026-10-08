# Limitaciones y pendientes

## No se puede
- Leer o escribir filas de datos (fuera de alcance por diseño).
- Escribir el DataModel directamente: crear/cambiar medidas, columnas, tablas, M o formatos requiere la vista DAX o TMDL en Desktop.
- Ver el resultado en pantalla: no hay Power BI Desktop en el entorno de Claude; cada cambio visual necesita una captura del usuario.
- Validar contra el esquema JSON oficial de PBIR si la red bloquea developer.microsoft.com.
- Instalar pbixray donde PyPI esté bloqueado: el usuario lo ejecuta en su Windows.

## Por validar

- Report Server: marcadores en el servidor; tema personalizado
  en clásico (item 201); `displayOption` 2 en clásico; botones de navegación; abrir en el Desktop para RS un archivo de la
  nube más viejo que el servidor; visual personalizado HTML Content publicado en el servidor.
- PBIR: filtros (`filterConfig`), grupos (`visualGroup`), marcadores, `reportExtensions.json`, página oculta, PBIR nacido como PBIR.
- Parte `DataMashup` (archivos antiguos) y `DataModelSchema` (.pbit).
- `leer_modelo.py`: consultas de variaciones, relaciones con nombre y anotaciones (estructura conocida por el TMDL generado por Desktop).
- TMDL: conservar `lineageTag` al reescribir medidas; expresiones multilínea; generar columnas completas desde metadatos.
- Significado exacto de `relationships.type = 1` (Layout clásico).
- Tamaño de página y alturas: probados a 1280 px de ancho; otros lienzos requieren ajustar.
- Temas: nombres de propiedades de `visualStyles` por tipo de visual (la inyección ya está probada).
- `actionButton` con texto y `visualLink` PageNavigation (botones de la barra de navegación).
- `displayOption: FitToWidth` en PBIR (Desktop lo guardó como FitToPage).
- `columnFormatting.labelPrecision` por columna en `tableEx` (visto en matrices de reportes reales).
- Visuales conocidos sin archivo de prueba: `cardVisual`, `kpi`, `waterfallChart`, `funnel`, `decompositionTreeVisual`, `donutChart`, `areaChart`, apilados al 100 %.
- Slicer clásico (`slicer`) en mosaico: no hay propiedad para el color del estado seleccionado; para eso, `advancedSlicerVisual`
  (botones; RS desde 2026.05) [por validar: estados de botón].
- `validate` del CLI de Microsoft solo acepta PBIP (se resuelve extrayendo el PBIR, ver `estructura_pbir.md`); no valida Layout
  clásico (para eso, `scripts/catalogo.py`). Su catálogo es de la nube: para Report Server es referencia.
