#!/usr/bin/env python3
"""Thu âm hội thoại bằng giọng AI Kokoro (chạy offline qua sherpa-onnx) và cập nhật mốc thời gian.

  python3 tools/make_audio.py dialogues KOKORO_DIR [unit ...]  -> audio/unitN-hoithoai.m4a + mốc t trong dialogues.json
  python3 tools/make_audio.py words KOKORO_DIR TEXTS.json      -> audio/tts/<mã>.m4a cho từ/câu (nút ▶ nghe)

KOKORO_DIR: thư mục giải nén kokoro-multi-lang-v1_0.tar.bz2
  (https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_0.tar.bz2)
Cần: pip install sherpa-onnx soundfile numpy; ffmpeg.
"""
import json, os, subprocess, sys, tempfile
import numpy as np, sherpa_onnx, soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEMALE, MALE, MALE_YOUNG = 47, 49, 51   # zf_xiaoxiao, zm_yunjian, zm_yunxia
SPEED = 0.9
LEAD, GAP, TAIL = 0.4, 0.7, 0.8         # giây im lặng: đầu bài, giữa câu, cuối bài


def engine(m):
    m = m.rstrip("/") + "/"
    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
                model=m + "model.onnx", voices=m + "voices.bin", tokens=m + "tokens.txt",
                data_dir=m + "espeak-ng-data", dict_dir=m + "dict",
                lexicon=m + "lexicon-us-en.txt," + m + "lexicon-zh.txt"),
            num_threads=4),
        rule_fsts=m + "date-zh.fst," + m + "phone-zh.fst," + m + "number-zh.fst",
        max_num_sentences=1)
    return sherpa_onnx.OfflineTts(cfg)


def voice(role):
    name = role.split(" · ")[0]
    if "Minh" in name:
        return MALE_YOUNG
    return MALE if name.startswith("Anh") else FEMALE


def trim(a, sr, thr=0.01):
    """Cắt bớt khoảng lặng thừa ở hai đầu câu, chừa 50 ms."""
    idx = np.where(np.abs(a) > thr)[0]
    if not len(idx):
        return a
    pad = int(0.05 * sr)
    return a[max(0, idx[0] - pad): idx[-1] + pad]


def encode(wav, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-c:a", "aac", "-b:a", "96k", "-ac", "1",
                    "-movflags", "+faststart", out], check=True)


def dialogues(tts, units):
    path = os.path.join(ROOT, "audio", "dialogues.json")
    data = json.load(open(path, encoding="utf-8"))
    for n in units or sorted(data, key=int):
        d = data[n]
        sr, chunks, t = None, [], LEAD
        for ln in d["lines"]:
            a = tts.generate(ln["zh"], sid=voice(d["roles"][ln["who"]]), speed=SPEED)
            sr = a.sample_rate
            s = trim(np.array(a.samples, dtype=np.float32), sr)
            if not chunks:
                chunks.append(np.zeros(int(LEAD * sr), np.float32))
            ln["t"] = round(t, 2)
            chunks += [s, np.zeros(int(GAP * sr), np.float32)]
            t += len(s) / sr + GAP
        chunks[-1] = np.zeros(int(TAIL * sr), np.float32)
        audio = np.concatenate(chunks)
        d["dur"] = round(len(audio) / sr, 1)
        d["file"] = f"audio/unit{n}-hoithoai.m4a"
        with tempfile.NamedTemporaryFile(suffix=".wav") as f:
            sf.write(f.name, audio, sr)
            encode(f.name, os.path.join(ROOT, d["file"]))
        print(f"Unit {n}: {d['dur']}s", flush=True)
        json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False)


def key(text):
    """FNV-1a 32 bit trên mã UTF-16 — app tính giống hệt để tìm file (hàm ttsKey trong index.html)."""
    b, h = text.encode("utf-16-le"), 0x811C9DC5
    for i in range(0, len(b), 2):
        h = ((h ^ (b[i] | b[i + 1] << 8)) * 0x01000193) & 0xFFFFFFFF
    return f"{h:08x}"


def words(tts, texts_file):
    texts = json.load(open(texts_file, encoding="utf-8"))
    out = os.path.join(ROOT, "audio", "tts")
    os.makedirs(out, exist_ok=True)
    have = set()
    for i, t in enumerate(sorted(set(texts))):
        k = key(t)
        dst = os.path.join(out, k + ".m4a")
        if not os.path.exists(dst):
            a = tts.generate(t, sid=FEMALE, speed=0.85)
            s = trim(np.array(a.samples, dtype=np.float32), a.sample_rate)
            with tempfile.NamedTemporaryFile(suffix=".wav") as f:
                sf.write(f.name, s, a.sample_rate)
                encode(f.name, dst)
        have.add(k)
        if i % 50 == 0:
            print(i, flush=True)
    # bỏ file cũ không còn dùng
    for f in os.listdir(out):
        if f.endswith(".m4a") and f[:-4] not in have:
            os.remove(os.path.join(out, f))
    json.dump(sorted(have), open(os.path.join(out, "index.json"), "w"), separators=(",", ":"))
    print(len(have), "file")


if __name__ == "__main__":
    mode, model = sys.argv[1], sys.argv[2]
    tts = engine(model)
    if mode == "dialogues":
        dialogues(tts, sys.argv[3:])
    else:
        words(tts, sys.argv[3])
