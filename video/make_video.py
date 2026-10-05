#!/usr/bin/env python3
"""Ghép hội thoại 16 unit thành một video dọc (9:16) kiểu phụ đề song ngữ.

Mỗi câu hiện 3 dòng: chữ Hán · pinyin · tiếng Việt, chạy khớp theo mốc thời gian
trong audio/dialogues.json. Trước mỗi unit có thẻ tiêu đề ngắn.

Cần: ffmpeg, pip install pillow pypinyin
Chạy:  python3 video/make_video.py [thư_mục_ra]   (mặc định: video/out)
"""
import json, math, os, random, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pypinyin import Style, pinyin

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, "video", "out")
W, H = 720, 1280
INTRO = 3.0      # giây thẻ tiêu đề mỗi unit
TAIL = 1.0       # nghỉ sau mỗi unit
FPS = 30

ZH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F = lambda p, s: ImageFont.truetype(p, s)

UNITS = {
    "1": ("求职与面试", 0), "2": ("入职手续", 0), "3": ("公司与部门介绍", 0),
    "4": ("会议安排", 0), "5": ("主持会议与分工", 0),
    "6": ("建立业务关系与产品介绍", 1), "7": ("询盘与报价", 1), "8": ("价格谈判", 1),
    "9": ("参观工厂", 2), "10": ("生产与质量控制", 2), "11": ("包装与定制", 2),
    "12": ("签订合同", 3), "13": ("国际运输与物流", 3), "14": ("海关与保险", 3),
    "15": ("索赔与投诉处理", 3), "16": ("售后服务与长期合作", 3),
}
PARTS = [("职场入门", "Phần 1 · Môi trường công sở", "#5FB89E"),
         ("国际商务谈判", "Phần 2 · Đàm phán thương mại", "#8BA2E0"),
         ("制造与工厂", "Phần 3 · Chế tạo & Nhà máy", "#DDA05A"),
         ("合同·物流·售后", "Phần 4 · Hợp đồng – Logistics – Hậu mãi", "#D883AE")]
SURNAME = {"Vương Lan": "兰", "Vương": "王", "Minh": "明", "Lý": "李", "Lâm": "林",
           "Trần": "陈", "Trương": "张"}

PUNCT = {"，": ", ", "。": ". ", "？": "? ", "！": "! ", "、": ", ", "：": ": ", "；": "; ",
         "“": "\"", "”": "\"", "（": " (", "）": ") ", "…": "…", "—": "—", "《": "«", "》": "»"}


TONE4 = set("àèìòùǜ")
TONE123 = set("āēīōūǖáéíóúǘǎěǐǒǔǚ")


def _tone(syl):
    return 4 if set(syl) & TONE4 else (1 if set(syl) & TONE123 else 0)


def to_pinyin(zh):
    # pinyin theo từng chữ, có biến điệu 一 / 不 như giáo trình
    chars = [s[0] for s in pinyin(zh, style=Style.TONE, errors=lambda s: list(s))]
    if len(chars) == len(zh):
        for i, ch in enumerate(zh):
            nxt = _tone(chars[i + 1]) if i + 1 < len(zh) and re.match(r"[\u4e00-\u9fff]", zh[i + 1]) else 0
            if ch == "不" and nxt == 4:
                chars[i] = "bú"
            elif ch == "一" and nxt and (i == 0 or zh[i - 1] not in "第十") and zh[i + 1] not in "月号日楼":
                chars[i] = "yí" if nxt == 4 else "yì"
    out = []
    for c in chars:
        if len(c) == 1 and ord(c) > 0x2000:
            out.append(PUNCT.get(c, c))
        else:
            out.append(" " + c)
    t = "".join(out)
    t = re.sub(r"\s+([,.?!:;)»…])", r"\1", t)
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r"(^|[.?!] )(\w)", lambda m: m.group(1) + m.group(2).upper(), t)


def hexrgb(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def wrap(draw, text, font, maxw, cjk=False):
    tokens = list(text) if cjk else text.split(" ")
    lines, cur = [], ""
    for tk in tokens:
        cand = cur + tk if cjk else (cur + " " + tk if cur else tk)
        if draw.textlength(cand, font=font) <= maxw or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = tk
    if cur:
        lines.append(cur)
    # không để dấu câu đứng đầu dòng chữ Hán
    if cjk:
        for i in range(1, len(lines)):
            while lines[i] and lines[i][0] in "，。？！、：；）”…":
                lines[i - 1] += lines[i][0]
                lines[i] = lines[i][1:]
    return [l for l in lines if l]


# ---------- khung cảnh (dải ảnh phía trên) ----------
BAND_Y, BAND_H = 230, 405


def scene_bg(unit, accent):
    rnd = random.Random(int(unit) * 7919)
    img = Image.new("RGB", (W, BAND_H))
    d = ImageDraw.Draw(img)
    a = hexrgb(accent)[:3]
    top = tuple(int(c * 0.22 + 18) for c in a)
    bot = (14, 12, 10)
    for y in range(BAND_H):
        k = y / BAND_H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] * (1 - k) + bot[i] * k) for i in range(3)))
    # cửa sổ văn phòng mờ phía sau
    win = Image.new("RGBA", (W, BAND_H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(win)
    for i in range(4):
        x = 40 + i * 170
        wd.rectangle([x, 40, x + 140, 250], fill=(255, 226, 170, 38))
        wd.line([(x + 70, 40), (x + 70, 250)], fill=(0, 0, 0, 60), width=4)
        wd.line([(x, 145), (x + 140, 145)], fill=(0, 0, 0, 60), width=4)
    # đèn bokeh ấm
    for _ in range(26):
        r = rnd.randint(10, 46)
        x, y = rnd.randint(0, W), rnd.randint(0, int(BAND_H * 0.7))
        c = rnd.choice([(255, 210, 140), (255, 236, 200), a])
        wd.ellipse([x - r, y - r, x + r, y + r], fill=c + (rnd.randint(25, 70),))
    win = win.filter(ImageFilter.GaussianBlur(9))
    img = Image.alpha_composite(img.convert("RGBA"), win)
    # mặt bàn
    d = ImageDraw.Draw(img)
    d.polygon([(0, 330), (W, 330), (W, BAND_H), (0, BAND_H)], fill=(40, 30, 22, 255))
    d.line([(0, 330), (W, 330)], fill=(120, 90, 60, 255), width=2)
    # vignette
    vig = Image.new("L", (W, BAND_H), 0)
    vd = ImageDraw.Draw(vig)
    for i in range(60):
        vd.rectangle([i, i, W - i, BAND_H - i], outline=int(150 * (1 - i / 60)))
    img.paste((0, 0, 0, 255), (0, 0), vig.filter(ImageFilter.GaussianBlur(20)))
    return img


def avatar(img, cx, cy, ch, role, accent, active):
    d = ImageDraw.Draw(img)
    a = hexrgb(accent)
    R = 64
    if active:
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([cx - R - 26, cy - R - 26, cx + R + 26, cy + R + 26], fill=a[:3] + (150,))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18)))
        d = ImageDraw.Draw(img)
    # thân
    body = (58, 66, 80, 255) if active else (40, 44, 52, 255)
    d.ellipse([cx - 92, cy + 48, cx + 92, cy + 260], fill=body)
    img.alpha_composite(TABLE[0], (0, 330))  # mặt bàn che phần thân dưới
    d = ImageDraw.Draw(img)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(236, 214, 190, 255) if active else (150, 138, 124, 255),
              outline=a if active else (90, 90, 90, 255), width=5)
    f = F(ZH, 62)
    d.text((cx, cy + 2), ch, font=f, fill=(40, 30, 24, 255), anchor="mm")
    name, _, title = role.partition(" · ")
    col = (255, 255, 255, 255) if active else (150, 150, 150, 255)
    d.text((cx, 284), name, font=F(SANS_B, 22), fill=col, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0, 255))
    d.text((cx, 310), title, font=F(SANS, 18), fill=col[:3] + (220,), anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0, 255))
    if active:  # bóng thoại nhỏ
        bx, by = cx + (54 if cx < W / 2 else -54), cy - 86
        d.rounded_rectangle([bx - 30, by - 20, bx + 30, by + 20], 12, fill=a)
        for i, dx in enumerate((-14, 0, 14)):
            d.ellipse([bx + dx - 4, by - 4, bx + dx + 4, by + 4], fill=(20, 20, 20, 255))


def surname_char(role):
    name = role.split(" · ")[0]
    for k, v in SURNAME.items():
        if k in name:
            return v
    return name.split()[-1][0]


TABLE = [None]


# ---------- khung hình ----------
def base_frame(n, d, accent):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    dr = ImageDraw.Draw(img)
    dr.text((W / 2, 92), f"UNIT {n}", font=F(SANS_B, 22), fill=hexrgb(accent), anchor="mm")
    dr.text((W / 2, 140), UNITS[n][0], font=F(ZH, 40), fill=(255, 255, 255, 255), anchor="mm",
            stroke_width=1, stroke_fill=(255, 255, 255, 255))
    dr.text((W / 2, 188), d["title"], font=F(SERIF, 24), fill=(200, 200, 200, 255), anchor="mm")
    dr.text((24, H - 40), "Tiếng Trung Văn phòng · Hội thoại 16 Unit", font=F(SANS, 16),
            fill=(110, 110, 110, 255), anchor="lm")
    return img


def frame(n, d, idx, accent, bg):
    img = base_frame(n, d, accent)
    band = bg.copy()
    who = d["lines"][idx]["who"] if idx is not None else None
    TABLE[0] = bg.crop((0, 330, W, BAND_H))
    avatar(band, 190, 150, surname_char(d["roles"]["A"]), d["roles"]["A"], accent, who == "A")
    avatar(band, W - 190, 150, surname_char(d["roles"]["B"]), d["roles"]["B"], accent, who == "B")
    if idx is not None:  # phụ đề nhỏ trên ảnh như bản gốc
        bd = ImageDraw.Draw(band)
        f = F(ZH, 18)
        t = d["lines"][idx]["zh"]
        if bd.textlength(t, font=f) > W - 40:
            while bd.textlength(t + "…", font=f) > W - 40:
                t = t[:-1]
            t += "…"
        bd.text((W / 2, BAND_H - 24), t, font=f, fill=(255, 255, 255, 255), anchor="mm",
                stroke_width=2, stroke_fill=(0, 0, 0, 255))
    img.paste(band, (0, BAND_Y))
    dr = ImageDraw.Draw(img)
    if idx is None:
        return img
    ln = d["lines"][idx]
    x, y, mw = 48, BAND_Y + BAND_H + 70, W - 96
    who_name = d["roles"][ln["who"]].split(" · ")[0]
    dr.text((x, y), f"{who_name}:", font=F(SANS_B, 20), fill=hexrgb(accent), anchor="ls")
    y += 22
    fz, fp, fv = F(ZH, 36), F(SERIF, 27), F(SERIF, 27)
    for l in wrap(dr, ln["zh"], fz, mw, cjk=True):
        y += 50
        dr.text((x, y), l, font=fz, fill=(255, 255, 255, 255), anchor="ls", stroke_width=1,
                stroke_fill=(255, 255, 255, 255))
    y += 14
    for l in wrap(dr, ln["py"], fp, mw):
        y += 38
        dr.text((x, y), l, font=fp, fill=(225, 225, 225, 255), anchor="ls")
    y += 6
    for l in wrap(dr, ln["vi"], fv, mw):
        y += 38
        dr.text((x, y), l, font=fv, fill=(200, 200, 200, 255), anchor="ls")
    # tiến độ
    total = len(d["lines"])
    dr.text((W - 24, H - 40), f"{idx + 1}/{total}", font=F(SANS, 16), fill=(110, 110, 110, 255), anchor="rm")
    return img


def title_card(n, d, accent):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    dr = ImageDraw.Draw(img)
    part = PARTS[UNITS[n][1]]
    dr.text((W / 2, 420), part[1], font=F(SANS, 22), fill=hexrgb(accent), anchor="mm")
    dr.text((W / 2, 520), f"UNIT {n}", font=F(SANS_B, 64), fill=(255, 255, 255, 255), anchor="mm")
    dr.line([(W / 2 - 60, 580), (W / 2 + 60, 580)], fill=hexrgb(accent), width=3)
    dr.text((W / 2, 650), UNITS[n][0], font=F(ZH, 54), fill=(255, 255, 255, 255), anchor="mm",
            stroke_width=1, stroke_fill=(255, 255, 255, 255))
    dr.text((W / 2, 715), to_pinyin(UNITS[n][0]).rstrip("."), font=F(SERIF, 28), fill=(220, 220, 220, 255), anchor="mm")
    dr.text((W / 2, 760), d["title"], font=F(SERIF, 30), fill=(200, 200, 200, 255), anchor="mm")
    y = 840
    for l in wrap(dr, d["scene"], F(SERIF, 24), W - 140):
        dr.text((W / 2, y), l, font=F(SERIF, 24), fill=(150, 150, 150, 255), anchor="mm")
        y += 34
    return img


def cover():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    dr = ImageDraw.Draw(img)
    dr.text((W / 2, 440), "办公室中文", font=F(ZH, 72), fill=(255, 255, 255, 255), anchor="mm",
            stroke_width=1, stroke_fill=(255, 255, 255, 255))
    dr.text((W / 2, 520), "bàngōngshì Zhōngwén", font=F(SERIF, 32), fill=(220, 220, 220, 255), anchor="mm")
    dr.text((W / 2, 580), "Tiếng Trung Văn phòng", font=F(SERIF_B, 40), fill=(255, 255, 255, 255), anchor="mm")
    dr.text((W / 2, 650), "16 bài hội thoại · Hán – Pinyin – Việt", font=F(SERIF, 26), fill=(180, 180, 180, 255), anchor="mm")
    for i, p in enumerate(PARTS):
        dr.text((W / 2, 760 + i * 40), p[1], font=F(SANS, 20), fill=hexrgb(p[2]), anchor="mm")
    return img


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    data = json.load(open(os.path.join(ROOT, "audio", "dialogues.json"), encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "tmp")
    os.makedirs(tmp, exist_ok=True)
    srt, parts, t0 = [], [], 0.0

    def seg_video(name, frames, audio=None, adelay=0.0, total=None):
        """frames: [(png, dur)] -> mp4 với audio (hoặc im lặng)."""
        lst = os.path.join(tmp, name + ".txt")
        with open(lst, "w") as f:
            for p, du in frames:
                f.write(f"file '{p}'\nduration {du:.3f}\n")
            f.write(f"file '{frames[-1][0]}'\n")
        out = os.path.join(tmp, name + ".mp4")
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst]
        if audio:
            ms = int(adelay * 1000)
            cmd += ["-i", audio, "-filter_complex", f"[1:a]adelay={ms}|{ms},apad[a]", "-map", "0:v", "-map", "[a]"]
        else:
            cmd += ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-map", "0:v", "-map", "1:a"]
        cmd += ["-t", f"{total:.3f}", "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-preset", "medium",
                "-crf", "22", "-tune", "stillimage", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2", out]
        run(cmd)
        parts.append(out)

    def ts(s):
        ms = int(round(s * 1000))
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"

    p = os.path.join(tmp, "cover.png")
    cover().convert("RGB").save(p)
    seg_video("u00", [(p, 3.0)], total=3.0)
    t0 += 3.0

    for n in sorted(data, key=int):
        d = data[n]
        accent = PARTS[UNITS[n][1]][2]
        for ln in d["lines"]:
            ln["py"] = to_pinyin(ln["zh"])
        audio = os.path.join(ROOT, d["file"])
        adur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                              "-of", "csv=p=0", audio]).decode())
        total = INTRO + adur + TAIL
        bg = scene_bg(n, accent)
        frames = []
        p = os.path.join(tmp, f"u{n}_title.png")
        title_card(n, d, accent).convert("RGB").save(p)
        frames.append((p, INTRO))
        first = d["lines"][0]["t"]
        if first > 0.05:
            p = os.path.join(tmp, f"u{n}_pre.png")
            frame(n, d, None, accent, bg).convert("RGB").save(p)
            frames.append((p, first))
        for i, ln in enumerate(d["lines"]):
            end = d["lines"][i + 1]["t"] if i + 1 < len(d["lines"]) else adur + TAIL
            p = os.path.join(tmp, f"u{n}_{i:02}.png")
            frame(n, d, i, accent, bg).convert("RGB").save(p)
            frames.append((p, end - ln["t"]))
            srt.append((t0 + INTRO + ln["t"], t0 + INTRO + min(end, adur), f"{ln['zh']}\n{ln['py']}\n{ln['vi']}"))
        seg_video(f"u{int(n):02}", frames, audio, INTRO, total)
        t0 += total
        print(f"Unit {n} xong ({total:.1f}s)", flush=True)

    lst = os.path.join(tmp, "all.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    final = os.path.join(OUT, "hoi-thoai-16-unit.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", final])
    with open(os.path.join(OUT, "hoi-thoai-16-unit.srt"), "w", encoding="utf-8") as f:
        for i, (a, b, t) in enumerate(srt, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n")
    print("=>", final, f"{t0 / 60:.1f} phút")


if __name__ == "__main__":
    main()
