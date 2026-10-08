# Editar el modelo

El DataModel no se puede escribir desde fuera (XPress9, solo lectura). Toda edición del modelo la ejecuta el usuario dentro de
Power BI Desktop con un script que tú preparas.

## Vista de consultas DAX: crear o redefinir medidas [probado]

```
DEFINE
    MEASURE Tabla[Nombre] = <expresión>
    ...
EVALUATE ROW ( "ok", 1 )          // o consultas de prueba para comparar cifras
```
El usuario pulsa *Ejecutar* y luego *Actualizar modelo con cambios* (crea o sobrescribe). Las medidas quedan sin formato.
Las medidas pueden referirse a otras definidas en el mismo `DEFINE`. Incluye `EVALUATE` de prueba para comparar con lo esperado.

## Vista TMDL: cambiar propiedades (formatos, carpetas) [probado]

```
createOrReplace

	ref table FactMovimientos

		measure 'RV Margen bruto' = DIVIDE ( [RV Ventas netas] - [RV Costo ventas], [RV Ventas netas] )
			formatString: 0.0%
			lineageTag: 00000000-0000-0000-0000-000000000001
```
- Sangría con **tabulaciones**. Nombres con espacios entre comillas simples.
- `ref table` entra a la tabla sin reemplazarla; `createOrReplace` reemplaza **cada objeto escrito** completo.
- La aplicación es atómica: si algo falla, no se aplica nada.
- Error conocido: redefinir una columna de fecha sin su `variation` →
  `Table 'LocalDateTable_…' with ShowAsVariationsOnly property set to '1' must be a target of a variation…`.
  Solución probada: el usuario arrastra la columna al editor TMDL (Power BI genera la definición completa: `dataType`, `formatString`,
  `lineageTag`, `summarizeBy`, `sourceColumn`, `variation` con `relationship` y `defaultHierarchy`, anotaciones), se cambia solo la línea
  necesaria y se aplica. Ejemplo real en `ejemplos/columna_fecha_generada_por_powerbi.tmdl`.
- Medida reescrita sin `lineageTag` → recibe uno nuevo. `tmdl_medidas.py` copia el original [por validar que se conserve].
- Expresiones multilínea: una tabulación más que las propiedades [por validar].

## Después de aplicar

El usuario guarda (Ctrl+S); corre `leer_modelo.py` y compara contra la lectura anterior: mismas columnas y medidas, mismas
expresiones, y solo las propiedades pedidas cambiadas.
