# Formato clásico: Report/Layout

## Partes del ZIP (.pbix) [probado]

| Parte | Codificación | Contenido |
|---|---|---|
| `Version` | UTF-16 LE | p. ej. `1.28`, `1.31` |
| `[Content_Types].xml` | UTF-8 con BOM | tipos MIME; un `Override` por parte |
| `Report/Layout` | **UTF-16 LE sin BOM** | todo el reporte (páginas, visuales, filtros) |
| `DiagramLayout` | UTF-16 LE | posición de tablas en la vista de modelo; `nodeIndex` = nombre de tabla (no incluye tablas de fecha automáticas) |
| `Settings`, `Metadata` | UTF-16 LE | versión de Power Query, `CreatedFrom` (Cloud/OnPrem), release |
| `Connections` | UTF-8 | solo si se publicó: `RemoteArtifacts` (DatasetId, ReportId). No describe orígenes |
| `Report/LinguisticSchema` | UTF-16 LE | sinónimos de Q&A (opcional) |
| `Report/CustomVisuals/<id>/` | UTF-8 | paquetes de visuales personalizados; pueden estar empaquetados sin usarse |
| `Report/StaticResources/` | binario/JSON | imágenes registradas y tema base |
| `DAXQueries/` | UTF-16 LE | pestañas de la vista de consultas DAX (`<tab>.dax` con espacios como `%20`, `.pbi/daxQueries.json`) |
| `SecurityBindings` | binario | se elimina al modificar el archivo |
| `DataModel` | binario, **STORED** | backup ABF comprimido con XPress9 (empieza con "This backup was created using XPress9 compression.") |

No hay `DataMashup` ni `DataModelSchema` en .pbix modernos (metadatos mejorados): el M vive dentro del DataModel.

## Estructura del Layout

```
{ id, filters (texto JSON), resourcePackages, config (texto JSON), sections: [ página ... ] }
página: { name (id), displayName, ordinal, width, height, displayOption, filters (texto JSON),
          config (texto JSON: objects, visibility=1 si oculta, relationships = interacciones),
          visualContainers: [ visual ... ] }
visual: { x, y, z, width, height, tabOrder, filters (texto JSON), config (texto JSON),
          query, dataTransforms (cachés, opcionales) }
```

**Doble parseo:** `config`, `filters` (y `query`, `dataTransforms`) son JSON guardado como texto dentro del JSON.

`config` de un visual: `name` (id), `layouts[0].position` (copia de x/y/z/width/height/tabOrder — mantener ambas sincronizadas),
`singleVisual` o `singleVisualGroup` (grupo, sin datos), `parentGroupName`.

`singleVisual`: `visualType`, `projections` (rol → `[{queryRef, active?}]`), `prototypeQuery` (`From` alias→Entity, `Select`,
`OrderBy`), `columnProperties` (queryRef → displayName), `objects` (formato del visual), `vcObjects` (contenedor: título, fondo,
borde, encabezado, `visualLink`), `drillFilterOtherVisuals`, `hasDefaultSort`, `syncGroup`, `cachedFilterDisplayItems`.

## Páginas, tema y recursos [probado salvo donde se indica]

- Orden de pestañas = orden de `sections` (+ `ordinal`); página que abre = `config.activeSectionIndex`.
- Página oculta: `section.config.visibility = 1`. Vista: `section.displayOption` (1 = ajustar a página observado; 2 = ajustar
  al ancho, 3 = tamaño real [por validar]).
- `resourcePackages`: `SharedResources` (type 2) con el tema base (item type 202, `BaseThemes/CY26SU05.json`) y
  `RegisteredResources` (type 1) con imágenes (item type 100). Archivos en `Report/StaticResources/<paquete>/`.
- `config.themeCollection.baseTheme = {name, type: 2, version}`. Tema personalizado: `customTheme = {name, version, type: 1}` +
  item type 201 en `RegisteredResources` [por validar: así lo escribe `Pbix.tema_personalizado`].
- `Metadata` (`CreatedFrom` OnPrem/Cloud, `CreatedFromRelease`) y `Version` identifican el Desktop que guardó el archivo
  (ver `report_server.md`).

## Resolver el campo real [probado]

Cruza cada `projections[rol][i].queryRef` con el `Select` que tiene ese `Name` y resuelve su expresión con el alias del `From`.

- `queryRef` y `Select.Name` pueden estar viejos: un `Tabla.Columna` que en realidad apunta a otra tabla (`Tabla_copia`);
  medidas renombradas (`Ventas.Avance` → `Avance %`); un `CountNonNull(Producto.Código)` que en realidad es `Max`
  (Function 4) y `Sum(...CostoUnitario)` es `Avg`. `NativeReferenceName` trae la etiqueta visible real.
- Entradas de `Select` ausentes de `projections` suelen ser ordenamiento.
- Funciones de `Aggregation`: 0 Sum, 1 Avg, 2 DistinctCount, 3 Min, 4 Max, 5 Count (no vacíos), 6 Median, 7 StdDev, 8 Variance.
- `HierarchyLevel` → `Hierarchy.Expression.PropertyVariationSource` = jerarquía automática de fecha sobre una columna;
  si no, jerarquía de usuario.
- `Arithmetic` (operadores 0 + · 1 − · 2 × · 3 ÷) con `ScopedEval` = "% del total".
- `SparklineData` (medida + `Groupings`), `GroupRef` (agrupación definida en el reporte; existe en el modelo como columna).

## Filtros [probado]

Tres ámbitos: `Layout.filters`, `section.filters`, `visualContainer.filters`. Cada filtro: `name`, `expression` (campo),
`filter` (`From` + `Where` con `Condition`), `type` (Categorical, Advanced, RelativeDate, TopN…), `howCreated`,
`isHiddenInViewMode`, `isLockedInViewMode`. Condiciones: `In` (Values / Table), `Not`, `And`, `Or`, `Comparison`
(0 =, 1 >, 2 >=, 3 <, 4 <=), `Contains`, `StartsWith`, `EndsWith`, `Between`, `Exists`; literales `'texto'`, `12L`, `1.5D`,
`datetime'…'`, `null`. Un filtro sin `Where` es un filtro vacío (en reportes grandes suele ser la mayoría).

## Otros usos de campos [probado]

- **Formato condicional y títulos dinámicos** en `objects` / `vcObjects`: `FillRule` (gradientes), `Conditional` (reglas con `Cases`),
  `Measure` como valor. Pueden referenciar campos que no están en las proyecciones (y hasta medidas borradas).
- **Selectores** (`selector.metadata` = queryRef, `selector.data` = valores): no son campos nuevos.
- **Estado de slicer**: `objects.general[].properties.filter.filter` (con su propio `From`).
- **Interacciones** en `section.config.relationships`: `{source, target, type}`; `type 3` = sin interacción [probado al convertir a PBIR];
  `type 1` aparece entre slicers y tarjetas (por validar su significado exacto).
