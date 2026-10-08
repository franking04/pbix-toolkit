# Reconocimientos

**pbix-toolkit** es obra de **Francisco J. Chacón R.** Se apoya en el trabajo de otras personas y proyectos, que se reconocen aquí.
Los textos de la skill son redacción propia: de las fuentes se tomaron ideas, reglas o datos técnicos, no se copió su contenido.

## Software y formatos en los que se apoya
| Proyecto | Autor | Para qué se usa |
|---|---|---|
| [pbixray](https://github.com/Hugoberry/pbixray) | Hugoberry | lectura del modelo (DataModel con XPress9) cuando está instalado (`leer_modelo.py`) |
| [Power BI Report Authoring CLI](https://github.com/microsoft/powerbi-report-authoring) (`@microsoft/powerbi-report-authoring-cli` 0.5.0) y `@microsoft/powerbi-core-visual-schema` 0.1.1 | Microsoft | catálogo de visuales, roles, objetos y propiedades (`references/catalogo/`) y validación opcional |
| Esquemas JSON de PBIR y documentación de TMDL, PBIR, Power BI Desktop y Report Server | Microsoft | estructura del reporte y del modelo |
| [Deneb](https://deneb-viz.github.io/) | Daniel Marsh-Patrick | visual certificado en el que corren las plantillas de `scripts/deneb.py` |
| [Vega-Lite](https://vega.github.io/vega-lite/) | proyecto Vega (UW Interactive Data Lab) | gramática de las plantillas Deneb |
| HTML Content (visual de AppSource) | Daniel Marsh-Patrick | mencionado como opción para texto enriquecido |
| [Playwright](https://playwright.dev/) | Microsoft | puertas de revisión y capturas de los diseños HTML |

## Diseño, color y accesibilidad
| Fuente | Qué se tomó |
|---|---|
| Skills de diseño de bencium.io (`bencium-controlled-ux-designer`, `bencium-impact-designer`, `bencium-innovative-ux-designer`, `design-audit`, `typography`, `relationship-design`) | reglas de diseño adaptadas a Power BI en `references/guia_diseno.md` (filtradas y reescritas) |
| Skill `dataviz` de Anthropic | método y umbrales de validación de paletas (banda de luminosidad, croma mínimo, separación con daltonismo) usados en `scripts/estilo_a_medida.py` |
| OKLab / OKLCH, de Björn Ottosson (2020) | espacio de color para generar y comparar colores |
| Machado, Oliveira y Fernandes (2009), *A Physiologically-based Model for Simulation of Color Vision Deficiency* | simulación de protanopia, deuteranopia y tritanopia |
| WCAG 2.x (W3C) | fórmula y mínimos de contraste (4.5:1 texto, 3:1 marcas) |

## Referencias e inspiración consultadas
- Microsoft Learn: [visuales personalizados](https://learn.microsoft.com/power-bi/developer/visuals/power-bi-custom-visuals),
  [visuales certificados](https://learn.microsoft.com/en-us/power-bi/developer/visuals/power-bi-custom-visuals-certified) y
  [visuales organizacionales](https://learn.microsoft.com/en-us/power-bi/developer/visuals/power-bi-custom-visuals-organization).
- Comunidad de Microsoft Fabric: hilos sobre visuales personalizados en Report Server
  ([1](https://community.fabric.microsoft.com/t5/Report-Server/Custom-Visuals-not-working/m-p/415271),
  [2](https://community.fabric.microsoft.com/t5/Report-Server/Custom-Visuals-that-Work-in-Report-Server/m-p/559090)) y la
  [Data Stories Gallery](https://community.fabric.microsoft.com/t5/Power-BI-Updates-Blog/Share-inspiration-in-the-new-Data-Stories-Gallery-and-get-a-t/ba-p/5175167).
- [Deneb en AppSource](https://appsource.microsoft.com/en-us/product/PowerBIVisuals/coacervolimited1596856650797.deneb).
- [Dashboard-Design / Power-BI-Design-Files](https://github.com/Dashboard-Design/Power-BI-Design-Files) (GitHub).
- [Guía de ejemplos de dashboards de Power BI](https://www.thebricks.com/resources/guide-where-can-i-find-power-bi-dashboard-examples) (The Bricks).
- [Visual Vocabulary](https://www.theinformationlab.co.uk/community/blog/visual-vocabulary) del Financial Times, vía The Information Lab.
- [Lo que los diseñadores de tableros pueden aprender de los premios IIB](https://nightingaledvs.com/business-dashboard-designers-learn-from-iib/) (Nightingale, Data Visualization Society).
- [Visualizaciones más favoritas de Tableau Public](https://www.tableau.com/blog/most-favorited-data-visualizations-tableau-public) (Tableau).

## Contenido de terceros
`references/catalogo/` se generó a partir de las definiciones que publica Microsoft en su CLI; esas definiciones son de Microsoft
y se rigen por su licencia. Los nombres Power BI, AppSource y Report Server son marcas de Microsoft. Este proyecto no está
afiliado a Microsoft ni a los demás autores citados.

## Herramientas de desarrollo
Construida con la ayuda de Claude (Anthropic), con pruebas en Power BI Desktop y Power BI Report Server.
