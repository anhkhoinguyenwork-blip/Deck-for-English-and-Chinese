# Deck for English and Chinese

Five Anki decks, each written entirely in its target language:

| Deck | File | Cards | Fields |
|---|---|---|---|
| English Vocabulary — Academic & Everyday | `dist/English-Vocabulary.apkg` | 800 | Word, IPA, Definition, Usage, Examples |
| English Collocations — Academic, Business & Everyday | `dist/English-Collocations.apkg` | 800 | Collocation, Meaning, Usage, Examples |
| English Chunks — Spoken & Written | `dist/English-Chunks.apkg` | 300 | Chunk, Meaning, Usage, Examples |
| 常用成语 | `dist/Chinese-Chengyu.apkg` | 100 | 成语, 拼音, 释义, 用法, 例句 |
| 常用语块 | `dist/Chinese-Chunks.apkg` | 300 | 语块, 拼音, 释义, 用法, 例句 |

Every card has 4–6 example sentences. The English deck mixes academic words (hypothesis, mitigate, coherent) with words common in everyday conversation (procrastinate, cope, hindsight). The original 100 core words have no level tag. The other 700 are tagged `C1` (579) or `C2` (121), so you can filter them in the browser with `tag:C1` or `tag:C2`. The levels are approximate, based on how common and advanced each word is, not on an official list.

The collocation deck covers word combinations that sound natural to native speakers. Each card is tagged `academic` (254), `business` (253) or `everyday` (293), for example conduct research, meet a deadline and make ends meet.

The two chunk decks teach ready-made phrases and sentence frames that you can drop straight into speech or writing. Slots are marked with … (English) or …… (Chinese), and the fixed parts are highlighted in each example. Each deck has 10 categories of 30 cards, and the category is an Anki tag:

- **English:** `opinion` (If you ask me, …), `agreeing` (I take your point, but …), `hedging` (As far as I know, …), `linking` (That being said, …), `clarifying` (What I mean is …), `requests` (I was wondering if you could …), `social` (I owe you one), `conversation` (Come to think of it, …), `academic` (It is worth noting that …) and `business` (I'll keep you posted).
- **Chinese:** `关联词` (与其……不如……), `句式` (对……来说), `观点` (说白了), `回应` (话是这么说), `推测` (说不定), `过渡` (话说回来), `书面` (由此可见), `交际` (给你添麻烦了), `口语` (舍不得) and `情绪` (真拿你没办法). None of them repeat a card from the 成语 deck.

The 成语 deck covers four-character idioms used in essays and discussion (显而易见, 以偏概全), study and work (循序渐进, 精益求精), daily life (哭笑不得, 小题大做), and the best-known story idioms (守株待兔, 塞翁失马).

## Importing

Download the `.apkg` files from `dist/` and open them with Anki (File → Import). Re-importing an updated file updates the existing cards and keeps your review history.

## Suggested study pace

Each card is dense, with a definition, usage notes, and several examples, so go slower than you would with simple word–translation cards:

- **English vocabulary:** about 10 new cards a day, so the deck takes roughly three months to introduce.
- **Collocations:** about 10 new cards a day. Studying both English decks means 20 new cards a day, so drop each to 5–8 if reviews pile up.
- **English chunks:** about 10 new cards a day, so about a month.
- **成语 and 语块:** about 5–8 new cards a day each. Each example also needs its pinyin read.

If you study several decks at once, keep the total to about 20–25 new cards a day and lower it when reviews pile up. The 成语 deck takes two to three weeks, and the 语块 deck about six to eight weeks.

## Editing and rebuilding

Card content lives in `data/english.json`, `data/collocations.json`, `data/chunks.json`, `data/chengyu.json` and `data/yukuai.json` (the Chinese chunks). After editing:

```sh
pip install -r requirements.txt
python scripts/check.py      # structure, monolingual rules, pinyin and IPA checks
python scripts/build.py      # writes dist/*.apkg
```

`check.py` compares pinyin against pypinyin and IPA stress against the CMU dictionary. For collocations and chunks it also checks that every example contains the headword. Both references are imperfect: pypinyin is context-blind and the CMU dictionary is American. So differences are listed for review rather than treated as errors. Notes already checked by hand are recorded in `scripts/reviewed.txt`.

Writing rules and conventions are in [CONTENT_GUIDELINES.md](CONTENT_GUIDELINES.md).
