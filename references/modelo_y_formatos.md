# Modelo semántico: DataModel, pbixray y SQLite

## Qué hay en el DataModel [probado]

Backup ABF comprimido con XPress9 (entropía ≈ 8 bits/byte: nada legible sin descomprimir). Dentro: `metadata.sqlitedb`
(todos los metadatos: tablas, columnas, medidas, relaciones, particiones con el M, roles, formatos, anotaciones) y los datos
VertiPaq (no se leen).

**Código M:** en .pbix modernos no existe la parte `DataMashup`; el M completo sale de `pbixray.power_query`
(`Partition.QueryDefinition`). La hipótesis "DataMashup = binario + ZIP con `Formulas/Section1.m`" aplica a archivos que traigan
esa parte [por validar: no hubo archivo de prueba]. `m_parameters` devuelve expresiones compartidas no cargadas
(p. ej. consultas "Errors in …"), no solo parámetros.

## pbixray 0.15.5 [probado]

Públicos: `tables`, `metadata`, `schema` (tipos pandas), `dax_measures` (sin formato), `dax_columns`, `dax_tables`,
`relationships` (cardinalidad, dirección, activa), `power_query`, `m_parameters`, `rls`, `statistics` (cardinalidad, tamaño),
`size`, más `tmschema_*` (p. ej. `tmschema_columns` trae FormatString/IsHidden/SummarizeBy pero no SortByColumn).
**Interno:** `PBIXRay._metadata._meta._db.conn` es una conexión `apsw` en memoria a `metadata.sqlitedb`; `leer_modelo.py` la usa
para lo que la API no expone (formato de medidas, ordenar por, lineageTag, variaciones, anotaciones). Si una versión futura la mueve,
inspecciona `vars()` del objeto (el árbol de atributos) y busca un `apsw.Connection`.

## Leer el modelo por TMDL (sin pbixray) [probado: nube 2026.09 y RS 2026.05]
- Fuente: pestaña de la vista TMDL con el modelo completo (el usuario arrastra «Modelo semántico» del panel Datos → Modelo y
  guarda; queda en `TMDLScripts/<pestaña>.tmdl`, UTF-16) o la carpeta `<x>.SemanticModel/definition/` de un .pbip.
- `leer_modelo_tmdl.py` toma la pestaña más grande que declare `model` y `table`; ignora scripts parciales (`ref table`).
- Lo que TMDL no trae: tipo de dato de las medidas (se infiere si devuelve texto), estadísticas y tamaños (solo pbixray),
  IDs internos. Trae columnas de las tablas de fecha automáticas (`tabla_automatica = true`), que pbixray filtra.
- Es una foto del momento en que se arrastró: si el reporte usa algo que no está, el cruce lo marca como referencia rota.

## Tablas SQLite útiles

`[Table]` (SystemFlags = 0 → tablas de usuario; las `LocalDateTable_*` y `DateTableTemplate_*` son de fecha automática),
`[Column]` (ExplicitName, ExplicitDataType, FormatString, IsHidden, SummarizeBy, SortByColumnID, Type, SourceColumn, Expression,
LineageTag), `[Measure]` (Name, Expression, FormatString, DisplayFolder, LineageTag), `[Relationship]` (Name = GUID),
`[Variation]` (ColumnID, RelationshipID, DefaultHierarchyID, IsDefault), `[Hierarchy]`, `[Annotation]` (ObjectType 4 columna,
8 medida). Consulta columnas opcionales con `PRAGMA table_info` antes de usarlas.

Códigos TOM: DataType 2 String, 6 Int64, 8 Double, 9 DateTime, 10 Decimal, 11 Boolean · SummarizeBy 1 Default, 2 None, 3 Sum,
4 Min, 5 Max, 6 Count, 7 Average, 8 DistinctCount · Column.Type 1 Data, 2 Calculated, 3 RowNumber (interna), 4 CalculatedTableColumn.

## Formatos [probado]

- Ejemplos reales: `Short Date`, `Long Date`, `yyyy-mm`, `mmm yy`, `0`, `0.00`, `#,0`, `0.0 %` (escapado `0.0\ %;-0.0\ %;0.0\ %`),
  moneda `\$#,0;(\$#,0);\$#,0`, moneda general `\$#,0.###############;…`.
- Una columna de fecha con formato personalizado lleva la anotación `PBI_FormatHint = {"isDateTimeCustom":true}`.
- Medidas creadas con la vista de consultas DAX: sin formato (las enteras reciben `0`).
- El caché del reporte (`dataTransforms.selects[].format`, `projections[].format`) solo trae algunos formatos: no lo uses como fuente.

## Locale: formatString vs FORMAT() [probado]

- Los visuales con medidas/columnas **numéricas** aplican el `formatString` con la **configuración regional del usuario**
  (`$1,234`); las medidas de **texto** con `FORMAT(valor, "$#,##0")` usan la **cultura del modelo** (`$1.234`, `$8,50`).
  En un mismo reporte conviven ambos estilos. Regla: **toda cifra visible va nativa** (medida numérica con formatString en
  tarjeta, tabla o eje), que es lo único que sigue al lector. El texto que no puede ser nativo usa la cultura del modelo
  (`FORMAT` sin tercer argumento); `USERCULTURE()` no coincide con los formatString en RS (ver `report_server.md`) y un locale
  fijo (`"en-US"`) va solo si el usuario lo pide.
  En SVG, la geometría (coordenadas, anchos) va siempre con `"en-US"` (punto decimal); solo el texto visible usa la cultura. Tercer argumento: funciona en el Desktop para RS 2026.05 y en el de la nube [probado: medidas SVG incrustadas con `FORMAT(…, "en-US")` creadas y evaluadas].
- Los nombres de mes salen de una columna de texto del modelo (`DimFecha[NombreMes]`) o del formato `mmm yy` de una columna de
  fecha (cultura del modelo: "dic 25"), no de `FORMAT(…, "en-US")` (daría "Dec").
- Una columna que llega como **texto** desde Power Query (tipo no asignado en "Tipo cambiado") sale cruda (`8589.0815`) y
  ningún formatString la arregla: tipa la columna en Power Query con cultura explícita
  (`Table.TransformColumnTypes(…, {{"Col", type number}}, "en-US")`) [probado: columnas de saldo y costo
  que llegaban como String]. `leer_modelo.py` muestra `tipo_dato` por columna: revísalo antes de diseñar.
  `cruzar_reporte_modelo.py` lo marca como hallazgo `numero_como_texto` (columna String en un rol de valores con agregación
  Sum/Avg/Median o nombre numérico: saldo, costo, valor, precio, cantidad…) [probado: sin falsos positivos en un modelo de 512 columnas].
  Sin acceso al origen para actualizar Power Query, sugerencia **[por validar, sin probar]**: columna calculada que parsee el
  texto sin depender de la cultura del modelo (no `VALUE(texto)` directo: en un modelo en español "8589.0815" se leería como
  85 millones): separar signo, parte entera y fracción y aplicar `VALUE` solo a dígitos; antes, contar con una consulta DAX
  agregada (nunca filas) cuántos valores traen coma, "E" o más de un separador.
- En el **portal de Report Server** el formatString usa la configuración regional del navegador del lector (con navegador en
  español: «$152.430»), aunque el Desktop mostrara «$152,430» [probado]; `FORMAT(…, "en-US")` no cambia.
- Montos `\$#,0.00` (o `\$#,0` en tarjetas/resúmenes), unidades `#,0`, porcentajes `0.0%`, fechas `dd/mm/yyyy`, eje de mes `mmm yy`.

## Jerarquías automáticas de fecha [probado]

Cada columna de fecha con "fecha/hora automática" tiene una `variation` hacia su `LocalDateTable_<guid>` (relación con nombre GUID y
jerarquía `'Date Hierarchy'` o `'Jerarquía de fechas'` según el idioma). La tabla local tiene `ShowAsVariationsOnly = 1`: si la
variación desaparece, el modelo es inválido.
