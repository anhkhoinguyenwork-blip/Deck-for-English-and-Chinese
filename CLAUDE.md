# Deck for English and Chinese

Anki decks for English vocabulary and Chinese 成语. Card data lives in
`data/*.json`; `scripts/build.py` turns it into `dist/*.apkg`.

All card content must follow the rules in @CONTENT_GUIDELINES.md.

After changing card data, run `python scripts/check.py` and fix every ERROR. Check
each new REVIEW line by hand; if it is a false positive, add it to
`scripts/reviewed.txt`. Then rebuild with `python scripts/build.py` and commit the
updated `dist/*.apkg` files.
