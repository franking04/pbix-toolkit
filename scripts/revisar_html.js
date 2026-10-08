// Puertas objetivas para un diseño HTML de referencia antes de replicarlo en Power BI.
// Uso: node revisar_html.js archivo.html [más.html]   (necesita playwright; NODE_PATH=$(npm root -g) si es global)
// Sale con código 1 si hay errores. Avisos no bloquean.
// Diseños de 1 capa (sobrio, realzado): todo debe poder hacerse con visuales nativos (sin degradados CSS, filtros, etc.).
// Diseños de 2 capas (impactante; hay [data-capa="fondo"]): la decoración y las cajas de los data-pbi van a la imagen de
// fondo y pueden usar efectos; el CONTENIDO de los data-pbi no (salvo visuales Deneb/HTML/SVG, que sí dibujan degradados).
// En 2 capas el contraste del texto se mide contra los píxeles reales de la imagen de fondo (percentil 10 del peor caso).
const { chromium } = require('playwright');
// Navegador: el de playwright si está descargado; si no, Microsoft Edge instalado (Windows) [probado]
const lanzar = async () => { try { return await chromium.launch(); } catch (e) { return await chromium.launch({ channel: 'msedge' }); } };
const aURL = f => require('url').pathToFileURL(require('path').resolve(f)).href;   // file:// válido también en Windows
const FUENTES_PBI = ['segoe ui','segoe ui semibold','segoe ui light','segoe ui bold','arial','georgia','calibri','tahoma','verdana','consolas','din','times new roman','sans-serif','serif','monospace','constantia','corbel','candara','trebuchet ms'];
const OCULTAR = `.canvas [data-pbi] *{visibility:hidden!important}.canvas [data-pbi]{color:transparent!important}
.canvas [data-pbi]::before,.canvas [data-pbi]::after{visibility:hidden!important}.canvas [data-caja="nativa"]{visibility:hidden!important}`;
(async () => {
  const b = await lanzar(); let fallo = false;
  for (const f of process.argv.slice(2)) {
    const p = await b.newPage({ viewport: { width: 1328, height: 900 } });
    await p.goto(aURL(f)); await p.waitForTimeout(250);
    const dosCapas = await p.evaluate(() => !!document.querySelector('.canvas [data-capa="fondo"]'));
    let fondo = null;
    if (dosCapas) {   // imagen de la capa de decoración, para medir contraste sobre píxeles reales
      const st = await p.addStyleTag({ content: OCULTAR }); await p.waitForTimeout(80);
      fondo = (await (await p.$('.canvas')).screenshot()).toString('base64');
      await st.evaluate(n => n.remove()); await p.waitForTimeout(80);
    }
    const r = await p.evaluate(async ([FUENTES, dos, fondo]) => {
      const err = [], av = [];
      const cv = document.querySelector('.canvas'); const R = cv.getBoundingClientRect();
      if (Math.round(R.width) !== 1280 || Math.round(R.height) !== 720) err.push(`lienzo ${R.width}x${R.height} (debe ser 1280x720)`);
      const rgb = c => c.match(/[\d.]+/g).map(Number);
      const lumA = a => { const m = a.slice(0, 3).map(v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4) }); return .2126 * m[0] + .7152 * m[1] + .0722 * m[2] };
      const lum = c => lumA(rgb(c));
      const cx2 = document.createElement('canvas').getContext('2d');
      const norm = c => { cx2.fillStyle = '#000'; cx2.fillStyle = c; const s = cx2.fillStyle; if (s[0] === '#') return [1, 3, 5].map(i => parseInt(s.slice(i, i + 2), 16)).concat(1); const m = s.match(/[\d.]+/g).map(Number); return [m[0], m[1], m[2], m[3] ?? 1] };
      const capasBg = (el, hasta) => { const out = []; while (el && el !== hasta) { const c = norm(getComputedStyle(el).backgroundColor); if (c[3] > 0) { out.push(c); if (c[3] >= .999) break } el = el.parentElement } return out };
      const componer = (capas, base) => { for (let i = capas.length - 1; i >= 0; i--) { const [r, g, b, a] = capas[i]; base = [r * a + base[0] * (1 - a), g * a + base[1] * (1 - a), b * a + base[2] * (1 - a)] } return base };
      const bg = el => 'rgb(' + componer(capasBg(el, null), [255, 255, 255]).join(',') + ')';
      let px = null;
      if (fondo) {
        const img = new Image(); img.src = 'data:image/png;base64,' + fondo; await img.decode();
        const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
        const g = c.getContext('2d'); g.drawImage(img, 0, 0); px = g.getImageData(0, 0, c.width, c.height);
      }
      const contrasteImagen = (fg, rc) => {   // percentil 10 de contraste sobre los píxeles bajo la caja del texto
        const L = lumA(rgb(fg)), out = [];
        const x0 = Math.max(0, Math.floor(rc.left - R.left)), x1 = Math.min(px.width - 1, Math.ceil(rc.right - R.left));
        const y0 = Math.max(0, Math.floor(rc.top - R.top)), y1 = Math.min(px.height - 1, Math.ceil(rc.bottom - R.top));
        for (let y = y0; y <= y1; y += 2) for (let x = x0; x <= x1; x += 2) {
          const i = (y * px.width + x) * 4, l = lumA([px.data[i], px.data[i + 1], px.data[i + 2]]);
          out.push((Math.max(L, l) + .05) / (Math.min(L, l) + .05));
        }
        out.sort((a, b) => a - b); return out.length ? out[Math.floor(out.length * .1)] : 21;
      };
      const libre = el => { const d = el.closest('[data-pbi]'); return d && /deneb|html content|svg/i.test(d.getAttribute('data-pbi')) };
      const tam = new Set(); let n = 0;
      for (const el of cv.querySelectorAll('*')) {
        const cs = getComputedStyle(el), r = el.getBoundingClientRect();
        const enFondo = !!el.closest('[data-capa="fondo"]');
        if (enFondo) continue;                                   // decoración: va a la imagen tal cual
        if (el.closest('svg') && el.tagName !== 'text') continue;
        const esCaja = el.hasAttribute('data-pbi');              // en 2 capas su caja se pinta en la imagen
        if (r.width && (r.right > R.right + 1 || r.bottom > R.bottom + 1 || r.left < R.left - 1 || r.top < R.top - 1))
          err.push(`fuera del lienzo: <${el.tagName.toLowerCase()} class="${el.className.baseVal ?? el.className}">`);
        const efectosOk = (dos && esCaja) || libre(el);
        if (!efectosOk) {
          if (cs.backgroundImage !== 'none') err.push('degradado/imagen de fondo en ' + el.tagName + (dos ? ' (contenido de un visual: pásalo a la caja o a [data-capa=fondo])' : ' (en 1 capa no se replica; usa 2 capas)'));
          if ((cs.filter && cs.filter !== 'none') || (cs.backdropFilter && cs.backdropFilter !== 'none')) err.push('filter/backdrop-filter en ' + el.tagName);
        }
        if (!libre(el)) {
          if (cs.textShadow !== 'none') err.push('text-shadow en ' + el.tagName + ' (Power BI no lo tiene en texto)');
          if (cs.letterSpacing !== 'normal' && cs.letterSpacing !== '0px') err.push('letter-spacing (Power BI no lo replica) en ' + el.tagName);
        }
        if (cs.animationName !== 'none' || (cs.transitionDuration && cs.transitionDuration !== '0s')) err.push('animación/transición en ' + el.tagName);
        const fam = cs.fontFamily.split(',')[0].replace(/["']/g, '').trim().toLowerCase();
        if (!FUENTES.includes(fam)) err.push('fuente no disponible en Power BI: ' + fam);
        const propio = [...el.childNodes].some(x => x.nodeType === 3 && x.textContent.trim());
        if (propio || el.tagName === 'text') {
          n++;
          const fs = parseFloat(el.tagName === 'text' ? (el.getAttribute('font-size') || cs.fontSize) : cs.fontSize);
          tam.add(Math.round(fs * 0.75 * 2) / 2);
          if (fs < 11.9) err.push(`texto < 9 pt (${(fs * .75).toFixed(1)} pt): "${el.textContent.trim().slice(0, 30)}"`);
          // Desbordes con la fuente real (Segoe UI es más ancha que Inter/Arial)
          const txt = `"${el.textContent.trim().slice(0, 30)}"`;
          if (el.tagName === 'text') {
            const sv = el.ownerSVGElement && el.ownerSVGElement.getBoundingClientRect(), tr = el.getBoundingClientRect();
            if (sv && sv.width && (tr.right > sv.right + 1 || tr.left < sv.left - 1)) err.push('etiqueta SVG cortada por el borde del gráfico: ' + txt);
          } else {
            if (cs.overflow !== 'visible' && el.scrollWidth > el.clientWidth + 1) err.push('texto recortado (no cabe en su caja): ' + txt);
            const caja = el.closest('[data-pbi]');
            if (caja && caja !== el) { const rc = caja.getBoundingClientRect(); if (r.right > rc.right + 1 || r.bottom > rc.bottom + 1) err.push('texto se sale de su visual: ' + txt); }
            const lh = parseFloat(cs.lineHeight) || fs * 1.2;
            if (/pill|pildora|píldora|chip|badge|tag|etiq/i.test(el.className && (el.className.baseVal ?? el.className)) && r.height > lh * 1.6)
              err.push('píldora/etiqueta partida en 2 líneas: ' + txt);
          }
          const fg = el.tagName === 'text' ? (el.getAttribute('fill') || cs.fill) : cs.color;
          if (fg && fg.startsWith('rgb')) {
            const min = fs >= 24 || (fs >= 18.6 && +cs.fontWeight >= 600) ? 3 : 4.5;
            let c;
            const caja = el.closest('[data-pbi]'), propio = caja && !el.closest('[data-caja="nativa"]') ? capasBg(el, caja) : [];
            if (px && !el.closest('[data-caja="nativa"]') && !(propio.length && propio[0][3] >= .999)) c = contrasteImagen(fg, el.tagName === 'text' ? el.getBoundingClientRect() : r);
            else { const b1 = lum(fg), b2 = lum(bg(el.tagName === 'text' ? el.closest('div') : el)); c = (Math.max(b1, b2) + .05) / (Math.min(b1, b2) + .05) }
            if (c < min - 0.05) err.push(`contraste ${c.toFixed(2)} < ${min}: "${el.textContent.trim().slice(0, 30)}"`);
          }
        }
      }
      [...cv.children].filter(e => !e.hasAttribute('data-pbi') && !e.hasAttribute('data-capa') && !e.classList.contains('vr') && !e.classList.contains('hr'))
        .forEach(e => av.push('bloque sin data-pbi: ' + (e.textContent.trim().slice(0, 30) || e.className)));
      if (tam.size > 6) av.push(`demasiados tamaños de texto (${tam.size}): ${[...tam].sort((a, b) => a - b).join(', ')} pt`);
      const noEnteros = [...tam].filter(t => Math.abs(t - Math.round(t)) > .01); if (noEnteros.length) av.push('tamaños no enteros en pt: ' + noEnteros.join(', '));
      if (!cv.querySelector('.pie') || !/Actualizado/i.test(cv.querySelector('.pie').textContent)) err.push('falta pie de confianza (fuente + actualizado)');
      if (!document.querySelector('.ficha')) av.push('falta ficha de decisiones');
      const segoe = document.fonts.check('12px "Segoe UI"');
      if (!segoe) av.push('Segoe UI no está instalada en este equipo: los anchos de texto no son los de Power BI');
      return { err: [...new Set(err)], av: [...new Set(av)], textos: n, tamanos_pt: [...tam].sort((a, b) => a - b), segoe };
    }, [FUENTES_PBI, dosCapas, fondo]);
    console.log(`\n== ${f}: ${dosCapas ? '2 capas' : '1 capa'} · ${r.err.length} errores, ${r.av.length} avisos · tamaños ${r.tamanos_pt.join('/')} pt · Segoe UI ${r.segoe ? 'sí' : 'NO'}`);
    r.err.forEach(e => console.log('  ERROR ' + e)); r.av.forEach(e => console.log('  aviso ' + e));
    if (r.err.length) fallo = true; await p.close();
  }
  await b.close(); process.exit(fallo ? 1 : 0);
})();
