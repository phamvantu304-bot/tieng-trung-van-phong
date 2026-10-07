#!/usr/bin/env python3
"""Video luyện nói đuổi (shadowing) cho một bài hội thoại.

Mỗi câu: đọc một lần (giọng theo vai), rồi một khoảng lặng dài bằng câu để người học nói theo
(có thanh đếm ngược). Khung hình: nền tối mờ, chữ Hán – pinyin – nghĩa tiếng Việt (vàng) ở giữa.

  python3 video/make_shadowing.py KOKORO_DIR 1 [2 ...]   -> video/out/shadowing-unit1.mp4
"""
import json, os, subprocess, sys, tempfile
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import make_video as mv          # phông chữ, pinyin, xuống dòng
import make_audio as ma          # giọng Kokoro, cắt lặng

W, H, FPS = 720, 1280, 25
YELLOW = (242, 196, 72, 255)
STEP = 0.25                      # thanh đếm ngược cập nhật mỗi 0,25 giây


def background(n):
    for name in (f"u{n}_A", f"u{n}_B"):
        fp = os.path.join(HERE, "scenes", name + ".png")
        if os.path.exists(fp):
            im = Image.open(fp).convert("RGB")
            k = H / im.height
            im = im.resize((int(im.width * k), H)).crop((0, 0, W, H))
            im = im.filter(ImageFilter.GaussianBlur(18))
            return ImageEnhance.Brightness(im).enhance(0.28).convert("RGBA")
    return Image.new("RGBA", (W, H), (16, 16, 16, 255))


def frame(bg, n, d, i, ln, state, left=1.0):
    img = bg.copy()
    dr = ImageDraw.Draw(img)
    dr.text((W / 2, 110), "SHADOWING · NÓI ĐUỔI", font=mv.F(mv.SANS_B, 20), fill=(200, 200, 200, 255), anchor="mm")
    dr.text((W / 2, 150), f"Unit {n} · {d['title']}", font=mv.F(mv.SERIF, 24), fill=(170, 170, 170, 255), anchor="mm")
    fz, fp, fv = mv.F(mv.ZH, 44), mv.F(mv.SERIF, 28), mv.F(mv.SERIF, 28)
    zl = mv.wrap(dr, ln["zh"], fz, W - 100, cjk=True)
    pl = mv.wrap(dr, ln["py"], fp, W - 100)
    vl = mv.wrap(dr, ln["vi"], fv, W - 100)
    block = len(zl) * 62 + 14 + len(pl) * 40 + 14 + len(vl) * 40
    y = H / 2 - block / 2 - 40
    who = d["roles"][ln["who"]].split(" · ")[0]
    dr.text((W / 2, y - 30), who, font=mv.F(mv.SANS_B, 20), fill=(150, 150, 150, 255), anchor="mm")
    for l in zl:
        y += 62
        dr.text((W / 2, y), l, font=fz, fill=(255, 255, 255, 255), anchor="ms", stroke_width=1, stroke_fill=(255, 255, 255, 255))
    y += 14
    for l in pl:
        y += 40
        dr.text((W / 2, y), l, font=fp, fill=(235, 235, 235, 255), anchor="ms")
    y += 14
    for l in vl:
        y += 40
        dr.text((W / 2, y), l, font=fv, fill=YELLOW, anchor="ms")
    # trạng thái: nghe / nói theo + thanh đếm ngược
    cy = H - 250
    if state == "listen":
        dr.text((W / 2, cy), "● Nghe", font=mv.F(mv.SANS_B, 26), fill=(170, 210, 255, 255), anchor="mm")
    else:
        dr.text((W / 2, cy), "● Đến lượt bạn — nói theo", font=mv.F(mv.SANS_B, 26), fill=YELLOW, anchor="mm")
        x0, x1 = 160, W - 160
        dr.rounded_rectangle([x0, cy + 32, x1, cy + 42], 5, fill=(80, 80, 80, 255))
        dr.rounded_rectangle([x0, cy + 32, x0 + (x1 - x0) * left, cy + 42], 5, fill=YELLOW)
    dr.text((W / 2, H - 120), f"{i + 1} / {len(d['lines'])}", font=mv.F(mv.SANS, 20), fill=(140, 140, 140, 255), anchor="mm")
    dr.text((W / 2, H - 80), "Tiếng Trung Văn phòng", font=mv.F(mv.SANS, 16), fill=(110, 110, 110, 255), anchor="mm")
    return img.convert("RGB")


def make(tts, n, out_dir):
    d = json.load(open(os.path.join(ROOT, "audio", "dialogues.json"), encoding="utf-8"))[n]
    bg = background(n)
    tmp = tempfile.mkdtemp(dir=out_dir)
    frames, chunks, sr = [], [], 24000
    # mở đầu 1,5 giây
    lead = 1.5
    intro = bg.copy()
    di = ImageDraw.Draw(intro)
    di.text((W / 2, H / 2 - 40), "SHADOWING", font=mv.F(mv.SANS_B, 52), fill=(255, 255, 255, 255), anchor="mm")
    di.text((W / 2, H / 2 + 20), f"Unit {n} · {d['title']}", font=mv.F(mv.SERIF, 28), fill=YELLOW, anchor="mm")
    di.text((W / 2, H / 2 + 70), "Nghe từng câu, rồi nói theo trong khoảng lặng", font=mv.F(mv.SERIF, 24), fill=(200, 200, 200, 255), anchor="mm")
    p = os.path.join(tmp, "intro.png"); intro.convert("RGB").save(p); frames.append((p, lead))
    chunks.append(np.zeros(int(lead * sr), np.float32))
    for i, ln in enumerate(d["lines"]):
        ln["py"] = mv.to_pinyin(ln["zh"])
        a = tts.generate(ln["zh"], sid=ma.voice(d["roles"][ln["who"]]), speed=0.85)
        sr = a.sample_rate
        s = ma.trim(np.array(a.samples, dtype=np.float32), sr)
        talk = len(s) / sr + 0.3
        pause = round(max(2.0, len(s) / sr * 1.1 + 0.8) / STEP) * STEP
        chunks += [s, np.zeros(int(0.3 * sr), np.float32), np.zeros(int(pause * sr), np.float32)]
        p = os.path.join(tmp, f"{i:02}_l.png"); frame(bg, n, d, i, ln, "listen").save(p); frames.append((p, talk))
        steps = int(pause / STEP)
        for k in range(steps):
            p = os.path.join(tmp, f"{i:02}_s{k:03}.png")
            frame(bg, n, d, i, ln, "speak", 1 - k / steps).save(p); frames.append((p, STEP))
        print(f"  câu {i + 1}/{len(d['lines'])}", flush=True)
    audio = np.concatenate(chunks)
    wav = os.path.join(tmp, "a.wav"); sf.write(wav, audio, sr)
    lst = os.path.join(tmp, "f.txt")
    with open(lst, "w") as f:
        for p, du in frames:
            f.write(f"file '{p}'\nduration {du:.3f}\n")
        f.write(f"file '{frames[-1][0]}'\n")
    out = os.path.join(out_dir, f"shadowing-unit{n}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav,
                    "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "23",
                    "-tune", "stillimage", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out],
                   check=True)
    subprocess.run(["rm", "-rf", tmp])
    print("=>", out, f"{len(audio) / sr:.1f}s")


if __name__ == "__main__":
    tts = ma.engine(sys.argv[1])
    out_dir = os.path.join(HERE, "out")
    os.makedirs(out_dir, exist_ok=True)
    for n in sys.argv[2:]:
        make(tts, n, out_dir)
