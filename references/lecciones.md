# Errores frecuentes y la regla que los evita (leer en el paso de brief)

| Síntoma | Causa | Regla |
|---|---|---|
| Rediseño que se ve «anticuado», con colores poco convincentes y mala disposición | no se preguntó el tipo de reporte; banda oscura + dorado; 4 tarjetas iguales | alcance y tipo siempre preguntados; dirección por tipo; héroe + tira; `corporativo` no por defecto |
| El usuario tiene que pegar y correr el DAX a mano | scripts entregados sueltos | `scripts_modelo.incrustar`: pestaña TMDL «Aplicar» dentro del .pbix |
| Números en dos estilos ($1.234 y $1,234), o distintos entre el Desktop y el portal de RS | `FORMAT()` usa la cultura del modelo; los formatString siguen la configuración regional del lector (Windows o navegador); `USERCULTURE()` no coincide con ninguno en RS | **cifras nativas** (medida numérica con formatString) siempre; SVG solo forma (`cifras=False`); texto con la cultura del modelo; locale fijo solo si se pide |
| «Cuadritos» de scroll en tarjetas y textos | padding global del tema y alturas justas | sin padding en `*`; `alto_min`; `revisar_html.js` |
| Archivo de la nube no publicable en Report Server | se guardó con el Desktop de la nube | `plataforma.py`; RS siempre clásico y Desktop para RS |
| Columnas numéricas que no aceptan formato | tipadas como texto en Power Query | hallazgo `numero_como_texto` en el cruce |
| Boceto HTML más «bonito» que el resultado en Power BI | letter-spacing, line-height, fuente distinta de Segoe UI | HTML solo con lo replicable; revisar con Segoe UI |
| Todos los dashboards de un tipo salen iguales y poco llamativos | una sola referencia por tipo y solo efectos nativos | niveles de impacto preguntados siempre; 2 capas con imagen de fondo; variante innovadora obligatoria en impactante |
| Texto ilegible sobre luces y vidrio | el contraste se mide contra el color CSS, no contra la imagen | `revisar_html.js` mide sobre los píxeles de la imagen de fondo; luces lejos de texto pequeño |
