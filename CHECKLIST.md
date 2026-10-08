# Checklist

## A. Antes de empezar
- [ ] El usuario confirmó que se puede procesar el archivo (información de la empresa).
- [ ] Plataforma detectada (`plataforma.py`): Report Server o servicio, release, formato. Destino claro.
- [ ] Modelo leído (`leer_modelo.py`): pbixray, o TMDL arrastrado y guardado en el archivo (foto reciente del modelo).
- [ ] Trabajo sobre una **copia**; nunca el original. Un solo archivo de trabajo para cambios de modelo.

## B. Brief (diseño o cambios visibles) — una sola ronda, con opción recomendada
- [ ] Alcance: solo apariencia / rediseño / desde cero.
- [ ] Tipo de reporte y público (nunca asumidos).
- [ ] Decisión que apoya y cifra que debe quedar clara en 5 s.
- [ ] Medio (comité, escritorio, mural, PDF, móvil) · comparación y polaridad/meta de cada KPI · navegación.
- [ ] **Nivel de impacto** (sobrio / realzado / impactante) preguntado siempre, con el sugerido por público (guía §12).
- [ ] Estilo: a la medida (recomendado en rediseño y desde cero) o dirección fija · formato regional: por defecto el del
      lector = cifras nativas (formatString); fijo solo si lo pide, avisando que ejes y tablas seguirán el navegador.
- [ ] Recursos de marca solo si la persona los quiere agregar (logo, colores, fotos).
- [ ] Lo no respondido quedó como **supuesto** en la ficha.
- [ ] Leí `references/lecciones.md`.

## C. Diseño HTML (rediseño / desde cero)
- [ ] Idea propia (guía §2b): carácter en 3 adjetivos, 2–4 referencias de inspiración (o catálogo sin web) con qué se toma y su
      traducción (`traductor_powerbi.md`); nada copiado de un diseño o marca ajena.
- [ ] Estilo a la medida generado (`estilo_a_medida.py` → OK) y activo con `PBIX_TOKENS_EXTRA`; o dirección fija justificada.
- [ ] Arquetipo elegido por la premisa (`arquetipos.md`); variantes con arquetipos distintos.
- [ ] `registro_disenos.py comparar` sin REPITE frente a otros reportes (PARECIDO justificado en la ficha).
- [ ] Visuales de AppSource solo certificados, sin licencia y sin Internet (`appsource.md`); probados en la plataforma o dicho.
- [ ] Premisa causal escrita; 2–3 variantes distintas de verdad (héroe, rejilla y ruta propios).
- [ ] `node scripts/revisar_html.js` = 0 errores; ganadora elegida con la rúbrica.
- [ ] Ficha de decisiones y pie de confianza (fuente · actualizado · definiciones).
- [ ] Nombres reales de medidas y campos; cifras ficticias.
- [ ] Impactante: al menos una variante innovadora; diseño en 2 capas; `capas_html.js` → fondo < 3 MB y cajas; contraste
      medido sobre la imagen (puerta). Las luces no van detrás de texto pequeño.

## D. Antes de entregar el .pbix
- [ ] `verificar_pbix.py nuevo.pbix base.pbix modelo.json [--destino]` sin errores (estructura, campos, catálogo, plataforma).
- [ ] Report Server: clásico, `Metadata`/`Version` del original, sin visuales no soportados en el release.
- [ ] Medidas/formatos nuevos incrustados (`scripts_modelo`) y una pestaña DAX de comprobación.
- [ ] 2 capas: fondo puesto (`fondo_pagina.py`), visuales en las cajas de `_visuales.json` (±8 px) y transparentes; avisé que
      mover un visual obliga a regenerar el fondo.
- [ ] Medidas SVG con `dataCategory: ImageUrl` en el script TMDL; tamaño de imagen del visual = tamaño del SVG; generadas con la
      MISMA dirección que el tema; en cardVisual van como imagen (`cardImage.imageUrl`), nunca en `card` clásica ni como valor.
- [ ] Deneb: plantilla de la misma dirección, campos renombrados como pide, fondo del visual apagado en 2 capas.
- [ ] Textos con altura suficiente (sin barra de scroll). Cifras visibles NATIVAS (formatString); SVG solo forma (`cifras=False`);
      texto que no puede ser nativo con la cultura del modelo. Solo técnicas [probado] salvo pedido explícito.
- [ ] Tablas con `LienzoV2.tabla_top` (o top N) y `orden_lectura()` al cerrar cada página.
- [ ] Variaciones (Δ) comprobadas con una consulta DAX por fila/categoría antes de la captura: si |Δ| > 200 % en la mayoría de
      filas, la medida compara cosas distintas (guía §8). El texto del visual dice qué compara («vs mes anterior»).
- [ ] Tarjetas y ejes con unidades «ninguna» + formato (`$#,0`); «auto» sale en el idioma del Desktop («$152 mil»).
- [ ] Tablas sin barra de desplazamiento: Top N (o medidas en blanco fuera del top), ajuste de texto apagado, anchos que caben.
- [ ] Auditoría `guia_diseno.md` §10: crítico → refinamiento → pulido. La parte [P] la da `python scripts/auditoria.py nuevo.pbix
      --direccion=<dir>` (también resumida en `verificar_pbix.py`); la [C], sobre la captura.
- [ ] Entrega por niveles: HTML diseñado / replicado en .pbix / verificado con captura. Lo [por validar] dicho explícitamente.
- [ ] Diseño entregado registrado: `registro_disenos.py agregar --ficha …` (registro del proyecto).

## E. Si cambiaste scripts de la skill
- [ ] Regresión de `leer_reporte.py` con los archivos de referencia (cifras de control en `SKILL.md`).
- [ ] Docs y `CHANGELOG.md` actualizados.
