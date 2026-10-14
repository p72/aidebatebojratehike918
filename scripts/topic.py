"""討論フォルダの topic.env（議題・立場・タイトルなど）を読む。

topic.env は bash からも `source` できるよう、1行に KEY='値' の形で書く。
画面やタイトルで改行したいところは「｜」で区切る。
"""
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(dir_name):
    d = ROOT / dir_name
    env = {}
    for line in (d / "topic.env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        env[key] = shlex.split(value)[0] if value else ""
    env["DIR"] = d
    # 相手のモデル名（話者名にも使う）と、その読み
    env.setdefault("ASTRA_MODEL", "gpt-6-astra")
    # こちら側（Claude）の話者名。Opus どうしの討論では Opus-A などに変える
    env.setdefault("OPUS_NAME", "Opus")
    # 最後の画面に出す、それぞれの作り方
    env.setdefault("OPUS_CREDIT", "Claude Opus 5.5")
    env.setdefault("ASTRA_CREDIT", "Codex CLI")
    env.setdefault("ASTRA_READING", "ジーピーティーシックス アストラ")
    env["TELOPS"] = read_tsv(d / "telops.tsv", int)
    env["READINGS"] = list(read_tsv(d / "readings.tsv").items())
    return env


def read_tsv(path, key_type=str):
    """「キー<TAB>値」の TSV を辞書で返す。ファイルがなければ空。"""
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            k, v = line.split("\t", 1)
            out[key_type(k)] = v
    return out


def scene_names(n_turns):
    """発言の番号 → 場面名。1が冒頭の主張、最後の往復が最終弁論、その間がラウンド。"""
    out = {1: "冒頭の主張", n_turns - 1: "最終弁論"}
    for i in range(3, n_turns - 1, 2):
        out[i] = f"第{(i - 1) // 2}ラウンド"
    return out


def read_log(dir_name):
    """討論ログを (話者, セリフ) の列で返す。行の形は 話者「セリフ」。"""
    turns = []
    for line in (ROOT / dir_name / "log.md").read_text(encoding="utf-8").splitlines():
        if line.strip():
            speaker, text = line.split("「", 1)
            turns.append((speaker, text[:-1]))
    return turns
