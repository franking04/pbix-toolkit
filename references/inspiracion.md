# Inspiración externa → diseño propio en Power BI

Objetivo: que cada reporte tenga una idea visual propia (no «el estilo moderno otra vez»), tomada de fuera y traducida a lo que
Power BI y Report Server pueden hacer. Se toman **patrones**, nunca diseños: nada de copiar un tablero, un logo, una marca ajena
ni imágenes de terceros. La inspiración se cita en la ficha (fuente + qué se tomó).

## Cuándo
- Rediseño o desde cero en nivel **realzado** o **impactante**, o cuando el usuario pide «algo distinto».
- Cuando `registro_disenos.py comparar` dice que la propuesta se parece demasiado a diseños anteriores.
- No hace falta en nivel **sobrio** para operación diaria ni en «solo apariencia» con marca dada (ahí manda la marca).

## Proceso (cabe en la misma ronda; no agrega preguntas)
1. **Carácter en 3 adjetivos** a partir del público, el medio y la marca: p. ej. «preciso, sobrio, industrial» o «cálido, cercano,
   artesanal». Elige el carácter de `estilo_a_medida.py --caracteres` que más se acerque.
2. **Buscar 2–4 referencias** (WebSearch; si la red no deja, usa el catálogo sin web de abajo). Consultas útiles:
   `"<sector> dashboard design"`, `"<adjetivo> data visualization"`, `"<tema> infographic editorial"`, `"<objeto físico> design"`
   (p. ej. «tablero de aeropuerto», «etiqueta de vino»). Mezcla al menos dos familias de fuentes de la tabla.
3. **Extraer, por referencia**: qué se toma (composición, color, tipografía, tratamiento del dato, un detalle), qué no se toma
   (todo lo que Power BI no hace o lo que identifica a otro) y cómo se traduce (`traductor_powerbi.md`, con su estado en RS).
4. **Semillas de color**: 1–3 hex elegidos de la referencia (aproximados) o de la marca → `estilo_a_medida.py`. El script ajusta
   contraste, daltonismo y estados; si mueve un color, el original queda como `marca` para la decoración.
5. **Arquetipo** (`arquetipos.md`) distinto de los últimos del registro, salvo que la premisa pida el mismo.
6. **Ficha**: tabla «Inspiración» (fuente con enlace · qué se toma · traducción · RS) + los 3 adjetivos + carácter + semillas.
   Es el «mood board» del diseño: en texto y enlaces, sin pegar imágenes ajenas en el entregable.
7. Registrar el diseño entregado: `registro_disenos.py agregar`.

## Fuentes (por familia)
| Familia | Fuentes | Qué aportan | Cuidado |
|---|---|---|---|
| Power BI | Data Stories Gallery (comunidad Fabric), NovyPro, repositorio GitHub `Dashboard-Design/Power-BI-Design-Files`, galerías de visuales de AppSource | lo que ya se logró en Power BI; trucos de fondo y botones | muchos usan visuales con licencia o fondos con texto incrustado: no sirve en RS / no es accesible |
| Visualización editorial | FT Visual Vocabulary (elegir gráfico por relación), Nightingale (Data Visualization Society), premios Information is Beautiful, The Pudding, gráficos de agencias de noticias | titulares-conclusión, anotaciones, jerarquía, sobriedad | son piezas para leer una vez: simplificar para uso diario |
| Comunidad de visualización | Tableau Public (Viz of the Day, más favoritos), Makeover Monday | composiciones arriesgadas y paletas | no copiar diseños de autor; tomar un patrón |
| Interfaz de producto | sistemas de diseño públicos, galerías de tableros de producto | tarjetas, estados, navegación, espaciado | las capturas de galerías de diseño suelen ser irreales (datos perfectos, texto 6 pt) |
| Mundo físico | carteles, empaques, señalética, revistas, instrumentos, mapas de transporte | carácter, paleta y tipografía con personalidad | traducir el carácter, no la imagen |
| Marca del usuario | manual de marca, presentaciones, sitio web de la empresa (solo si el usuario lo aporta) | semillas de color, tipografía, tono | colores de marca rojos/verdes chocan con estados (`estilo_a_medida` avisa) |

## Catálogo sin web (ideas de partida)
Conceptos genéricos (no imitan a ninguna organización real). Cada uno = carácter + semillas sugeridas + arquetipo que le va.
| Idea | Rasgos que se toman | Carácter · modo | Semillas sugeridas | Arquetipo |
|---|---|---|---|---|
| Tablero de salidas de aeropuerto | filas densas, columnas fijas, estado en texto, fondo oscuro | tecnico · oscuro | #F2C230 (marca), #4FA3E0 | `excepciones`, `scorecard` |
| Instrumentos de cabina | una cifra por instrumento, anillos, luz tenue | premium · oscuro, 2 capas | #3FB6A8, #C9A227 (marca) | `bento`, `cifra_unica` |
| Plano técnico (blueprint) | retícula visible, líneas finas, cotas, monocromo azul | tecnico · claro | #1F4E8C | `small_multiples`, `detalle_tabla` |
| Diario financiero en papel | papel cálido, titular con serifa, gráficos sin cajas, notas al margen | calido · claro | #1F4E8C, #B4642D | `titular_grafico`, `puente` |
| Estado de cuenta privado | mucho aire, cifras finas, una línea de oro | premium · claro | #8C6D2C (marca), #23395B | `ab_espejo`, `heroe_tira` |
| Marcador deportivo | cifras enormes, dos bandos, diferencia al centro | energico · oscuro | #E4572E (marca), #2E86DE | `ab_espejo`, `cifra_unica` |
| Mapa de metro | líneas de colores categóricos, estaciones = etapas | neutro · claro | #0F62FE, #8A3FFC | `embudo_etapas` |
| Etiqueta nutricional | jerarquía tipográfica estricta, reglas gruesas y finas, blanco y negro | tecnico · claro | #111111 (marca), #3B3A9E | `scorecard` |
| Pronóstico del tiempo | iconos de estado, franja de días, rangos | sereno · claro | #3D9AB9, #5EC4B6 | `calendario` |
| Revista de diseño | bloques asimétricos, una foto/forma grande de color, mucho blanco | energico · claro | #6D28D9, #FF7A59 (marca) | `bento`, `portada_menu` |
| Sala de control | oscuro sereno, estados claros, nada decorativo | sereno · oscuro | #5AB2F0 | `excepciones`, `cifra_unica` |
| Cuaderno de campo | papel, tinta verde/sepia, anotaciones a mano (en tipografía normal) | calido · claro | #2E5E4E, #8C5A2B | `titular_grafico`, `narrativa_vertical` |

## Reglas
- Máximo 3 referencias por diseño; si no se puede explicar qué aporta cada una, sobra.
- Lo que no pase las puertas (`revisar_html.js`) o no tenga traducción probada en la plataforma del usuario no se usa, por bonito que sea.
- Si el usuario trae su propia referencia (captura, enlace), es la fuente principal: se analiza igual (qué se toma / qué no / traducción).
