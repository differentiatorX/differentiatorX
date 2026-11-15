// Render animation frames: node frames.mjs <url> <outdir> <n> [w h]
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os'; import { join } from 'node:path';
const [url, out, nStr, w = '1280', h = '680', dpr = '1.25'] = process.argv.slice(2); const N = +nStr; mkdirSync(out, { recursive: true });
const port = 9800 + Math.floor(Math.random() * 100);
const chrome = spawn('C:/Program Files/Google/Chrome/Application/chrome.exe', ['--headless=new', `--remote-debugging-port=${port}`, '--allow-file-access-from-files', `--user-data-dir=${mkdtempSync(join(tmpdir(), 'fr-'))}`, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let t; for (let i = 0; i < 60 && !t; i++) { try { t = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((x) => x.type === 'page'); } catch { await sleep(200); } }
const ws = new WebSocket(t.webSocketDebuggerUrl); await new Promise((r) => ws.addEventListener('open', r));
let id = 0; const wait = new Map();
ws.addEventListener('message', (e) => { const m = JSON.parse(e.data); if (m.method === 'Runtime.exceptionThrown') console.log('PAGE ERROR', m.params.exceptionDetails.exception?.description); if (wait.has(m.id)) { wait.get(m.id)(m.result || m.error); wait.delete(m.id); } });
const send = (method, params = {}) => new Promise((r) => { wait.set(++id, r); ws.send(JSON.stringify({ id, method, params })); });
await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: +w, height: +h, deviceScaleFactor: +dpr, mobile: false });
await send('Page.enable'); await send('Page.navigate', { url }); await sleep(2500); await send('Runtime.evaluate', { expression: 'document.fonts.ready.then(()=>1)', awaitPromise: true });
for (let i = 0; i < N; i++) {
  const r = await send('Runtime.evaluate', { expression: `window.renderFrame(${i / N})`, returnByValue: true });
  const shot = await send('Page.captureScreenshot', { format: 'png' }); const data = shot.data; writeFileSync(join(out, `f${String(i).padStart(3, '0')}.png`), Buffer.from(data, 'base64'));
  if (i % 10 === 0) console.log('frame', i);
}
chrome.kill(); process.exit(0);
