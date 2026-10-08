const { chromium } = require('playwright');
// Navegador: el de playwright si está descargado; si no, Microsoft Edge instalado (Windows) [probado]
const lanzar = async () => { try { return await chromium.launch(); } catch (e) { return await chromium.launch({ channel: 'msedge' }); } };
const aURL = f => require('url').pathToFileURL(require('path').resolve(f)).href;   // file:// válido también en Windows
(async()=>{const b=await lanzar();const p=await b.newPage({viewport:{width:1328,height:768}});
for(const f of process.argv.slice(2)){await p.goto(aURL(f));await p.waitForTimeout(300);
const c=await p.$('.canvas');await c.screenshot({path:f.replace('.html','.png')});
await p.evaluate(()=>document.body.classList.add('map'));await c.screenshot({path:f.replace('.html','_mapa.png')});await p.evaluate(()=>document.body.classList.remove('map'));}
await b.close()})();
