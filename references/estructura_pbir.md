# Formato PBIR: Report/definition/

Power BI Desktop (2026) convierte el reporte a PBIR al guardar. Todos los JSON en **UTF-8 sin BOM**. [probado]

```
Report/definition/
  version.json                      {"version": "2.0.0"}
  report.json                       themeCollection, objects, settings, resourcePackages, publicCustomVisuals, filterConfig?
  pages/pages.json                  {"pageOrder": [ids], "activePageName": id}
  pages/<id>/page.json              name, displayName, displayOption, width, height, objects, visualInteractions, filterConfig?, visibility?
  pages/<id>/visuals/<id>/visual.json
  bookmarks/…                       [por validar: el archivo de prueba no tenía]
  reportExtensions.json             medidas de reporte [por validar]
```
Las demás partes del .pbix (DataModel, DiagramLayout, Settings, DAXQueries, StaticResources, CustomVisuals) siguen igual.
`Report/Layout` desaparece. `SecurityBindings` reaparece al guardar.

## visual.json [probado]

```json
{ "$schema": ".../visualContainer/2.13.0/schema.json", "name": "<id>",
  "position": {"x":..,"y":..,"z":..,"height":..,"width":..,"tabOrder":..},
  "visual": { "visualType": "tableEx",
     "query": { "queryState": { "Values": { "projections": [
          {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "FactMovimientos"}}, "Property": "RV Ventas netas"}},
           "queryRef": "FactMovimientos.RV Ventas netas", "nativeQueryRef": "Ventas", "displayName": "Ventas", "active": true} ]}},
       "sortDefinition": {"sort": [{"field": {...}, "direction": "Descending"}], "isDefaultSort": true} },
     "objects": {...}, "visualContainerObjects": {...}, "drillFilterOtherVisuals": true },
  "filterConfig": {"filters": [...]}, "parentGroupName": "..." }
```

## Equivalencias con el Layout clásico [probado]

| Layout clásico | PBIR |
|---|---|
| `config` / `filters` como texto JSON (doble parseo) | JSON directo |
| `projections` + `prototypeQuery.Select` (con alias `From`) | `query.queryState[rol].projections[].field` con `SourceRef.Entity` (sin alias) |
| `Select.Name` / `NativeReferenceName` | `queryRef` / `nativeQueryRef` |
| `columnProperties[qr].displayName` | `projections[].displayName` |
| `prototypeQuery.OrderBy` (Direction 1/2) | `sortDefinition.sort` (`"Ascending"`/`"Descending"`) |
| `vcObjects` | `visualContainerObjects` |
| `objects` | `objects` (idéntico) |
| `section.config.relationships` type 3 | `page.visualInteractions` type `"NoFilter"` |
| `displayOption` 1 | `"FitToPage"` (también `"FitToWidth"`) |
| `config.visibility = 1` | `"visibility": "HiddenInViewMode"` [probado: así lo guarda Desktop] |
| `query`, `dataTransforms` (cachés) | no existen; a veces `projections[].format` |

Tema personalizado [probado]: `report.json.themeCollection.customTheme = {name, reportVersionAtImport, type: "RegisteredResources"}`
+ item `{name, path, type: "CustomTheme"}` en el paquete `RegisteredResources` + archivo en `Report/StaticResources/RegisteredResources/`.
Regla del CLI de Microsoft: `customTheme.name` lleva `.json`, es igual al `name`/`path` del item y al `"name"` dentro del JSON
del tema (si no, `PBIR_THEME_FILE_NAME_MISMATCH`). Con nombres distintos el tema igual se aplicó en el Desktop [probado], pero
`tema_powerbi.aplicar_tema_pbir` y `Pbix.tema_personalizado` ya los igualan (archivo = `name` sin espacios ni acentos).

Prueba de regresión: un mismo reporte leído en Layout y en PBIR da las mismas referencias, campos y estados de slicer por página.

## Al escribir PBIR [probado]

- Cada `SourceRef` de los campos (proyecciones y orden) debe llevar `Entity`; un `Source` (alias) hace que el archivo no abra y
  Power BI solo muestra un identificador de actividad.
- Los filtros guardados de slicers (`objects.general.properties.filter.filter`) sí conservan `From` + `Source`: son una consulta.
- Desktop acepta valores con decimales en `position` y literales `0D` o `0.0D`.
- Enums numéricos (`labelDisplayUnits`, `orientation`…) como entero con `D` (`dint(1)` → `1D`), como los escribe el Desktop;
  `1.0D` funciona en pantalla pero el CLI lo marca como enum inválido [probado]. Propiedades `integer` con `L` (`lit(8)` → `8L`).
- `$schema` de visual.json: el Desktop 2026.09 escribe `visualContainer/2.13.0` [probado], que aún no está publicado
  (404; el espejo llega a 2.12.0): el aviso `PBIR_SCHEMA_UNREACHABLE` es esperado.

## Validar con el CLI de Microsoft [probado]

`npm install -g @microsoft/powerbi-report-authoring-cli` (Node ≥ 20) → binario `powerbi-report-author`, salida JSON.
`validate` solo acepta un PBIP (`.pbip`, carpeta `X.Report` o carpeta con `definition/`). **Truco**: extraer del .pbix
`Report/definition/` y `Report/StaticResources/` a `X.Report/` y agregar dos archivos mínimos:
```
X.Report/definition.pbir  {"$schema": ".../definitionProperties/2.0.0/schema.json", "version": "4.0",
                           "datasetReference": {"byPath": {"path": "../X.SemanticModel"}}}
X.Report/.platform        {"$schema": ".../platformProperties/2.0.0/schema.json", "metadata": {"type": "Report", "displayName": "X"},
                           "config": {"version": "2.0", "logicalId": "<uuid>"}}
```
Da **los mismos diagnósticos** que guardar como .pbip desde el Desktop (117 de 118 JSON iguales en contenido [probado]). `verificar_pbix.py --cli` lo hace en una carpeta temporal. Sin `.platform`: error `PBIR_PLATFORM_MISSING`.
Lo que el CLI marca y en pantalla resultó inofensivo [probado: capturas]: nombre del tema ≠ archivo, `1.0D` en enums, piso de
altura de textbox (`max(18, ceil(pt·25/16)) + padding 8+8`). Lo que sí importa: propiedades u objetos inexistentes (el Desktop
los ignora o los borra al guardar) y enums con valores fuera de la lista.
Validación sin Node: `scripts/catalogo.py validar` (mismo catálogo, también para Layout clásico).

## Por validar

- Filtros en PBIR (`filterConfig`): se espera la clave `field` en lugar de `expression`; el lector acepta ambas.
- Grupos de visuales (`visualGroup` en lugar de `visual`), marcadores, medidas de reporte, PBIR creado desde cero (no convertido).
