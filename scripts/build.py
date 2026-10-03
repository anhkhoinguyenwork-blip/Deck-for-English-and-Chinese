"""Build Anki packages (.apkg) from the JSON files in data/.

Usage: python scripts/build.py
Output: dist/English-Vocabulary.apkg, dist/Chinese-Chengyu.apkg

Model, deck and note IDs are fixed, so re-importing an updated package
updates existing notes instead of creating duplicates, and keeps review history.
"""

import html
import json
import re
from pathlib import Path

import genanki

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DIST = ROOT / "dist"

BASE_CSS = """
.card {
  font-family: -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial,
               "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  font-size: 18px; line-height: 1.6; text-align: left;
  color: #1f2328; background: #ffffff;
  max-width: 680px; margin: 0 auto; padding: 12px 16px;
}
.nightMode.card, .night_mode .card { color: #e6e6e6; background: #1e1e1e; }
.head { text-align: center; margin: 12px 0 4px; }
.term { font-size: 40px; font-weight: 700; letter-spacing: .02em; }
.pron { text-align: center; font-size: 20px; color: #57606a; margin-bottom: 8px; }
.nightMode .pron, .night_mode .pron { color: #a0a8b0; }
hr#answer { border: none; border-top: 1px solid #d0d7de; margin: 16px 0; }
.label {
  font-size: 13px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .08em; color: #8250df; margin: 18px 0 4px;
}
.nightMode .label, .night_mode .label { color: #c297ff; }
.ex { padding-left: 1.4em; margin: 4px 0; }
.ex li { margin-bottom: 8px; }
.ex b { color: #0969da; font-weight: 600; }
.nightMode .ex b, .night_mode .ex b { color: #58a6ff; }
.py { font-size: 15px; color: #6e7781; }
.nightMode .py, .night_mode .py { color: #9aa4ae; }
"""

ZH_CSS = """
.card { font-size: 19px; }
.term { font-size: 46px; letter-spacing: .12em; }
.label { text-transform: none; letter-spacing: .2em; }
"""

ENGLISH_MODEL = genanki.Model(
    1735200001,
    "English Vocabulary",
    fields=[{"name": n} for n in ("Word", "IPA", "Definition", "Usage", "Examples")],
    templates=[{
        "name": "Recognition",
        "qfmt": '<div class="head"><span class="term">{{Word}}</span></div>',
        "afmt": (
            '{{FrontSide}}<div class="pron">{{IPA}}</div><hr id="answer">'
            '<div class="label">Definition</div><div>{{Definition}}</div>'
            '<div class="label">Usage</div><div>{{Usage}}</div>'
            '<div class="label">Examples</div>{{Examples}}'
        ),
    }],
    css=BASE_CSS,
    sort_field_index=0,
)

CHENGYU_MODEL = genanki.Model(
    1735200002,
    "汉语成语",
    fields=[{"name": n} for n in ("成语", "拼音", "释义", "用法", "例句")],
    templates=[{
        "name": "认读",
        "qfmt": '<div class="head"><span class="term">{{成语}}</span></div>',
        "afmt": (
            '{{FrontSide}}<div class="pron">{{拼音}}</div><hr id="answer">'
            '<div class="label">释义</div><div>{{释义}}</div>'
            '<div class="label">用法</div><div>{{用法}}</div>'
            '<div class="label">例句</div>{{例句}}'
        ),
    }],
    css=BASE_CSS + ZH_CSS,
    sort_field_index=0,
)


def para(text):
    return html.escape(text).replace("\n", "<br>")


def bold(text, pattern):
    return pattern.sub(lambda m: f"<b>{m.group(0)}</b>", html.escape(text))


def target_pattern(word):
    """Match a headword and its inflected forms: cope/coping, imply/implied."""
    if word.endswith("ing"):
        stem = word[:-3]
    elif word[-1] in "ey" and len(word) > 3:
        stem = word[:-1]
    else:
        stem = word
    return re.compile(r"\b" + re.escape(stem) + r"\w*", re.IGNORECASE)


def english_notes(cards):
    for c in cards:
        word = c["word"]
        pat = target_pattern(word)
        examples = "".join(f"<li>{bold(e, pat)}</li>" for e in c["examples"])
        yield genanki.Note(
            model=ENGLISH_MODEL,
            fields=[html.escape(word), html.escape(c["ipa"]), para(c["definition"]),
                    para(c["usage"]), f'<ol class="ex">{examples}</ol>'],
            guid=genanki.guid_for("english", word),
        )


def chengyu_notes(cards):
    for c in cards:
        term = c["成语"]
        pat = re.compile(re.escape(term))
        examples = "".join(
            f'<li><div>{bold(e["zh"], pat)}</div><div class="py">{html.escape(e["py"])}</div></li>'
            for e in c["例句"]
        )
        yield genanki.Note(
            model=CHENGYU_MODEL,
            fields=[term, html.escape(c["拼音"]), para(c["释义"]), para(c["用法"]),
                    f'<ol class="ex">{examples}</ol>'],
            guid=genanki.guid_for("chengyu", term),
        )


def build(deck_id, deck_name, data_file, notes, out_file):
    cards = json.loads((DATA / data_file).read_text(encoding="utf-8"))
    deck = genanki.Deck(deck_id, deck_name)
    for note in notes(cards):
        deck.add_note(note)
    DIST.mkdir(exist_ok=True)
    genanki.Package(deck).write_to_file(DIST / out_file)
    print(f"{out_file}: {len(cards)} cards")


if __name__ == "__main__":
    build(1735200101, "English Vocabulary — Academic & Everyday", "english.json",
          english_notes, "English-Vocabulary.apkg")
    build(1735200102, "常用成语", "chengyu.json", chengyu_notes, "Chinese-Chengyu.apkg")
