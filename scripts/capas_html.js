// Separa un diseño HTML de 2 capas en lo que va a Power BI:
//   <base>_fondo.png      capa de decoración (degradados, brillos, paneles vidrio, sombras, cajas de los visuales)
//                         → imagen de fondo de la página (fondo_pagina.py). 1920x1080 por defecto (16:9).
//   <base>_visuales.json  caja de cada elemento data-pbi en coordenadas del lienzo 1280x720 (= coordenadas de Power BI)
//                         → posición exacta de cada visual nativo (transparente) encima del fondo.
//   <base>_compuesto.png  cómo debe verse el resultado (fondo + datos), para comparar con la captura de Power BI.
// Convenciones del HTML (ver references/guia_diseno.md §11):
//   * [data-capa="fondo"]  decoración pura (manchas de luz, formas, líneas): va entera a la imagen.
//   * [data-pbi]           su caja (fondo, borde, radio, sombra, desenfoque) va a la imagen; su contenido (texto, SVG) NO:
//                          lo dibuja el visual nativo, con fondo transparente.
//   * [data-caja="nativa"] el visual pone su propia caja (p. ej. cardVisual con glow): no se pinta nada en la imagen.
// Uso: node capas_html.js diseno.html [carpeta_salida] [--escala 1.5]   (NODE_PATH=$(npm root -g) si playwright es global)
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
// Navegador: el de playwright si está descargado; si no, Microsoft Edge instalado (Windows) [probado]
const lanzar = async () => { try { return await chromium.launch(); } catch (e) { return await chromium.launch({ channel: 'msedge' }); } };
const aURL = f => require('url').pathToFileURL(require('path').resolve(f)).href;   // file:// válido también en Windows
const OCULTAR = `.canvas [data-pbi] *{visibility:hidden!important}
.canvas [data-pbi]{color:transparent!important}
.canvas [data-pbi]::before,.canvas [data-pbi]::after{visibility:hidden!important}
.canvas [data-caja="nativa"]{visibility:hidden!important}
.toggle,.ficha{display:none!important}`;
const LIMITE = 3 * 1024 * 1024;
(async () => {
  const args = process.argv.slice(2); const iE = args.indexOf('--escala');
  let escala = iE >= 0 ? parseFloat(args.splice(iE, 2)[1]) : 1.5;
  const [archivo, salida = path.dirname(path.resolve(archivo))] = args;
  const base = path.join(salida, path.basename(archivo, '.html'));
  const b = await lanzar();
  for (let intento = 0; intento < 3; intento++) {
    const p = await b.newPage({ viewport: { width: 1328, height: 900 }, deviceScaleFactor: escala });
    await p.goto(aURL(archivo)); await p.waitForTimeout(300);
    const cv = await p.$('.canvas');
    const cajas = await p.evaluate(() => {
      const R = document.querySelector('.canvas').getBoundingClientRect();
      return [...document.querySelectorAll('.canvas [data-pbi]')].map((e, i) => {
        const r = e.getBoundingClientRect();
        return { orden: i, visual: e.getAttribute('data-pbi'), id: e.id || null, caja: e.getAttribute('data-caja') || 'fondo',
                 x: Math.round(r.left - R.left), y: Math.round(r.top - R.top), w: Math.round(r.width), h: Math.round(r.height),
                 anidado: !!e.parentElement.closest('[data-pbi]'),
                 texto: (e.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 60) };
      });
    });
    await cv.screenshot({ path: base + '_compuesto.png' });
    await p.addStyleTag({ content: OCULTAR }); await p.waitForTimeout(100);
    const png = await cv.screenshot({ path: base + '_fondo.png' });
    await p.close();
    if (png.length <= LIMITE || escala <= 1) {
      fs.writeFileSync(base + '_visuales.json', JSON.stringify({ lienzo: [1280, 720], imagen: [Math.round(1280 * escala), Math.round(720 * escala)], cajas }, null, 1));
      console.log(`${base}_fondo.png ${Math.round(1280 * escala)}x${Math.round(720 * escala)} · ${(png.length / 1024).toFixed(0)} KB · ${cajas.length} cajas data-pbi`);
      if (png.length > LIMITE) console.log('  ERROR imagen > 3 MB aun a 1280x720: simplifica la decoración (menos ruido/texturas)');
      break;
    }
    escala = escala > 1.3 ? 1.3 : 1;   // 1920 → 1664 → 1280
  }
  await b.close();
})();
