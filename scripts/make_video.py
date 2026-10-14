"""討論動画を作る。

  uv run --with pillow python scripts/make_video.py prepare   # 1文ずつの読み上げリストを作る
  powershell -File scripts/tts_onecore.ps1 ...                 # 1文ずつ WAV を作る
  uv run --with pillow python scripts/make_video.py render    # 画面を作り、音声と結合する
"""
import re
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
TSV = ROOT / "debate" / "tts_lines.tsv"
BUILD = ROOT / "build"
SENTENCES = BUILD / "sentences.tsv"
AUDIO = BUILD / "audio"
FRAMES = BUILD / "frames"
OUT_DIR = ROOT / "video"
OUT_MP4 = OUT_DIR / "boj_debate_0918.mp4"
OUT_SRT = OUT_DIR / "boj_debate_0918.srt"

W, H, FPS = 1920, 1080, 30
FONT_R = r"C:\Windows\Fonts\BIZ-UDGothicR.ttc"
FONT_B = r"C:\Windows\Fonts\BIZ-UDGothicB.ttc"
WHITE, GRAY, DIM = (255, 255, 255), (150, 150, 150), (90, 90, 90)

TITLE_SEC, CARD_SEC, END_SEC = 3.0, 1.5, 4.0
GAP_SENTENCE, GAP_SPEAKER = 0.15, 0.5

# 話者ごとの声と画面表示（声の名前は tts_onecore.ps1 で使う）
SPEAKERS = {
    "ナレーター": ("Haruka", "ナレーター"),
    "Opus": ("Ichiro", "Opus｜反対"),
    "gpt-6-astra": ("Ayumi", "gpt-6-astra｜賛成"),
}

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
            rows.append(f"{len(rows):03d}\t{SPEAKERS[speaker][0]}\t{s}")
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
    centered(d, ["AI vs AI 討論"], font(FONT_R, 44), 300, GRAY)
    centered(d, ["9月18日の日銀利上げは", "正しかったのか？"], font(FONT_B, 96), 520, WHITE)
    centered(d, ["Opus（反対）　vs　gpt-6-astra（賛成）"], font(FONT_R, 52), 800, WHITE)
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
    f_txt = font(FONT_R, 76)
    y = 420
    for ln in wrap(d, sentence, f_txt, W - 240):
        d.text((120, y), ln, font=f_txt, fill=WHITE)
        y += int(76 * 1.55)
    img.save(path)


def frame_end(path):
    img, d = new_canvas()
    centered(d, ["答え合わせは", "10月29〜30日の日銀会合"], font(FONT_B, 84), 400, WHITE)
    centered(d, ["Opus：Claude Opus 5.5 ／ gpt-6-astra：Codex CLI",
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
    assert len(speeches) == len(SCENES), "tts_lines.tsv の発言数と SCENES の数が合わない"

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

    idx, prev = 0, None
    for k, ((speaker, sentences), (scene, card)) in enumerate(zip(speeches, SCENES)):
        if card:
            p = FRAMES / f"card{k:02d}.png"
            frame_card(p, card)
            timeline.append((p, t, t + CARD_SEC, None))
            add_silence(CARD_SEC)
        elif prev is not None:
            add_silence(GAP_SPEAKER)
        label = SPEAKERS[speaker][1]
        for j, s in enumerate(sentences):
            if j:
                add_silence(GAP_SENTENCE)
            with wave.open(str(AUDIO / f"{idx:03d}.wav")) as w:
                if w.getparams()[:3] != params[:3]:
                    sys.exit(f"{idx:03d}.wav の形式が違う")
                data = trim_silence(w.readframes(w.getnframes()), params)
            disp = to_display(s)
            p = FRAMES / f"{idx:03d}.png"
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
    print(f"{idx} sentences, {t:.1f} sec -> {OUT_MP4}")


if __name__ == "__main__":
    {"prepare": prepare, "render": render}[sys.argv[1]]()
