"""Build Anki packages (.apkg) from the JSON files in data/.

Usage: python scripts/build.py
Output: dist/English-Vocabulary.apkg, dist/English-Collocations.apkg,
        dist/Chinese-Chengyu.apkg

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

COLLOCATION_MODEL = genanki.Model(
    1735200003,
    "English Collocation",
    fields=[{"name": n} for n in ("Collocation", "Meaning", "Usage", "Examples")],
    templates=[{
        "name": "Recognition",
        "qfmt": '<div class="head"><span class="term colloc">{{Collocation}}</span></div>',
        "afmt": (
            '{{FrontSide}}<hr id="answer">'
            '<div class="label">Meaning</div><div>{{Meaning}}</div>'
            '<div class="label">Usage</div><div>{{Usage}}</div>'
            '<div class="label">Examples</div>{{Examples}}'
        ),
    }],
    css=BASE_CSS + ".term.colloc { font-size: 32px; }",
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


# Function words that are not highlighted or required in collocation examples.
STOPWORDS = set("""a an the to of in on at for with by from into up out off your you
someone someone's something it and or as be""".split())

IRREGULAR = {
    "make": "made", "take": "took taken", "do": "did done does", "have": "has had",
    "get": "got gotten", "keep": "kept", "break": "broke broken", "catch": "caught",
    "pay": "paid", "run": "ran", "come": "came", "go": "went gone goes", "tell": "told",
    "say": "said", "lose": "lost", "feel": "felt", "draw": "drew drawn", "stand": "stood",
    "hold": "held", "throw": "threw thrown", "bear": "bore borne", "give": "gave given",
    "meet": "met", "sleep": "slept", "ring": "rang rung", "blow": "blew blown",
    "fall": "fell fallen", "spend": "spent", "lend": "lent", "win": "won", "lead": "led",
    "build": "built", "lay": "laid", "strike": "struck", "seek": "sought",
    "bring": "brought", "think": "thought", "sell": "sold", "deal": "dealt",
    "leave": "left", "write": "wrote written", "rise": "rose risen", "grow": "grew grown",
    "know": "knew known", "sit": "sat", "find": "found", "shed": "shed", "lie": "lay lain",
    "undertake": "undertook undertaken", "withstand": "withstood", "wake": "woke woken",
    "eat": "ate eaten", "teach": "taught", "buy": "bought", "fight": "fought",
    "criterion": "criteria", "phenomenon": "phenomena", "hypothesis": "hypotheses",
    "uphold": "upheld", "oversee": "oversaw overseen", "withhold": "withheld",
}


def word_forms(word):
    """Regex alternatives for a word and its inflections, including irregular verbs."""
    if word.endswith("ing"):
        stem = word[:-3]
    elif word[-1] in "ey" and len(word) > 3:
        stem = word[:-1]
    else:
        stem = word
    forms = [re.escape(stem) + r"\w*"] + [re.escape(f) for f in IRREGULAR.get(word, "").split()]
    return "|".join(forms)


def target_pattern(word):
    """Match a headword and its inflected forms: cope/coping, imply/implied."""
    return re.compile(r"\b(?:" + word_forms(word) + r")\b", re.IGNORECASE)


def collocation_words(colloc):
    """Content words of a collocation, e.g. 'make a decision' -> ['make', 'decision']."""
    return [w for w in re.findall(r"[a-z'-]+", colloc.lower()) if w not in STOPWORDS]


def collocation_patterns(colloc):
    return [target_pattern(w) for w in collocation_words(colloc)]


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
            tags=[c["level"]] if c.get("level") else [],
        )


def collocation_notes(cards):
    for c in cards:
        term = c["collocation"]
        pat = re.compile("|".join(p.pattern for p in collocation_patterns(term)), re.IGNORECASE)
        examples = "".join(f"<li>{bold(e, pat)}</li>" for e in c["examples"])
        yield genanki.Note(
            model=COLLOCATION_MODEL,
            fields=[html.escape(term), para(c["meaning"]), para(c["usage"]),
                    f'<ol class="ex">{examples}</ol>'],
            guid=genanki.guid_for("collocation", term),
            tags=[c["domain"]],
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
    build(1735200103, "English Collocations — Academic, Business & Everyday",
          "collocations.json", collocation_notes, "English-Collocations.apkg")
    build(1735200102, "常用成语", "chengyu.json", chengyu_notes, "Chinese-Chengyu.apkg")
