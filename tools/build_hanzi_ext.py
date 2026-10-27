#!/usr/bin/env python3
"""Tạo hanzi-x.json: dữ liệu bộ thủ + âm Hán Việt cho ~6.700 chữ thông dụng (GB2312),
dùng cho mục Dịch (hiện bộ thủ & mẹo nhớ cho từ bất kỳ). Các chữ đã có trong hanzi.json (soạn tay) không đưa vào đây.

  python3 tools/build_hanzi_ext.py UNIHAN_DB HANVIET_DATA_JS

- Cấu tạo chữ: Make Me a Hanzi (tools/mmah-dictionary.txt, cùng nguồn với build_hanzi.py).
- Âm Hán Việt: ưu tiên bảng theo pinyin của gói npm `hanviet-pinyin-words` (MIT; HANVIET_DATA_JS = src/hanvietData.js),
  thiếu thì dùng Unihan kVietnamese (UNIHAN_DB là file sqlite của gói npm `cjk-unihan`: package/data/unihan.db);
  chữ giản thể lấy âm của chữ phồn thể tương ứng.
- Tên bộ/thành phần: bảng HV trong build_hanzi.py (soạn tay), thiếu thì lấy âm Hán Việt của chính thành phần đó.
"""
import json, os, sqlite3, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_hanzi import parse, HV, AS_PART, FAMILY

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDC = {c for c in map(chr, range(0x2FF0, 0x2FFC))}


def gb2312():
    out = []
    for hi in range(0xB0, 0xF8):
        for lo in range(0xA1, 0xFF):
            try:
                out.append(bytes([hi, lo]).decode("gb2312"))
            except UnicodeDecodeError:
                pass
    return out


def main():
    db = sqlite3.connect(sys.argv[1])
    U = {}
    for ch, vi, trad in db.execute("select character, kVietnamese, kTraditionalVariant from unihan where kVietnamese!='' or kTraditionalVariant!=''"):
        if ch.startswith("\\x{"):
            ch = chr(int(ch[3:-1], 16))
        U[ch] = (vi.split(), [chr(int(x[2:], 16)) for x in trad.split()] if trad else [])

    t = open(sys.argv[2], encoding="utf-8").read()
    HVD = json.loads(t[t.index("=") + 1:].strip().rstrip(";"))
    TONE = {"\u0304": "1", "\u0301": "2", "\u030c": "3", "\u0300": "4"}

    def numeric(py):  # "wǒ" -> "wo3"; ü -> "u:" (cách ghi của hanviet-pinyin-words)
        out, tone = "", "5"
        for ch in unicodedata.normalize("NFD", py):
            if ch in TONE:
                tone = TONE[ch]
            elif ch == "\u0308":
                out += ":"
            else:
                out += ch
        return out + tone

    def viet(c, py=""):
        cands = [c] + U.get(c, ([], []))[1]
        key = numeric(py) if py else ""
        for k in cands:  # 1) bảng theo pinyin
            e = HVD.get(k)
            if e:
                if "*" in e and e["*"]:
                    return "/".join(e["*"][:2])
                if key in e and e[key]:
                    return "/".join(e[key][:2])
        for k in cands:  # 2) cùng âm nhưng khác thanh
            e = HVD.get(k) or {}
            for kk, v in e.items():
                if v and kk[:-1] == key[:-1]:
                    return "/".join(v[:2])
        for k in cands:  # 3) Unihan
            if U.get(k, ([], []))[0]:
                return "/".join(U[k][0][:2])
        for k in cands:  # 4) cách đọc bất kỳ của chữ
            for v in (HVD.get(k) or {}).values():
                if v:
                    return "/".join(v[:2])
        return ""

    D = {}
    for l in open(os.path.join(ROOT, "tools", "mmah-dictionary.txt"), encoding="utf-8"):
        j = json.loads(l)
        D[j["character"]] = j
    hand = json.load(open(os.path.join(ROOT, "hanzi.json"), encoding="utf-8"))
    hv_tbl = parse(HV)  # chữ|hán việt|nghĩa
    hv_tbl = {k: v for k, v in hv_tbl.items()}
    for k, v in AS_PART.items():
        hv_tbl[k] = v

    chars = [c for c in gb2312() if c in D and c not in hand]
    C, R, used = {}, {}, set()
    for c in chars:
        j = D[c]
        e = j.get("etymology") or {}
        parts = [p for p in j["decomposition"] if p not in IDC and p != "？" and p != c]
        py = (j.get("pinyin") or [""])[0]
        s = e.get("semantic") if e.get("type") == "pictophonetic" else ""
        p = e.get("phonetic") if e.get("type") == "pictophonetic" else ""
        if s not in parts or p not in parts:
            s = p = ""
        C[c] = [viet(c, py), py, "".join(parts), s or "", p or ""]
        used.update(parts)
    for p in used:
        if p in C or p in hand:
            continue
        name = hv_tbl.get(p)
        if name:
            R[p] = [name[0], name[1] if len(name) > 1 else ""]
        else:
            v = viet(p, (D.get(p, {}).get("pinyin") or [""])[0])
            if v:
                R[p] = [v, ""]
    # tên bộ/thành phần lấy cả từ hanzi.json (chữ soạn tay) khi chữ đó cũng là thành phần: app tự tra HZ trước
    fam = {k: v for k, v in FAMILY.items() if k in used or k in hand}
    out = {"c": C, "r": R, "f": fam}
    dst = os.path.join(ROOT, "hanzi-x.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    miss = sum(1 for v in C.values() if not v[0])
    print(f"{len(C)} chữ, {len(R)} thành phần, thiếu Hán Việt: {miss}, {os.path.getsize(dst)//1024} KB -> {dst}")


if __name__ == "__main__":
    main()
