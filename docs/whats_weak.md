# What's weak

The full list of limits. The README shows the top few. They are ranked by how much
each one could change the main result, largest first.

The main result is this: on the 12 questions I checked by hand, whole pages with
[hybrid search](glossary.md#hybrid-search) put the right page in the top 5 for 0.58 of them (0.33 to 0.83). The
[baseline](glossary.md#baseline), fixed 180-word chunks with [dense search](glossary.md#dense-search), scores 0.25 (0.00 to 0.50).
The numbers come from [reports/metrics.json](../reports/metrics.json).

## Ranked by how much they could change the result

| Rank | Weakness | How much it could change the result | What was done |
|---|---|---|---|
| 1 | Only 12 questions are checked by hand | A lot. One question moves [hit@5](glossary.md#hit5) by about 0.08 (1 divided by 12). The intervals of the top setups overlap, so the best setup could change with a few more questions <!-- not-a-claim --> | The headline uses only these 12 and shows its [confidence interval](glossary.md#confidence-interval). Reading the other 18 is open work |
| 2 | No held-out questions. The best setup was picked on the same questions it is scored on, and the [baseline](glossary.md#baseline) is the weakest setup in the first comparison | A lot. The gap to the baseline is large, but the gap to the closest rival (dense search over whole pages, 0.50, which is what the first version used) is one question of 12. On new questions the winner could differ | Nothing yet. A new set of questions, written after the setup was fixed, would test it |
| 3 | The intervals are rough, and there is none for the gap between two setups. Each comes from resampling only 12 questions, so it can only move in steps of one question. The baseline's lower end of 0.00 is one sign of that. The setups are compared by looking at whether their intervals overlap | Medium. No number here can say that one setup beats another. The README says so | [ADR 0001](decisions/0001-adopting-the-house-standard.md), decision 7, leaves a paired interval for the gap as open work, because adding one would be a new result |
| 4 | 18 of the 30 questions are checked only by a script. I proposed their pages after the first results were known | Medium. It moves the 30-question table, which is where the best setup was picked. The pages could lean toward ones the search finds easily | A stricter check (label and figure in the same passage) passes for 18 of the 20 new questions. The two that failed were read by hand ([ADR 0006](decisions/0006-headline-on-hand-checked-questions.md)) |
| 5 | I wrote the questions (the 20 later ones with an AI assistant as co-author) while reading the report, so they often use the report's own words. Real users would phrase questions their own way | Medium, direction unknown. Questions in the report's words favour keyword search, and so hybrid search. With other wording, dense search might do relatively better | Nothing yet. Questions written by someone who has not read the report would test it |
| 6 | The [embedding](glossary.md#embedding) model reads only the first 256 word pieces of a page | Medium. Dense search over whole pages mostly sees the top of each page. A model with a longer window could change which setup wins | Measured in `notebooks/01_explore.ipynb`. Not fixed. Splitting pages for the vectors while citing whole pages is the first fix to try |
| 7 | One document, one bank, one year | Medium for any general claim, none for the numbers themselves. Nothing here shows how the search does on another report | Nothing yet |
| 8 | The [strict hit](glossary.md#strict-hit) score undercounts, and the lenient score may overcount | Small for the ranking of setups, larger for the level. For the headline setup, strict hit@5 is 0.58 and lenient is 0.83 on the 12 questions | Both are reported, with strict as the headline ([ADR 0004](decisions/0004-two-ways-of-scoring-a-hit.md)) |
| 9 | No test runs `eval/evaluate.py`, the code that produces every number. The coverage floor for the whole repo is 47%, below the bar the standard sets for new repos | Small but hard to see. A bug in the loop that pairs questions with results would move every number, and no test would catch it | The scoring code in `eval/metrics.py` is tested on toy data. A rerun during the retrofit matched the earlier results exactly (commit `f0f065e`). That shows the numbers are stable, not that they are right |
| 10 | The code names the embedding model but does not pin a revision of it | Small today, possibly large later. A new upstream revision would change the dense and hybrid numbers with no change in this repo | Recorded in ADR 0001, decision 8. Pinning it is a change to `src/` that must first be shown not to move any number |
| 11 | The fusion settings (the constant 60 and a depth of 50) are not tuned | Small. Tuning could help hybrid search, but tuning on these questions would overfit | Kept at the published default ([ADR 0005](decisions/0005-hybrid-search-with-rank-fusion.md)). In Q10, fusion loses a correct keyword hit (see [reports/error_analysis.md](../reports/error_analysis.md)) | <!-- not-a-claim -->
| 12 | Tables lose their column headers when text is pulled from the PDF | Small to medium on table questions. Only 2 of the 30 questions are marked as table questions | Nothing yet | <!-- not-a-claim -->

## Limits that change no number

These do not move hit@5 or [MRR](glossary.md#mrr). They affect how far a reader can trust the method, or
what the project covers.

| Weakness | Why it matters | What was done |
|---|---|---|
| The [eval plan](eval_plan.md) was written after the results. An earlier README said the strict score was defined before any results, and the history does not support that | It affects how far a reader can trust that the method was fixed first | The eval plan says so in its title and cites a commit for each choice. The README rewrite (`442727b`) removed that sentence and says what the history does show |
| The answers written by Gemini are not scored | The project measures only whether the right page is found | Nothing yet. The generator refuses without calling the model when nothing is found, and a test checks that |
| `make demo` runs keyword search only, on a few made-up pages | The demo shows that the code runs, not how well the real search works. A reader could mistake its scores for results | The demo's first line says the pages are made up and the scores are a smoke test. A test checks that it never loads the embedding model or the generator |
| mypy runs in its default mode, not strict | Type mistakes in code without type hints could go unseen | Recorded in ADR 0001, decision 11. Strict mode is open work | <!-- not-a-claim -->
| Search times come from one machine, and the index compares the question with every vector | The times would differ on other machines, and exact search would be slow on a large set of documents | The README says times vary from run to run. They are left out of the numbers that must match between runs |
