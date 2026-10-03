"""Validate deck data before building.

Checks structure, the monolingual rules in CONTENT_GUIDELINES.md, pinyin
(against pypinyin) and IPA stress/syllable count (against the CMU dictionary).
Pinyin and IPA differences are printed for manual review: the reference
dictionaries are American (CMU) or context-blind (pypinyin), so a difference
is not automatically an error.

Notes listed in scripts/reviewed.txt were verified by hand and are not shown.

Usage: python scripts/check.py [english|collocations|chengyu] [--strict]
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

import pronouncing
from pypinyin import Style, pinyin

from build import collocation_patterns, target_pattern

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
# Review notes already checked by hand and confirmed correct (one per line).
REVIEWED = Path(__file__).resolve().parent / "reviewed.txt"

MIN_EXAMPLES, MAX_EXAMPLES = 4, 6

CJK = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
LATIN = re.compile(r"[A-Za-z]")
# Vietnamese-only letters plus the Latin Extended Additional block (ạ, ả, ấ, ...).
VIETNAMESE = re.compile(r"[ăâđêôơưĂÂĐÊÔƠƯ\u1ea0-\u1ef9]")
TONE_MARKS = {"\u0304": 1, "\u0301": 2, "\u030c": 3, "\u0300": 4}
# Common traditional-only characters (simplified forms differ).
TRADITIONAL = re.compile("[問題說這們時個會學國來對過還為麼裡後經實現發開關見長樣種點讓應話認聽寫讀給從]")


class Report:
    def __init__(self):
        self.errors = []
        self.reviews = []

    def error(self, key, msg):
        self.errors.append(f"[{key}] {msg}")

    def review(self, key, msg):
        self.reviews.append(f"[{key}] {msg}")


# ---------------------------------------------------------------- English

IPA_DIPHTHONGS = ("eɪ", "aɪ", "ɔɪ", "əʊ", "aʊ", "ɪə", "eə", "ʊə")
IPA_VOWELS = set("iɪeæɑɒɔʊuʌɜəaoɛ")
CMU_PRIMARY = re.compile(r"[A-Z]+1")


def ipa_nuclei(ipa):
    """Return (syllable count, index of primary-stressed syllable)."""
    s = ipa.strip("/").replace("ː", "")
    count, primary, i = 0, None, 0
    prev_consonant = False
    while i < len(s):
        ch = s[i]
        if ch == "ˈ":
            primary = count
            i += 1
            continue
        if ch == "ˌ" or ch in "() ":
            i += 1
            continue
        if s[i:i + 2] in IPA_DIPHTHONGS:
            count += 1
            i += 2
            prev_consonant = False
            continue
        if ch in IPA_VOWELS:
            count += 1
            prev_consonant = False
        else:
            # Syllabic l/n/m after a consonant, as in /ˈveəriəbl/ or /ˈneɪʃn/.
            nxt = s[i + 1] if i + 1 < len(s) else ""
            if ch in "lnm" and prev_consonant and (not nxt or nxt not in IPA_VOWELS):
                count += 1
            prev_consonant = True
        i += 1
    return count, primary


def cmu_variants(word):
    out = []
    for phones in pronouncing.phones_for_word(word.lower()):
        vowels = [p for p in phones.split() if p[-1].isdigit()]
        primary = next((i for i, p in enumerate(vowels) if p.endswith("1")), None)
        out.append((len(vowels), primary))
    return out


def check_english(cards, rep):
    seen = set()
    for card in cards:
        key = card.get("word", "?")
        for field in ("word", "ipa", "definition", "usage", "examples"):
            if not card.get(field):
                rep.error(key, f"missing field '{field}'")
        if key in seen:
            rep.error(key, "duplicate word")
        seen.add(key)

        if card.get("level") not in (None, "C1", "C2"):
            rep.error(key, f"level must be C1 or C2: {card.get('level')}")

        examples = card.get("examples", [])
        if not MIN_EXAMPLES <= len(examples) <= MAX_EXAMPLES:
            rep.error(key, f"{len(examples)} examples (need {MIN_EXAMPLES}-{MAX_EXAMPLES})")
        pat = target_pattern(key)
        for n, ex in enumerate(examples, 1):
            if not pat.search(ex):
                rep.review(key, f"example {n} may not contain the target word: {ex}")

        text = " ".join([card.get("definition", ""), card.get("usage", "")] + examples)
        if CJK.search(text):
            rep.error(key, "Chinese characters in English content")
        if VIETNAMESE.search(text):
            rep.error(key, "Vietnamese letters in English content")

        ipa = card.get("ipa", "")
        if not (ipa.startswith("/") and ipa.endswith("/")):
            rep.error(key, f"IPA must be wrapped in slashes: {ipa}")
        if re.search(r"[':]", ipa):
            rep.error(key, f"use ˈ ˌ ː, not ASCII ' or : in IPA: {ipa}")
        if "ˈ" not in ipa and ipa_nuclei(ipa)[0] > 1:
            rep.error(key, f"no primary stress mark: {ipa}")

        variants = cmu_variants(key)
        if not variants:
            rep.review(key, f"not in CMU dict, check IPA by hand: {ipa}")
            continue
        count, primary = ipa_nuclei(ipa)
        if count == 1:
            primary = 0
        if not any(p == primary for _, p in variants):
            rep.review(key, f"primary stress on syllable {primary}, CMU says "
                            f"{sorted({p for _, p in variants})}: {ipa}")
        if not any(c == count for c, _ in variants):
            rep.review(key, f"{count} syllables, CMU says "
                            f"{sorted({c for c, _ in variants})}: {ipa}")


# ---------------------------------------------------------------- Collocations

DOMAINS = ("academic", "business", "everyday")


def check_collocations(cards, rep):
    seen = set()
    for card in cards:
        key = card.get("collocation", "?")
        for field in ("collocation", "domain", "meaning", "usage", "examples"):
            if not card.get(field):
                rep.error(key, f"missing field '{field}'")
        if key.lower() in seen:
            rep.error(key, "duplicate collocation")
        seen.add(key.lower())
        if card.get("domain") not in DOMAINS:
            rep.error(key, f"domain must be one of {DOMAINS}")

        examples = card.get("examples", [])
        if not MIN_EXAMPLES <= len(examples) <= MAX_EXAMPLES:
            rep.error(key, f"{len(examples)} examples (need {MIN_EXAMPLES}-{MAX_EXAMPLES})")
        pats = collocation_patterns(key)
        for n, ex in enumerate(examples, 1):
            missing = [p.pattern for p in pats if not p.search(ex)]
            if missing:
                rep.review(key, f"example {n} may not contain the collocation: {ex}")

        text = " ".join([card.get("meaning", ""), card.get("usage", "")] + examples)
        if CJK.search(text):
            rep.error(key, "Chinese characters in English content")
        if VIETNAMESE.search(text):
            rep.error(key, "Vietnamese letters in English content")


# ---------------------------------------------------------------- Chinese

def split_tone(syl):
    """'zhōng' -> ('zhong', 1); 'de' -> ('de', 0). Keeps ü."""
    tone = 0
    out = []
    for ch in unicodedata.normalize("NFD", syl):
        if ch in TONE_MARKS:
            tone = TONE_MARKS[ch]
        else:
            out.append(ch)
    return unicodedata.normalize("NFC", "".join(out)).lower(), tone


def expected_syllables(zh):
    """Per-character readings: (primary toned reading, all toned readings)."""
    hanzi = [c for c in zh if CJK.match(c)]
    text = "".join(hanzi)
    primary = [p[0] for p in pinyin(text, style=Style.TONE, errors="ignore")]
    alts = [set(pinyin(c, style=Style.TONE, heteronym=True)[0]) for c in hanzi]
    if len(primary) != len(hanzi):
        return None
    # Apply 一/不 tone sandhi as written in the guidelines' examples.
    for i, c in enumerate(hanzi):
        if c not in "一不" or i + 1 >= len(hanzi):
            continue
        _, next_tone = split_tone(primary[i + 1])
        if c == "不":
            primary[i] = "bú" if next_tone == 4 else "bù"
        elif primary[i] == "yī" and next_tone:
            primary[i] = "yí" if next_tone == 4 else "yì"
    return list(zip(hanzi, primary, alts))


def strip_tones_keep_len(s):
    return "".join(split_tone(ch)[0] if ch.isalpha() else ch for ch in s)


def check_pinyin(key, label, zh, py, rep):
    exp = expected_syllables(zh)
    if exp is None:
        rep.error(key, f"{label}: could not read characters: {zh}")
        return
    toned = "".join(ch for ch in unicodedata.normalize("NFC", py).lower()
                    if ch.isalpha())
    plain = strip_tones_keep_len(toned)
    pos = 0
    for hz, prim, alts in exp:
        cands = sorted({split_tone(a)[0] for a in alts} | {split_tone(prim)[0]},
                       key=len, reverse=True)
        match = next((c for c in cands if plain.startswith(c, pos)), None)
        if match is None:
            rep.error(key, f"{label}: pinyin diverges at '{hz}' "
                           f"(expected {prim}, got '{toned[pos:pos + 8]}…'): {py}")
            return
        mine = toned[pos:pos + len(match)]
        pos += len(match)
        _, my_tone = split_tone(mine)
        if my_tone == 0:
            continue  # neutral tone; pypinyin does not mark these
        if mine == prim:
            continue
        if hz in "一不":
            rep.review(key, f"{label}: '{hz}' written {mine}, rule gives {prim}: {zh}")
        elif mine in alts:
            rep.review(key, f"{label}: polyphone '{hz}' written {mine}, "
                            f"pypinyin prefers {prim}: {zh}")
        else:
            rep.review(key, f"{label}: '{hz}' written {mine}, expected {prim}: {zh}")
    if pos != len(plain):
        rep.error(key, f"{label}: extra pinyin '{toned[pos:]}': {py}")


def check_chengyu(cards, rep):
    seen = set()
    for card in cards:
        key = card.get("成语", "?")
        for field in ("成语", "拼音", "释义", "用法", "例句"):
            if not card.get(field):
                rep.error(key, f"missing field '{field}'")
        if key in seen:
            rep.error(key, "duplicate 成语")
        seen.add(key)

        check_pinyin(key, "拼音", key, card.get("拼音", ""), rep)

        examples = card.get("例句", [])
        if not MIN_EXAMPLES <= len(examples) <= MAX_EXAMPLES:
            rep.error(key, f"{len(examples)} 例句 (need {MIN_EXAMPLES}-{MAX_EXAMPLES})")
        for n, ex in enumerate(examples, 1):
            zh, py = ex.get("zh", ""), ex.get("py", "")
            if key not in zh:
                rep.review(key, f"例句{n} does not contain {key}: {zh}")
            if LATIN.search(zh) or re.search(r"\d", zh):
                rep.error(key, f"例句{n} has Latin letters or digits: {zh}")
            if CJK.search(py):
                rep.error(key, f"例句{n} pinyin contains characters: {py}")
            check_pinyin(key, f"例句{n}", zh, py, rep)

        prose = card.get("释义", "") + card.get("用法", "")
        if LATIN.search(prose):
            rep.error(key, "Latin letters in 释义/用法")
        if VIETNAMESE.search(prose + "".join(e.get("py", "") for e in examples)):
            rep.error(key, "Vietnamese letters in content")
        trad = TRADITIONAL.findall(key + prose + "".join(e.get("zh", "") for e in examples))
        if trad:
            rep.error(key, f"traditional characters {''.join(sorted(set(trad)))}; use simplified")


# ---------------------------------------------------------------- main

DECKS = {"english": check_english, "collocations": check_collocations,
         "chengyu": check_chengyu}


def main(argv):
    strict = "--strict" in argv
    reviewed = set(REVIEWED.read_text(encoding="utf-8").splitlines()) if REVIEWED.exists() else set()
    names = [a for a in argv if not a.startswith("--")] or list(DECKS)
    failed = False
    for name in names:
        cards = json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))
        rep = Report()
        DECKS[name](cards, rep)
        new = [r for r in rep.reviews if r not in reviewed]
        print(f"== {name}: {len(cards)} cards, {len(rep.errors)} errors, "
              f"{len(new)} to review ({len(rep.reviews) - len(new)} already reviewed)")
        for line in rep.errors:
            print("ERROR  ", line)
        for line in new:
            print("REVIEW ", line)
        failed |= bool(rep.errors) or (strict and bool(new))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
