// Vẽ ảnh nhân vật hoạt hình đơn giản (16:9) cho video hội thoại -> video/scenes/u{n}_{A|B}.png
// Mỗi ảnh là người đang nói, đặt trong bối cảnh hợp với bài (văn phòng, phòng họp, nhà máy, kho cảng).
// Chạy: node video/make_characters.js   (cần playwright + chromium), sau đó: python3 video/make_video.py
const path = require("path"), fs = require("fs");
let pw;
try { pw = require("playwright"); } catch (e) { pw = require("/opt/node22/lib/node_modules/playwright"); }

const ROOT = path.dirname(__dirname);
const OUT = path.join(__dirname, "scenes");
const W = 1280, H = 720;

// ngoại hình từng nhân vật
const SKIN = { a: "#F6D3B3", b: "#EFC6A0", c: "#E8B98F" };
const PEOPLE = {
  "Chị Vương":    { f: 1, hair: "bob", hc: "#1F1A17", skin: SKIN.a, coat: "#2E3E5C", shirt: "#F4F1EA", glasses: 1 },
  "Anh Minh":     { f: 0, hair: "short", hc: "#1C1A19", skin: SKIN.b, coat: "#8FB3D9", shirt: "#8FB3D9", open: 1 },
  "Chị Lý":       { f: 1, hair: "pony", hc: "#3A2618", skin: SKIN.a, coat: "#C9A57E", shirt: "#FFFFFF" },
  "Lâm":          { f: 1, hair: "long", hc: "#231B16", skin: SKIN.a, coat: "#F3EEE6", shirt: "#F3EEE6", open: 1 },
  "Anh Trần":     { f: 0, hair: "side", hc: "#2B2B2B", skin: SKIN.c, coat: "#5B6068", shirt: "#FFFFFF", tie: "#A33B32", glasses: 1 },
  "Anh Lý":       { f: 0, hair: "short", hc: "#151515", skin: SKIN.b, coat: "#22262E", shirt: "#FFFFFF", tie: "#3A5A9A" },
  "Chị Vương Lan":{ f: 1, hair: "long", hc: "#4A2E1F", skin: SKIN.a, coat: "#8C2F3C", shirt: "#F7EFE6" },
  "Anh Trương":   { f: 0, hair: "side", hc: "#1E1E1E", skin: SKIN.b, coat: "#283A57", shirt: "#E9EEF5", tie: "#7A7F88" },
  "Chị Thu":      { f: 1, hair: "bob", hc: "#3B2A20", skin: SKIN.a, coat: "#1F6F8B", shirt: "#FFFFFF" },
  "Anh Lưu":      { f: 0, hair: "short", hc: "#222222", skin: SKIN.b, coat: "#4A4F57", shirt: "#F2F2F2", open: 1 },
};
// bối cảnh theo unit
const PLACE = { 4: "meeting", 5: "meeting", 9: "factory", 10: "factory", 11: "factory", 13: "port", 14: "port", 18: "home", 20: "home" };

function background(kind) {
  const blur = `filter="url(#bl)"`;
  if (kind === "factory") return `<g ${blur}>
    <rect width="${W}" height="${H}" fill="url(#gFac)"/>
    ${[0, 1, 2, 3, 4, 5].map(i => `<rect x="${i * 230 - 20}" y="40" width="160" height="90" fill="#FFF3D6" opacity=".55"/>`).join("")}
    <rect x="40" y="300" width="300" height="200" rx="10" fill="#5D7A8C"/><rect x="70" y="330" width="120" height="60" fill="#9FC1D3"/>
    <circle cx="270" cy="360" r="28" fill="#E0B341"/><rect x="40" y="480" width="300" height="30" fill="#3D5160"/>
    <rect x="930" y="330" width="120" height="110" fill="#C49A63"/><rect x="1060" y="330" width="120" height="110" fill="#B88C55"/>
    <rect x="995" y="220" width="120" height="110" fill="#CFA56C"/>
    <rect x="0" y="520" width="${W}" height="20" fill="#E7C14A" opacity=".7"/></g>`;
  if (kind === "port") return `<g ${blur}>
    <rect width="${W}" height="${H}" fill="url(#gSky)"/>
    <rect x="0" y="380" width="${W}" height="340" fill="#6E7F8D"/>
    ${[["#C8553D", 40, 250], ["#2F6690", 250, 250], ["#E0A030", 40, 140], ["#3A7D44", 900, 250], ["#C8553D", 1110, 250], ["#2F6690", 1000, 140]]
      .map(([c, x, y]) => `<rect x="${x}" y="${y}" width="200" height="105" fill="${c}"/>${[1, 2, 3, 4, 5, 6, 7].map(k => `<rect x="${x + k * 25}" y="${y + 10}" width="6" height="85" fill="#000" opacity=".15"/>`).join("")}`).join("")}
    <path d="M520 380 L540 60 L560 60 L580 380 Z M540 80 L900 80 L900 95 L540 95 Z" fill="#E3B23C"/></g>`;
  if (kind === "home") return `<g ${blur}>
    <rect width="${W}" height="${H}" fill="#E9DCC8"/>
    <rect x="70" y="60" width="420" height="380" rx="6" fill="url(#gSky)"/>
    <path d="M70 440 L70 330 L150 330 L150 260 L230 260 L230 300 L320 300 L320 220 L400 220 L400 290 L490 290 L490 440 Z" fill="#9DB4C8" opacity=".75"/>
    <rect x="70" y="60" width="420" height="380" rx="6" fill="none" stroke="#FFFFFF" stroke-width="14"/>
    <path d="M40 50 Q90 250 60 470 L20 470 L20 50 Z M520 50 Q470 250 500 470 L540 470 L540 50 Z" fill="#C98E6B" opacity=".85"/>
    <rect x="860" y="380" width="380" height="120" rx="30" fill="#7D9A8C"/><rect x="880" y="330" width="340" height="80" rx="24" fill="#8FAE9F"/>
    <circle cx="1090" cy="150" r="70" fill="none" stroke="#B89B6E" stroke-width="10"/><circle cx="1090" cy="150" r="52" fill="#F4EDE0"/>
    <line x1="1090" y1="150" x2="1090" y2="112" stroke="#555" stroke-width="6"/><line x1="1090" y1="150" x2="1118" y2="160" stroke="#555" stroke-width="6"/>
    <rect x="800" y="210" width="10" height="190" fill="#8A6A4A"/><path d="M760 210 L850 210 L830 160 L780 160 Z" fill="#F7E3B5"/></g>`;
  const meeting = kind === "meeting";
  return `<g ${blur}>
    <rect width="${W}" height="${H}" fill="url(#gWall)"/>
    <rect x="60" y="70" width="380" height="330" rx="6" fill="url(#gSky)"/>
    <path d="M60 400 L60 300 L120 300 L120 250 L190 250 L190 320 L250 320 L250 210 L320 210 L320 290 L390 290 L390 260 L440 260 L440 400 Z" fill="#9DB4C8" opacity=".8"/>
    <rect x="60" y="70" width="380" height="330" rx="6" fill="none" stroke="#FFFFFF" stroke-width="14"/>
    <line x1="250" y1="70" x2="250" y2="400" stroke="#FFFFFF" stroke-width="10"/>
    ${meeting
      ? `<rect x="820" y="90" width="400" height="260" rx="8" fill="#FBFBF8" stroke="#C9C4BA" stroke-width="8"/>
         <rect x="860" y="140" width="200" height="14" rx="7" fill="#5C7FB8"/><rect x="860" y="180" width="300" height="10" rx="5" fill="#BBB"/>
         <rect x="860" y="210" width="260" height="10" rx="5" fill="#BBB"/><path d="M880 320 L940 270 L990 295 L1080 230 L1160 250" stroke="#D2633F" stroke-width="8" fill="none"/>`
      : `<rect x="880" y="120" width="320" height="18" fill="#9B7B5A"/><rect x="880" y="250" width="320" height="18" fill="#9B7B5A"/>
         ${[0, 1, 2, 3, 4, 5].map(i => `<rect x="${895 + i * 34}" y="${60 + (i % 2) * 8}" width="26" height="${60 - (i % 2) * 8}" fill="${["#B5523B", "#3E6E8E", "#D9A441", "#5E8C61", "#7A5C99", "#C27C4E"][i]}"/>`).join("")}
         ${[0, 1, 2, 3].map(i => `<rect x="${900 + i * 40}" y="${195 + (i % 2) * 6}" width="30" height="${55 - (i % 2) * 6}" fill="${["#3E6E8E", "#D9A441", "#B5523B", "#5E8C61"][i]}"/>`).join("")}
         <rect x="1110" y="400" width="70" height="90" rx="10" fill="#C77B4D"/>
         <ellipse cx="1125" cy="380" rx="40" ry="70" fill="#5E9C63"/><ellipse cx="1170" cy="370" rx="35" ry="80" fill="#4E8A55"/>`}
  </g>`;
}

function hairBack(p, cx, cy) {
  if (p.hair === "long") return `<path d="M${cx - 112} ${cy - 30} Q${cx - 130} ${cy + 150} ${cx - 120} ${cy + 230} L${cx + 120} ${cy + 230} Q${cx + 130} ${cy + 150} ${cx + 112} ${cy - 30} Z" fill="${p.hc}"/>`;
  if (p.hair === "bob") return `<path d="M${cx - 112} ${cy - 30} Q${cx - 122} ${cy + 70} ${cx - 104} ${cy + 92} L${cx + 104} ${cy + 92} Q${cx + 122} ${cy + 70} ${cx + 112} ${cy - 30} Z" fill="${p.hc}"/>`;
  if (p.hair === "pony") return `<ellipse cx="${cx + 105}" cy="${cy - 40}" rx="40" ry="62" fill="${p.hc}" transform="rotate(25 ${cx + 105} ${cy - 40})"/>`;
  return "";
}

function hairFront(p, cx, cy) {
  const t = cy - 112;
  if (p.hair === "short") return `<path d="M${cx - 100} ${cy - 5} Q${cx - 112} ${t - 10} ${cx} ${t - 18} Q${cx + 112} ${t - 10} ${cx + 100} ${cy - 5} Q${cx + 92} ${cy - 62} ${cx + 40} ${cy - 70} Q${cx - 20} ${cy - 58} ${cx - 60} ${cy - 72} Q${cx - 92} ${cy - 55} ${cx - 100} ${cy - 5} Z" fill="${p.hc}"/>`;
  if (p.hair === "side") return `<path d="M${cx - 100} ${cy} Q${cx - 115} ${t - 8} ${cx - 10} ${t - 16} Q${cx + 110} ${t - 12} ${cx + 100} ${cy - 2} Q${cx + 96} ${cy - 60} ${cx + 70} ${cy - 72} Q${cx - 10} ${cy - 66} ${cx - 40} ${t + 10} Q${cx - 80} ${cy - 50} ${cx - 100} ${cy} Z" fill="${p.hc}"/>`;
  // nữ: mái chia ngôi
  return `<path d="M${cx - 108} ${cy + 10} Q${cx - 118} ${t - 14} ${cx - 5} ${t - 18} Q${cx + 118} ${t - 14} ${cx + 108} ${cy + 10} Q${cx + 100} ${cy - 50} ${cx + 60} ${cy - 70} Q${cx + 20} ${cy - 80} ${cx + 5} ${t + 6} Q${cx - 30} ${cy - 60} ${cx - 90} ${cy - 50} Q${cx - 104} ${cy - 20} ${cx - 108} ${cy + 10} Z" fill="${p.hc}"/>`;
}

function person(p, cx, cy, talk) {
  const sh = 470; // vai
  const coat = p.coat, dark = "rgba(0,0,0,.18)";
  let body = `<path d="M${cx - 250} ${H} Q${cx - 240} ${sh + 20} ${cx - 130} ${sh - 10} L${cx + 130} ${sh - 10} Q${cx + 240} ${sh + 20} ${cx + 250} ${H} Z" fill="${coat}"/>`;
  if (p.open) // áo sơ mi / áo kiểu: cổ áo đơn giản
    body += `<path d="M${cx - 55} ${sh - 12} L${cx} ${sh + 45} L${cx + 55} ${sh - 12}" fill="none" stroke="${dark}" stroke-width="8"/>`;
  else body += `<path d="M${cx - 60} ${sh - 12} L${cx} ${sh + 110} L${cx + 60} ${sh - 12} Z" fill="${p.shirt}"/>
     <path d="M${cx - 60} ${sh - 12} L${cx - 8} ${sh + 120} L${cx - 70} ${sh + 60} L${cx - 95} ${sh} Z" fill="${dark}"/>
     <path d="M${cx + 60} ${sh - 12} L${cx + 8} ${sh + 120} L${cx + 70} ${sh + 60} L${cx + 95} ${sh} Z" fill="${dark}"/>`;
  if (p.tie) body += `<path d="M${cx - 13} ${sh - 4} L${cx + 13} ${sh - 4} L${cx + 8} ${sh + 12} L${cx + 18} ${sh + 95} L${cx} ${sh + 112} L${cx - 18} ${sh + 95} L${cx - 8} ${sh + 12} Z" fill="${p.tie}"/>`;
  const neck = `<path d="M${cx - 36} ${cy + 80} L${cx - 38} ${sh} Q${cx} ${sh + 24} ${cx + 38} ${sh} L${cx + 36} ${cy + 80} Z" fill="${p.skin}"/><path d="M${cx - 36} ${cy + 96} Q${cx} ${cy + 116} ${cx + 36} ${cy + 96} L${cx + 36} ${cy + 86} L${cx - 36} ${cy + 86} Z" fill="rgba(0,0,0,.08)"/>`;
  const ey = cy + 8;
  const eyes = [-1, 1].map(s => `<ellipse cx="${cx + s * 36}" cy="${ey}" rx="9" ry="12" fill="#2A211D"/><circle cx="${cx + s * 36 + 3}" cy="${ey - 4}" r="3.5" fill="#FFF"/>
    <path d="M${cx + s * 22} ${ey - 30} Q${cx + s * 37} ${ey - 38} ${cx + s * 52} ${ey - 30}" stroke="${p.hc}" stroke-width="6" fill="none" stroke-linecap="round"/>
    ${p.f ? `<path d="M${cx + s * 26} ${ey - 12} L${cx + s * 22} ${ey - 16}" stroke="#2A211D" stroke-width="3"/>` : ""}`).join("");
  const glasses = p.glasses ? [-1, 1].map(s => `<rect x="${cx + s * 36 - 26}" y="${ey - 20}" width="52" height="40" rx="12" fill="rgba(255,255,255,.12)" stroke="#2C2C2C" stroke-width="4"/>`).join("") + `<path d="M${cx - 10} ${ey - 4} Q${cx} ${ey - 10} ${cx + 10} ${ey - 4}" stroke="#2C2C2C" stroke-width="4" fill="none"/>` : "";
  const mouth = talk
    ? `<path d="M${cx - 22} ${cy + 52} Q${cx} ${cy + 46} ${cx + 22} ${cy + 52} Q${cx + 16} ${cy + 76} ${cx} ${cy + 76} Q${cx - 16} ${cy + 76} ${cx - 22} ${cy + 52} Z" fill="#8E3B36"/><path d="M${cx - 12} ${cy + 68} Q${cx} ${cy + 62} ${cx + 12} ${cy + 68} Q${cx} ${cy + 76} ${cx - 12} ${cy + 68} Z" fill="#D9776E"/>`
    : `<path d="M${cx - 22} ${cy + 54} Q${cx} ${cy + 70} ${cx + 22} ${cy + 54}" stroke="#8E3B36" stroke-width="5" fill="none" stroke-linecap="round"/>`;
  const lips = p.f && talk ? "" : "";
  return `${hairBack(p, cx, cy)}${body}${neck}
    <ellipse cx="${cx - 96}" cy="${cy + 10}" rx="16" ry="24" fill="${p.skin}"/><ellipse cx="${cx + 96}" cy="${cy + 10}" rx="16" ry="24" fill="${p.skin}"/>
    <ellipse cx="${cx}" cy="${cy}" rx="98" ry="112" fill="${p.skin}"/>
    <ellipse cx="${cx - 58}" cy="${cy + 40}" rx="18" ry="10" fill="#F08F80" opacity=".35"/><ellipse cx="${cx + 58}" cy="${cy + 40}" rx="18" ry="10" fill="#F08F80" opacity=".35"/>
    ${eyes}${glasses}<path d="M${cx - 4} ${cy + 22} Q${cx + 6} ${cy + 34} ${cx - 6} ${cy + 36}" stroke="rgba(0,0,0,.25)" stroke-width="4" fill="none" stroke-linecap="round"/>
    ${mouth}${lips}${hairFront(p, cx, cy)}${p.hair === "pony" ? `<rect x="${cx + 70}" y="${cy - 82}" width="22" height="16" rx="6" fill="#C0392B" transform="rotate(30 ${cx + 81} ${cy - 74})"/>` : ""}`;
}

function desk(kind, flip) {
  const top = 615;
  const items = kind === "factory" || kind === "port"
    ? `<rect x="${flip ? 900 : 230}" y="${top - 60}" width="150" height="70" rx="6" fill="#3B4A57"/><rect x="${flip ? 912 : 242}" y="${top - 50}" width="126" height="45" fill="#7FB0D0"/>`
    : `<rect x="${flip ? 260 : 870}" y="${top - 8}" width="190" height="14" rx="4" fill="#C9CDD3"/><path d="M${flip ? 275 : 885} ${top - 8} L${flip ? 295 : 905} ${top - 120} L${flip ? 445 : 1035} ${top - 120} L${flip ? 425 : 1015} ${top - 8} Z" fill="#AEB4BC"/>
       <rect x="${flip ? 1020 : 230}" y="${top - 70}" width="58" height="70" rx="8" fill="#FFFFFF"/><path d="M${flip ? 1078 : 288} ${top - 55} q24 0 24 22 q0 22 -24 22" stroke="#FFFFFF" stroke-width="9" fill="none"/>
       <ellipse cx="${flip ? 1049 : 259}" cy="${top - 68}" rx="27" ry="6" fill="#6B3F22"/>`;
  return `${items}<rect x="0" y="${top}" width="${W}" height="${H - top}" fill="url(#gDesk)"/><rect x="0" y="${top}" width="${W}" height="6" fill="#E3BC8C" opacity=".8"/>`;
}

function svg(p, place, side, unitCol) {
  const cx = side === "A" ? 560 : 720, cy = 300;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <defs>
    <filter id="bl"><feGaussianBlur stdDeviation="5"/></filter>
    <linearGradient id="gWall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EFE3CF"/><stop offset="1" stop-color="#D9C6A8"/></linearGradient>
    <linearGradient id="gFac" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C9CED1"/><stop offset="1" stop-color="#9AA3A8"/></linearGradient>
    <linearGradient id="gSky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A9D4F0"/><stop offset="1" stop-color="#F6E3C4"/></linearGradient>
    <linearGradient id="gDesk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B07A4C"/><stop offset="1" stop-color="#7A5132"/></linearGradient>
    <radialGradient id="gWarm" cx="${side === "A" ? 0.2 : 0.8}" cy="0.1" r="0.9"><stop offset="0" stop-color="#FFD9A0" stop-opacity=".35"/><stop offset="1" stop-color="#FFD9A0" stop-opacity="0"/></radialGradient>
    <radialGradient id="gVig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient>
  </defs>
  ${background(place)}
  ${person(p, cx, cy, true)}
  ${desk(place, side === "B")}
  <rect width="${W}" height="${H}" fill="url(#gWarm)"/><rect width="${W}" height="${H}" fill="url(#gVig)"/>
  <rect x="0" y="${H - 8}" width="${W}" height="8" fill="${unitCol}"/>
</svg>`;
}

(async () => {
  const data = JSON.parse(fs.readFileSync(path.join(ROOT, "audio", "dialogues.json"), "utf8"));
  const COL = ["#5FB89E", "#8BA2E0", "#DDA05A", "#D883AE", "#6FB7CF"], PART = n => (n <= 5 ? 0 : n <= 8 ? 1 : n <= 11 ? 2 : n <= 16 ? 3 : 4);
  fs.mkdirSync(OUT, { recursive: true });
  const exe = fs.existsSync("/opt/pw-browsers/chromium") ? { executablePath: "/opt/pw-browsers/chromium" } : {};
  const b = await pw.chromium.launch(exe).catch(() => pw.chromium.launch());
  const page = await b.newPage({ viewport: { width: W, height: H } });
  for (const n of Object.keys(data)) {
    for (const side of ["A", "B"]) {
      const name = data[n].roles[side].split(" · ")[0];
      const p = PEOPLE[name];
      if (!p) { console.warn("Chưa có ngoại hình cho", name); continue; }
      await page.setContent(`<body style="margin:0">${svg(p, PLACE[n] || "office", side, COL[PART(+n)])}</body>`);
      await page.screenshot({ path: path.join(OUT, `u${n}_${side}.png`), clip: { x: 0, y: 0, width: W, height: H } });
    }
    console.log("Unit", n, "xong");
  }
  await b.close();
})();
