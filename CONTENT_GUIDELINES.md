# Content Guidelines

Rules for writing card content in the English decks (vocabulary and collocations)
and the Chinese 成语 deck.

## Language of explanations

**Keep each deck internally monolingual.**

### English deck

- All definitions and explanations are written in natural English.
- Do **not** explain English vocabulary in Vietnamese or Chinese.
- Use English for:
  - definitions
  - usage notes
  - register notes
  - nuance
  - collocation explanations
  - example sentences
  - synonym/antonym explanations
- IPA is required.
- If the schema has a Vietnamese translation field, keep it only if the field is
  structurally required. The vocabulary explanation itself must still be in English.

Example:

```
WORD: reluctant
IPA: /rɪˈlʌktənt/

Definition:
Not willing or eager to do something, usually because you are uncertain,
uncomfortable, or have doubts about it.

Usage:
Often followed by "to + verb".

Examples:
1. I was reluctant to go at first, but I'm glad I did.
2. She was reluctant to accept the offer because of the long commute.
3. He's usually reluctant to talk about his personal life.
4. The company was reluctant to invest more money without seeing better results.
```

### Chinese 成语 deck

- All definitions and explanations are written in natural Mandarin Chinese.
- Do **not** explain 成语 in Vietnamese or English.
- Use Chinese for:
  - meaning/definition (释义)
  - usage notes (用法)
  - register notes
  - nuance
  - explanations
  - example sentences (例句)
- Pinyin is required.
- Do **not** add Vietnamese or English translations unless the schema explicitly
  requires them.
- The explanations must read as if written for a native Chinese learner or student,
  not translated from English or Vietnamese.

Example:

```
成语：三分钟热度
拼音：sān fēnzhōng rèdù

释义：
形容刚开始做一件事情的时候非常积极、热情，
但是坚持不了多久，很快就失去了兴趣。

用法：
通常用来形容一个人做事情缺乏耐心和持续性，
常带有轻微的批评意味。

例句：
1. 我以前学过很多东西，但总是三分钟热度。
   Wǒ yǐqián xuéguo hěn duō dōngxi, dàn zǒng shì sān fēnzhōng rèdù.

2. 他学英语最大的问题就是三分钟热度。
   Tā xué Yīngyǔ zuì dà de wèntí jiùshì sān fēnzhōng rèdù.

3. 如果你只是三分钟热度，很难真正掌握一门语言。
   Rúguǒ nǐ zhǐshì sān fēnzhōng rèdù, hěn nán zhēnzhèng zhǎngwò yì mén yǔyán.

4. 她一开始特别积极，买了很多教材，可惜没过多久就三分钟热度了。
   Tā yì kāishǐ tèbié jījí, mǎi le hěn duō jiàocái, kěxī méi guò duō jiǔ jiù sān fēnzhōng rèdù le.
```

## Language quality

### English

- Write explanations in natural, concise C1-level English.
- Do not simplify everything into basic learner English.
- The explanation itself should expose the learner to useful advanced English.

### Chinese

- Write explanations in natural, modern Mandarin (simplified characters).
- Use vocabulary and grammar appropriate for an advanced Chinese learner.
- Do not translate English explanations word-for-word into Chinese.
- The explanation should itself be useful Chinese input.

### Both decks

- Prefer natural language over dictionary-like, mechanical translations.
- Avoid bilingual explanations unless the schema explicitly requires them.
- Never mix Vietnamese explanations into the learning content just to make it
  easier to understand.

## Card format and conventions

### Fields

- English: `Word`, `IPA`, `Definition`, `Usage`, `Examples`. Cards beyond the core
  100 have a `level` of `C1` or `C2`, which becomes an Anki tag.
- Collocations: `Collocation`, `Meaning`, `Usage`, `Examples`, plus a `domain` of
  `academic`, `business` or `everyday` (an Anki tag). The collocations deck follows
  the English deck's language rules. Every example contains all of the collocation's
  content words. A form may vary (`made a mistake`, `my best`), and so may a
  placeholder such as `someone`.
- Chinese: `成语`, `拼音`, `释义`, `用法`, `例句` (each 例句 has the sentence and its pinyin).
- 4–6 example sentences per card, each containing the headword. Mix academic and
  everyday contexts.
- Usage notes cover grammar patterns, collocations, register, nuance, and
  comparisons with near-synonyms where helpful.

### English

- British spelling with Oxford `-ize` endings: criticize, organize, colour, centre,
  analyse, sceptical.
- British IPA in the style of the Oxford Learner's Dictionaries, between slashes,
  with `ˈ ˌ ː` (not ASCII `'` or `:`) and `(r)` for a linking r: /ˈhɪndə(r)/.

### Chinese

- Simplified characters only.
- 成语 are genuine four-character idioms (not 惯用语 such as 三分钟热度).
- Pinyin uses tone marks. 一 and 不 are written with their tone changes
  (yí ge, bú shì, yì zhī bàn jiě), but 一 keeps yī as a number or ordinal
  (dì yī, quē yī bù kě, jǔ yī fǎn sān). Neutral tones are unmarked (péngyou, kàn le).
- Headword pinyin is spaced by syllable (yì jǔ liǎng dé); sentence pinyin is spaced
  by word, starts with a capital letter, and mirrors the sentence's punctuation.
- 释义 and 用法 contain no Latin letters; use …… as a placeholder, not A/B.
- Avoid 儿化 in example sentences, so that the pinyin stays unambiguous.

Run `python scripts/check.py` before building; it enforces most of these rules.
