"""グラフを見ながらしゃべる、短い掛け合い動画を作る（VOICEVOX 用）。8本目（debate8）で使った。

  python scripts/make_manzai.py prepare debate8                       # 1文ずつの読み上げリスト
  python scripts/tts_voicevox.py build_debate8_vv/sentences.tsv build_debate8_vv/audio --speed 1.25
  uv run --with pillow python scripts/make_manzai.py render debate8   # 画面を作り、音声と結合する

フォルダには次を置く。
- log.md：話者「セリフ」を1発言1行
- manzai.json：話者（VOICEVOX のスタイルID・色・立場）、発言ごとの場面とグラフ、タイトル、最後の画面
- charts/：グラフの画像（manzai.json の crop で切り抜ける）
- readings.tsv（なくてもよい）：表記<TAB>読み。読み上げのときだけ置き換える

画面：上にグラフ、下にセリフ。セリフは発言を4行ずつのページに分け、読み終わった文は白、読み上げ中の文は黄色、
まだ読んでいない文は出さない（置き場所は最初から決めておくので、文が出ても行は動かない）。
"""
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H, FPS = 1920, 1080, 30
FONT_R = next((p for p in [r"C:\Windows\Fonts\BIZ-UDGothicR.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
               if Path(p).exists()), None)
FONT_B = next((p for p in [r"C:\Windows\Fonts\BIZ-UDGothicB.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]
               if Path(p).exists()), None)

BG = (20, 22, 28)
PANEL = (32, 35, 44)
WHITE, GRAY, DIM, HIGHLIGHT = (245, 245, 245), (160, 165, 175), (95, 100, 110), (255, 226, 77)

CHART_BOX = (40, 78, W - 40, 708)          # グラフを置く枠（左, 上, 右, 下）
TEXT_X, TEXT_Y, TEXT_W = 92, 796, W - 92 - 70
FONT_SIZE, LINE_H, MAX_LINES = 46, 62, 4
GAP_SENTENCE, GAP_SPEAKER, TITLE_SEC, END_SEC = 0.12, 0.35, 2.5, 4.0

NO_LINE_START = "、。，．」』）？！%ー〜…"
TOKEN = re.compile(r"[0-9A-Za-z][0-9A-Za-z.,%*+\-]*|.", re.S)   # 数字・英単語は途中で改行しない


def font(path, size):
    return ImageFont.truetype(path, size, index=0)


def load(folder):
    d = ROOT / folder
    cfg = json.loads((d / "manzai.json").read_text(encoding="utf-8"))
    turns = []
    for line in (d / "log.md").read_text(encoding="utf-8").splitlines():
        if line.strip():
            speaker, text = line.split("「", 1)
            turns.append((speaker, text.rstrip()[:-1]))
    assert len(turns) == len(cfg["turns"]), "log.md の発言数と manzai.json の turns の数が合わない"
    readings = []
    if (d / "readings.tsv").exists():
        readings = [l.split("\t") for l in (d / "readings.tsv").read_text(encoding="utf-8").splitlines() if "\t" in l]
    build = ROOT / f"build_{folder}_vv"
    return d, cfg, turns, readings, build


def split_sentences(text):
    return [s.strip() for s in re.findall(r"[^。？！]+[。？！]?", text) if s.strip()]


def reading(text, readings):
    for a, b in sorted(readings, key=lambda r: -len(r[0])):
        text = text.replace(a, b)
    return text


def prepare(folder):
    d, cfg, turns, readings, build = load(folder)
    build.mkdir(exist_ok=True)
    rows = []
    for speaker, text in turns:
        style = cfg["speakers"][speaker]["style"]
        for s in split_sentences(text):
            rows.append(f"{len(rows):03d}\t{style}\t{reading(s, readings)}")
    (build / "sentences.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    chars = sum(len(re.sub(r"\s", "", t)) for _, t in turns)
    print(f"{len(rows)} sentences, {chars} chars -> {build / 'sentences.tsv'}")


# ---------- 画面 ----------

def layout(sentences, fnt, draw):
    """文をつなげて折り返し、(文の番号, 行, x, 文字列) の断片の並びにする。行は 0 から。"""
    tokens = [(m.group(), k) for k, s in enumerate(sentences) for m in TOKEN.finditer(s)]
    lines, cur, x = [], [], 0.0
    for i, (tok, k) in enumerate(tokens):
        w = draw.textlength(tok, font=fnt)
        if x + w > TEXT_W and cur:
            carry = []   # 行頭に来てはいけない文字は、前の行の最後の1字と一緒に送る
            while tok[0] in NO_LINE_START and cur and len(carry) < 1:
                carry.insert(0, cur.pop())
            lines.append(cur)
            cur, x = carry, sum(draw.textlength(t, font=fnt) for t, _ in carry)
        cur.append((tok, k))
        x += w
    if cur:
        lines.append(cur)
    return lines


def paginate(sentences, fnt, draw):
    """発言をページに分ける。ページは文の切れ目で変え、各ページは行の頭から組む。
    MAX_LINES 行に収まる最少のページ数で、ページごとの行数がなるべくそろう分け方を選ぶ。
    返り値は [(そのページの文の番号のリスト, 組んだ行), ...]。"""
    n = len(sentences)
    memo = {}

    def lines_of(i, j):   # 文 i〜j-1 を1ページに組んだときの行
        if (i, j) not in memo:
            memo[(i, j)] = [[(t, k + i) for t, k in ln] for ln in layout(sentences[i:j], fnt, draw)]
        return memo[(i, j)]

    best = {}

    def solve(i):   # 文 i 以降の分け方：(ページ数, 最大行数-最小行数, 区切り)
        if i == n:
            return (0, 0, [])
        if i in best:
            return best[i]
        cands = []
        for j in range(i + 1, n + 1):
            h = len(lines_of(i, j))
            if h > MAX_LINES and j > i + 1:
                break
            np_, _, rest = solve(j)
            sizes = [h] + [len(lines_of(a, b)) for a, b in rest]
            cands.append((np_ + 1, max(sizes) - min(sizes), [(i, j)] + rest))
        best[i] = min(cands, key=lambda c: (c[0], c[1]))
        return best[i]

    return [(list(range(a, b)), lines_of(a, b)) for a, b in solve(0)[2]]


def new_canvas():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def chart_image(d, turn, cache={}):
    key = (turn["chart"], tuple(turn.get("crop", ())))
    if key not in cache:
        im = Image.open(d / "charts" / turn["chart"]).convert("RGB")
        if turn.get("crop"):
            im = im.crop(tuple(turn["crop"]))
        l, t, r, b = CHART_BOX
        s = min((r - l) / im.width, (b - t) / im.height)
        cache[key] = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    return cache[key]


def frame_title(cfg, path):
    img, d = new_canvas()
    y = 330
    kick = font(FONT_R, 48)
    d.text((W / 2, y), cfg["title_kicker"], font=kick, fill=GRAY, anchor="mm")
    big = font(FONT_B, 96)
    for i, line in enumerate(cfg["title"]):
        d.text((W / 2, y + 150 + i * 130), line, font=big, fill=WHITE, anchor="mm")
    x0 = W / 2
    names = list(cfg["speakers"])
    small = font(FONT_B, 44)
    for i, name in enumerate(names):
        sp = cfg["speakers"][name]
        label = f"{name}｜{sp['tag']}"
        # 1人目は「vs」の左に右寄せ、2人目は右に左寄せ
        tx, anchor = (x0 - 70, "rm") if i == 0 else (x0 + 70, "lm")
        d.text((tx, 800), label, font=small, fill=tuple(sp["color"]), anchor=anchor)
    d.text((x0, 800), "vs", font=small, fill=GRAY, anchor="mm")
    img.save(path)


def frame_talk(cfg, dirpath, turn, speaker, page, page_lines, active, path, page_no, n_pages):
    img, d = new_canvas()
    sp = cfg["speakers"][speaker]
    color = tuple(sp["color"])
    # 上の帯：場面とヘッダー
    d.text((40, 38), turn["scene"], font=font(FONT_B, 34), fill=WHITE, anchor="lm")
    d.text((W - 40, 38), cfg["header"], font=font(FONT_R, 28), fill=GRAY, anchor="rm")
    # グラフ（白い台紙ごと中央に）
    ch = chart_image(dirpath, turn)
    l, t, r, b = CHART_BOX
    img.paste(ch, (l + (r - l - ch.width) // 2, t + (b - t - ch.height) // 2))
    # セリフの枠
    d.rounded_rectangle((40, 724, W - 40, H - 24), radius=18, fill=PANEL)
    d.rounded_rectangle((40, 724, 52, H - 24), radius=6, fill=color)
    name_f = font(FONT_B, 38)
    d.text((TEXT_X, 760), speaker, font=name_f, fill=color, anchor="lm")
    nx = TEXT_X + d.textlength(speaker, font=name_f) + 24
    d.text((nx, 762), sp["tag"], font=font(FONT_R, 28), fill=GRAY, anchor="lm")
    if n_pages > 1:
        d.text((W - 70, 762), f"{page_no}/{n_pages}", font=font(FONT_R, 28), fill=DIM, anchor="rm")
    # 本文：このページの行だけ。読み終わった文は白、読み上げ中は黄色、まだの文は出さない
    fnt = font(FONT_R, FONT_SIZE)
    fnt_b = font(FONT_B, FONT_SIZE)
    y = TEXT_Y
    for ln in page_lines:
        x = TEXT_X
        for tok, k in ln:
            w = d.textlength(tok, font=fnt)
            if k in page and k <= active:
                f = fnt_b if k == active else fnt
                d.text((x, y), tok, font=f, fill=HIGHLIGHT if k == active else WHITE)
            x += w
        y += LINE_H
    img.save(path)


def frame_end(cfg, cast, path):
    img, d = new_canvas()
    big = font(FONT_B, 84)
    for i, line in enumerate(cfg["end"]):
        d.text((W / 2, 360 + i * 120), line, font=big, fill=WHITE, anchor="mm")
    small = font(FONT_R, 34)
    credits = [" ／ ".join(f"{n}：{s['credit']}" for n, s in cfg["speakers"].items()),
               f"音声：VOICEVOX:{cast}", cfg.get("notes", "")]
    for i, line in enumerate(c for c in credits if c):
        d.text((W / 2, 760 + i * 56), line, font=small, fill=GRAY, anchor="mm")
    img.save(path)


# ---------- 結合 ----------

def trim_silence(data, rate, threshold=200, margin=0.04):
    import array
    a = array.array("h", data)
    first = next((i for i, v in enumerate(a) if abs(v) > threshold), 0)
    last = next((i for i in range(len(a) - 1, -1, -1) if abs(a[i]) > threshold), len(a) - 1)
    pad = int(margin * rate)
    return a[max(0, first - pad):min(len(a), last + pad)].tobytes()


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def render(folder):
    dirpath, cfg, turns, readings, build = load(folder)
    frames, audio = build / "frames", build / "audio"
    frames.mkdir(parents=True, exist_ok=True)
    out_dir = ROOT / "video"
    out_mp4, out_srt = out_dir / f"{cfg['video']}.mp4", out_dir / f"{cfg['video']}.srt"
    cast_file = audio / "cast.txt"
    cast = cast_file.read_text(encoding="utf-8").strip() if cast_file.exists() else ""

    with wave.open(str(audio / "000.wav")) as w:
        params = w.getparams()
    rate, unit = params.framerate, params.sampwidth * params.nchannels
    chunks, timeline, t = [], [], 0.0

    def silence(sec):
        nonlocal t
        n = int(round(sec * rate))
        chunks.append(b"\x00" * n * unit)
        t += n / rate

    p = frames / "title.png"
    frame_title(cfg, p)
    timeline.append((p, t, None))
    silence(TITLE_SEC)

    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    fnt = font(FONT_R, FONT_SIZE)
    idx, page_counts = 0, []
    for n, ((speaker, text), turn) in enumerate(zip(turns, cfg["turns"])):
        if n:
            silence(GAP_SPEAKER)
        sentences = split_sentences(text)
        pages = paginate(sentences, fnt, probe)
        page_counts.append(len(pages))
        for k, s in enumerate(sentences):
            if k:
                silence(GAP_SENTENCE)
            no = next(i for i, (pg, _) in enumerate(pages) if k in pg)
            p = frames / f"{idx:03d}.png"
            frame_talk(cfg, dirpath, turn, speaker, *pages[no], k, p, no + 1, len(pages))
            with wave.open(str(audio / f"{idx:03d}.wav")) as w:
                data = trim_silence(w.readframes(w.getnframes()), rate)
            timeline.append((p, t, f"{speaker}：{s}"))
            chunks.append(data)
            t += len(data) / unit / rate
            idx += 1

    silence(0.4)
    p = frames / "end.png"
    frame_end(cfg, cast, p)
    timeline.append((p, t, None))
    silence(END_SEC)

    audio_all = build / "audio_all.wav"
    with wave.open(str(audio_all), "wb") as w:
        w.setparams(params)
        w.writeframes(b"".join(chunks))

    bounds = [tl[1] for tl in timeline] + [t]
    fr = [round(b * FPS) for b in bounds]
    lines = []
    for (img, *_), f0, f1 in zip(timeline, fr, fr[1:]):
        lines += [f"file '{img.as_posix()}'", f"duration {(f1 - f0) / FPS:.6f}"]
    lines.append(f"file '{timeline[-1][0].as_posix()}'")
    concat = build / "frames.txt"
    concat.write_text("\n".join(lines) + "\n", encoding="utf-8")

    srt, n = [], 0
    for (img, s0, text), s1 in zip(timeline, bounds[1:]):
        if text:
            n += 1
            srt += [str(n), f"{srt_time(s0)} --> {srt_time(s1)}", text, ""]
    out_dir.mkdir(exist_ok=True)
    out_srt.write_text("\n".join(srt), encoding="utf-8")

    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat), "-i", str(audio_all),
        "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-tune", "stillimage", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out_mp4),
    ], check=True)
    print(f"{idx} sentences, pages per turn {page_counts}, {t:.1f} sec -> {out_mp4}")


if __name__ == "__main__":
    {"prepare": prepare, "render": render}[sys.argv[1]](sys.argv[2].rstrip("/"))
