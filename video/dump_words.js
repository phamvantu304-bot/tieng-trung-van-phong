// Lấy "Từ mới" của từng câu hội thoại từ app (cùng cách app hiển thị) -> video/words.json
// Cần chạy web server ở thư mục gốc repo: python3 -m http.server 8765
// Chạy: node video/dump_words.js   rồi python3 video/make_video.py
const path = require("path");
let pw;
try { pw = require("playwright"); } catch (e) { pw = require("/opt/node22/lib/node_modules/playwright"); }
const { chromium } = pw;
(async () => {
  const fs = require('fs');
  const b = await chromium.launch(fs.existsSync('/opt/pw-browsers/chromium') ? { executablePath: '/opt/pw-browsers/chromium' } : {});
  const p = await b.newPage();
  const errs=[]; p.on('pageerror', e => errs.push(e.message));
  await p.goto('http://localhost:8765/index.html');
  await p.waitForFunction(() => Object.keys(DLG).length > 0);
  const out = await p.evaluate(() => { const o = {}; for (const n in DLG) o[n] = DLG[n].lines.map(L => wordsIn(L.zh, n).map(w => [w[0], w[1], w[2]])); return o; });
  require('fs').writeFileSync(path.join(__dirname, 'words.json'), JSON.stringify(out, null, 0));
  await b.close();
})();
