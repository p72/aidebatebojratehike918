"""討論動画を作る。

  uv run --with pillow python scripts/make_video.py prepare <対象>          # 1文ずつの読み上げリストを作る
  powershell -File scripts/tts_onecore.ps1 ...                              # 1文ずつ WAV を作る
  uv run --with pillow python scripts/make_video.py render <対象> [paged]   # 画面を作り、音声と結合する

<対象> は 1（1本目・ファクトシートあり）、2（ガチ討論版）、1p・2p（それぞれのページ表示版）、
または topic.env のある討論フォルダ（debate3 など）。フォルダのときは、途中のファイルは build_<フォルダ>/ にでき、
最後に paged を付けるとページ表示版（音声は同じものを使う）を作る。
"""
import re
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from topic import load, read_log, scene_names

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "video"

W, H, FPS = 1920, 1080, 30
FONT_R = r"C:\Windows\Fonts\BIZ-UDGothicR.ttc"
FONT_B = r"C:\Windows\Fonts\BIZ-UDGothicB.ttc"
WHITE, GRAY, DIM = (255, 255, 255), (150, 150, 150), (90, 90, 90)


# 話者ごとの声（名前は tts_onecore.ps1 で使う）。画面の立場の表示は設定の tags から
VOICES = {"ナレーター": "Haruka"}   # こちら側（C["me"]）は Ichiro、相手は Ayumi


def speaker_label(speaker):
    tag = C["tags"].get(speaker)
    return f"{speaker}｜{tag}" if tag else speaker

# 発言（tts_lines.tsv の行）ごとの場面。カードは場面の頭に無音で出す
SCENES = [
    ("オープニング", None),
    ("冒頭の主張", "冒頭の主張"),
    ("冒頭の主張", None),
    ("第1ラウンド　円安が止まらなかったのはなぜか", "第1ラウンド\n円安が止まらなかったのはなぜか"),
    ("第1ラウンド　円安が止まらなかったのはなぜか", None),
    ("第2ラウンド　「待つリスク」と「上げすぎるリスク」", "第2ラウンド\n「待つリスク」と「上げすぎるリスク」"),
    ("第2ラウンド　「待つリスク」と「上げすぎるリスク」", None),
    ("第3ラウンド　本当の狙いは為替なのか", "第3ラウンド\n本当の狙いは為替なのか"),
    ("第3ラウンド　本当の狙いは為替なのか", None),
    ("最終弁論", "最終弁論"),
    ("最終弁論", None),
    ("エンディング", None),
]

def gachi_scenes(n_turns):
    """ガチ版：ナレーター＋討論の発言＋ナレーター。"""
    cards = scene_names(n_turns)
    out, cur = [("オープニング", None)], ""
    for i in range(1, n_turns + 1):
        if i in cards:
            cur = cards[i]
            out.append((cur, cur))
        else:
            out.append((cur, None))
    out.append(("エンディング", None))
    return out


def from_topic(dir_name, build=None):
    """topic.env のある討論フォルダから、ガチ版の設定を作る。"""
    T = load(dir_name)
    return dict(tsv=f"{dir_name}/tts_lines.tsv", log=f"{dir_name}/log.md", build=build or f"build_{dir_name}",
                name=T["VIDEO"], scenes=gachi_scenes(len(read_log(dir_name))),
                title_sec=2.5, card_sec=1.0, end_sec=4.0, gap_sentence=0.08, gap_speaker=0.3,
                title=(T["TITLE_KICKER"], T["TITLE"].split("｜")), end=T["END"].split("｜"),
                tags={T["OPUS_NAME"]: T["OPUS_TAG"], T["ASTRA_MODEL"]: T["ASTRA_TAG"]},
                me=T["OPUS_NAME"], rival=T["ASTRA_MODEL"],
                credit=f"{T['OPUS_NAME']}：{T['OPUS_CREDIT']} ／ {T['ASTRA_MODEL']}：{T['ASTRA_CREDIT']}")


CONFIGS = {
    "1": dict(tsv="debate/tts_lines.tsv", log=None, build="build", name="boj_debate_0918",
              scenes=SCENES, title_sec=3.0, card_sec=1.5, end_sec=4.0,
              gap_sentence=0.15, gap_speaker=0.5,
              title=("AI vs AI 討論", ["9月18日の日銀利上げは", "正しかったのか？"]),
              end=["答え合わせは", "10月29〜30日の日銀会合"],
              tags={"Opus": "反対", "gpt-6-astra": "賛成"}, me="Opus", rival="gpt-6-astra",
              credit="Opus：Claude Opus 5.5 ／ gpt-6-astra：Codex CLI"),
    "2": from_topic("debate2", build="build2"),
}
# ガチ版のページ表示：音声は 2 と同じもの（build2/audio）を使い、画面だけ変える
CONFIGS["2p"] = dict(CONFIGS["2"], build="build2p", audio="build2/audio",
                     name="boj_debate2_0918_paged", paged=True)
CONFIGS["1p"] = dict(CONFIGS["1"], build="build1p", audio="build/audio",
                     name="boj_debate_0918_paged", paged=True)
C = CONFIGS["1"]


def use(key, paged=False):
    global C, TSV, BUILD, SENTENCES, AUDIO, FRAMES, OUT_MP4, OUT_SRT
    C = CONFIGS.get(key) or from_topic(key.rstrip("/"))
    if paged:
        C = dict(C, build=C["build"] + "p", audio=f"{C['build']}/audio", name=C["name"] + "_paged", paged=True)
    TSV = ROOT / C["tsv"]
    BUILD = ROOT / C["build"]
    SENTENCES, FRAMES = BUILD / "sentences.tsv", BUILD / "frames"
    AUDIO = ROOT / C.get("audio", f"{C['build']}/audio")
    OUT_MP4, OUT_SRT = OUT_DIR / f"{C['name']}.mp4", OUT_DIR / f"{C['name']}.srt"


def display_speeches(speeches):
    """画面に出す文。討論ログがあれば記事の表記をそのまま使い、なければ読み上げ用から戻す。"""
    if not C["log"]:
        return [[to_display(s) for s in sents] for _, sents in speeches]
    turns = [re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", l.split("「", 1)[1][:-1])
             for l in (ROOT / C["log"]).read_text(encoding="utf-8").splitlines()]
    out = []
    for k, (_, sents) in enumerate(speeches):
        if 1 <= k <= len(turns):
            disp = split_sentences(turns[k - 1])
            if len(disp) == len(sents):
                out.append(disp)
                continue
            print(f"warning: 発言{k} の文の数が合わないので、読み上げ用から戻す")
        out.append([to_display(s) for s in sents])
    return out


# 読み上げ用の表記を、画面では記事の表記に戻す（長いものから順に置き換える）
DISPLAY = [
    ("ジーピーティーシックス アストラ", "gpt-6-astra"),
    ("クロード・オーパス", "Claude Opus"),
    ("シーピーアイ", "CPI"),
    ("パーセント", "%"),
    ("うわぶれ", "上振れ"),
    ("エーアイ", "AI"),
]

NO_LINE_START = "、。，．」』）？！%ー"


def split_sentences(text):
    return [s.strip() for s in re.findall(r"[^。？！]+[。？！]?", text) if s.strip()]


def to_display(text):
    for a, b in DISPLAY:
        text = text.replace(a, b)
    return text


def prepare():
    BUILD.mkdir(exist_ok=True)
    rows = []
    for i, line in enumerate(TSV.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        speaker, text = line.split("\t", 1)
        for s in split_sentences(text):
            rows.append(f"{len(rows):03d}\t{VOICES.get(speaker, 'Ichiro' if speaker == C['me'] else 'Ayumi')}\t{s}")
    SENTENCES.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"{len(rows)} sentences -> {SENTENCES}")


# ---------- 画面 ----------

def font(path, size):
    return ImageFont.truetype(path, size, index=0)


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for ch in text:
        if cur and draw.textlength(cur + ch, font=fnt) > max_w and ch not in NO_LINE_START:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def new_canvas():
    img = Image.new("RGB", (W, H), (0, 0, 0))
    return img, ImageDraw.Draw(img)


def centered(draw, lines, fnt, y_center, fill, spacing=1.5):
    size = fnt.size
    total = int(size * spacing * (len(lines) - 1) + size)
    y = y_center - total // 2
    for ln in lines:
        w = draw.textlength(ln, font=fnt)
        draw.text(((W - w) / 2, y), ln, font=fnt, fill=fill)
        y += int(size * spacing)


def frame_title(path):
    img, d = new_canvas()
    kicker, title = C["title"]
    centered(d, [kicker], font(FONT_R, 44), 300, GRAY)
    centered(d, title, font(FONT_B, 96), 520, WHITE)
    tags = C["tags"]
    rival = C["rival"]
    me = C["me"]
    centered(d, [f"{me}（{tags[me]}）　vs　{rival}（{tags[rival]}）"], font(FONT_R, 52), 800, WHITE)
    img.save(path)


def frame_card(path, text):
    img, d = new_canvas()
    lines = text.split("\n")
    centered(d, lines[:1], font(FONT_B, 88), 470 if len(lines) > 1 else 540, WHITE)
    if len(lines) > 1:
        centered(d, lines[1:], font(FONT_R, 60), 610, GRAY)
    img.save(path)


def frame_line(path, scene, speaker_label, sentence):
    img, d = new_canvas()
    d.text((120, 80), scene, font=font(FONT_R, 40), fill=GRAY)
    f_spk = font(FONT_B, 60)
    d.text((120, 260), speaker_label, font=f_spk, fill=WHITE)
    d.line([(120, 350), (1800, 350)], fill=DIM, width=2)
    for size in (76, 68, 60, 54):   # 長い文は文字を小さくして画面に収める
        f_txt = font(FONT_R, size)
        lines = wrap(d, sentence, f_txt, W - 240)
        if 420 + len(lines) * size * 1.55 <= H - 60:
            break
    y = 420
    for ln in lines:
        d.text((120, y), ln, font=f_txt, fill=WHITE)
        y += int(size * 1.55)
    img.save(path)


# ---------- ページ表示（1画面に複数の文、読んでいる文だけ明るく） ----------

PAGE_FONT, PAGE_LH, PAGE_LINES, PAGE_TOP = 56, 1.6, 7, 340
HIGHLIGHT = (255, 210, 0)   # 読み上げ中の文の色（ほかの文は白）
WORD_CHAR = re.compile(r"[0-9A-Za-z０-９.%％\-]")   # 途中で改行しない文字


def flow(draw, sentences, ids, fnt, max_w):
    """文を改行せずに段落として流し、行ごとに (文字, 文の番号) の列を返す。"""
    lines, cur, cur_text = [], [], ""
    for k in ids:
        for ch in sentences[k]:
            if cur and draw.textlength(cur_text + ch, font=fnt) > max_w and ch not in NO_LINE_START:
                # 数字や英単語（1995、1.25%、Claude）の途中では切らず、単語ごと次の行へ送る
                cut = len(cur)
                if WORD_CHAR.match(ch):
                    while cut > 0 and WORD_CHAR.match(cur[cut - 1][0]):
                        cut -= 1
                    if cut == 0:      # 1行より長い単語は、仕方なくそこで切る
                        cut = len(cur)
                lines.append(cur[:cut])
                cur = cur[cut:]
                cur_text = "".join(c for c, _ in cur)
            cur.append((ch, k))
            cur_text += ch
    if cur:
        lines.append(cur)
    return lines


def paginate(sentences):
    """1発言の文を、PAGE_LINES 行に収まる単位でページに分ける。"""
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    fnt = font(FONT_R, PAGE_FONT)
    pages, cur = [], []
    for j in range(len(sentences)):
        if cur and len(flow(d, sentences, cur + [j], fnt, W - 240)) > PAGE_LINES:
            pages.append(cur)
            cur = []
        cur.append(j)
    if cur:
        pages.append(cur)
    # 後ろのページが極端に短くならないよう、前のページの最後の文を送ってならす
    fits = lambda ids: len(flow(d, sentences, ids, fnt, W - 240)) <= PAGE_LINES
    for i in range(len(pages) - 1, 0, -1):
        while len(pages[i]) + 1 < len(pages[i - 1]) and fits([pages[i - 1][-1]] + pages[i]):
            pages[i].insert(0, pages[i - 1].pop())
    return pages


def frame_page(path, scene, speaker_label, sentences, ids, active, page_no, n_pages):
    img, d = new_canvas()
    d.text((120, 80), scene, font=font(FONT_R, 40), fill=GRAY)
    if n_pages > 1:
        f_no = font(FONT_R, 40)
        no = f"{page_no}/{n_pages}"
        d.text((W - 120 - d.textlength(no, font=f_no), 80), no, font=f_no, fill=GRAY)
    d.text((120, 180), speaker_label, font=font(FONT_B, 60), fill=WHITE)
    d.line([(120, 270), (1800, 270)], fill=DIM, width=2)
    fnt = font(FONT_R, PAGE_FONT)
    y = PAGE_TOP
    for line in flow(d, sentences, ids, fnt, W - 240):
        x = 120
        run, run_k = "", line[0][1]
        for ch, k in line + [("", None)]:   # 番号が変わるところで色を切り替えて描く
            if k != run_k:
                d.text((x, y), run, font=fnt, fill=HIGHLIGHT if run_k == active else WHITE)
                x += d.textlength(run, font=fnt)
                run, run_k = "", k
            run += ch
        y += int(PAGE_FONT * PAGE_LH)
    img.save(path)


def frame_end(path):
    img, d = new_canvas()
    centered(d, C["end"], font(FONT_B, 84 if len(C["end"]) <= 2 else 72), 400, WHITE)
    centered(d, [C["credit"],
                 "音声：Windows 音声合成（Haruka・Ichiro・Ayumi）"], font(FONT_R, 40), 800, GRAY)
    img.save(path)


# ---------- 結合 ----------

def trim_silence(data, params, threshold=200, margin=0.04):
    """音声合成が前後に付ける無音を削る（16bit モノラル前提）。"""
    import array
    a = array.array("h", data)
    first = next((i for i, v in enumerate(a) if abs(v) > threshold), 0)
    last = next((i for i in range(len(a) - 1, -1, -1) if abs(a[i]) > threshold), len(a) - 1)
    pad = int(margin * params.framerate)
    return a[max(0, first - pad):min(len(a), last + pad)].tobytes()


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def render():
    FRAMES.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(exist_ok=True)

    speeches = []
    for line in TSV.read_text(encoding="utf-8").splitlines():
        if line.strip():
            speaker, text = line.split("\t", 1)
            speeches.append((speaker, split_sentences(text)))
    assert len(speeches) == len(C["scenes"]), "tts_lines.tsv の発言数と場面の数が合わない"
    displays = display_speeches(speeches)
    TITLE_SEC, CARD_SEC, END_SEC = C["title_sec"], C["card_sec"], C["end_sec"]
    GAP_SENTENCE, GAP_SPEAKER = C["gap_sentence"], C["gap_speaker"]

    params, chunks = None, []   # 音声データを順につなぐ
    timeline = []               # (画像, 開始秒, 終了秒, 字幕)
    t = 0.0

    def add_silence(sec):
        nonlocal t
        n = int(round(sec * params.framerate))
        chunks.append(b"\x00" * n * params.sampwidth * params.nchannels)
        t += n / params.framerate

    # 音声の形式を先に読む
    with wave.open(str(AUDIO / "000.wav")) as w:
        params = w.getparams()

    p = FRAMES / "title.png"
    frame_title(p)
    timeline.append((p, t, t + TITLE_SEC, None))
    add_silence(TITLE_SEC)

    idx, prev, page_sizes = 0, None, []
    for k, ((speaker, sentences), (scene, card)) in enumerate(zip(speeches, C["scenes"])):
        if card:
            p = FRAMES / f"card{k:02d}.png"
            frame_card(p, card)
            timeline.append((p, t, t + CARD_SEC, None))
            add_silence(CARD_SEC)
        elif prev is not None:
            add_silence(GAP_SPEAKER)
        label = speaker_label(speaker)
        pages = paginate(displays[k]) if C.get("paged") else None
        if pages:
            page_sizes.append([len(pg) for pg in pages])
        for j, s in enumerate(sentences):
            if j:
                add_silence(GAP_SENTENCE)
            with wave.open(str(AUDIO / f"{idx:03d}.wav")) as w:
                if w.getparams()[:3] != params[:3]:
                    sys.exit(f"{idx:03d}.wav の形式が違う")
                data = trim_silence(w.readframes(w.getnframes()), params)
            disp = displays[k][j]
            p = FRAMES / f"{idx:03d}.png"
            if pages:
                no = next(n for n, pg in enumerate(pages) if j in pg)
                frame_page(p, scene, label, displays[k], pages[no], j, no + 1, len(pages))
            else:
                frame_line(p, scene, label, disp)
            start = t
            chunks.append(data)
            t += len(data) / (params.sampwidth * params.nchannels) / params.framerate
            timeline.append((p, start, t, disp))
            idx += 1
        prev = speaker

    add_silence(0.5)
    p = FRAMES / "end.png"
    frame_end(p)
    timeline.append((p, t, t + END_SEC, None))
    add_silence(END_SEC)

    audio_path = BUILD / "audio_all.wav"
    with wave.open(str(audio_path), "wb") as w:
        w.setparams(params)
        w.writeframes(b"".join(chunks))

    # 字幕と画面の切り替えを同じ境界にするため、各区間の終わりまで画像を表示する
    # （無音の間は直前の画像のまま）。境界はフレーム単位に丸めてずれをためない
    bounds = [tl[1] for tl in timeline] + [t]
    frames_at = [round(b * FPS) for b in bounds]
    lines = []
    for (img, *_), f0, f1 in zip(timeline, frames_at, frames_at[1:]):
        lines += [f"file '{img.as_posix()}'", f"duration {(f1 - f0) / FPS:.6f}"]
    lines.append(f"file '{timeline[-1][0].as_posix()}'")
    concat = BUILD / "frames.txt"
    concat.write_text("\n".join(lines) + "\n", encoding="utf-8")

    srt, n = [], 0
    for _, s0, s1, text in timeline:
        if text:
            n += 1
            srt += [str(n), f"{srt_time(s0)} --> {srt_time(s1)}", text, ""]
    OUT_SRT.write_text("\n".join(srt), encoding="utf-8")

    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat),
        "-i", str(audio_path),
        "-vf", f"fps={FPS},format=yuv420p",
        "-c:v", "libx264", "-tune", "stillimage", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
        str(OUT_MP4),
    ], check=True)
    if page_sizes:
        flat = [n for sizes in page_sizes for n in sizes]
        print(f"{len(flat)} pages, sentences per page: min {min(flat)} / max {max(flat)} / "
              f"avg {sum(flat) / len(flat):.1f}")
    print(f"{idx} sentences, {t:.1f} sec -> {OUT_MP4}")


if __name__ == "__main__":
    use(sys.argv[2] if len(sys.argv) > 2 else "1", paged=sys.argv[3:4] == ["paged"])
    {"prepare": prepare, "render": render}[sys.argv[1]]()
