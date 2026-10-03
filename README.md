# Deck for English and Chinese

Two Anki decks, each written entirely in its target language:

| Deck | File | Cards | Fields |
|---|---|---|---|
| English Vocabulary — Academic & Everyday | `dist/English-Vocabulary.apkg` | 100 | Word, IPA, Definition, Usage, Examples |
| 常用成语 | `dist/Chinese-Chengyu.apkg` | 100 | 成语, 拼音, 释义, 用法, 例句 |

Every card has 4–6 example sentences. The English deck mixes academic words (hypothesis, mitigate, coherent) with words common in everyday conversation (procrastinate, cope, hindsight). The 成语 deck covers four-character idioms used in essays and discussion (显而易见, 以偏概全), study and work (循序渐进, 精益求精), daily life (哭笑不得, 小题大做), and the best-known story idioms (守株待兔, 塞翁失马).

## Importing

Download the `.apkg` files from `dist/` and open them with Anki (File → Import). Re-importing an updated file updates the existing cards and keeps your review history.

## Suggested study pace

Each card is dense, with a definition, usage notes, and several examples, so go slower than you would with simple word–translation cards:

- **English:** about 10 new cards a day, so the deck takes roughly two weeks to introduce.
- **成语:** about 5–8 new cards a day. 成语 are harder to absorb, and each example also needs its pinyin read.

Add the next batch of 50–100 cards once most of the current ones have an interval of three weeks or more.

## Editing and rebuilding

Card content lives in `data/english.json` and `data/chengyu.json`. After editing:

```sh
pip install -r requirements.txt
python scripts/check.py      # structure, monolingual rules, pinyin and IPA checks
python scripts/build.py      # writes dist/*.apkg
```

`check.py` compares pinyin against pypinyin and IPA stress against the CMU dictionary. Both references are imperfect: pypinyin is context-blind and the CMU dictionary is American. So differences are listed for review rather than treated as errors. Notes already checked by hand are recorded in `scripts/reviewed.txt`.

Writing rules and conventions are in [CONTENT_GUIDELINES.md](CONTENT_GUIDELINES.md).
