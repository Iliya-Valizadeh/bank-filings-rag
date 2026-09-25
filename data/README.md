# Data

The filing PDF is **not** committed (size + redistribution). Download it locally.

## Getting the report
1. Download the **2024 Annual Report** PDF from RBC:
   https://www.rbc.com/investor-relations/_assets-custom/pdf/ar_2024_e.pdf
   (listed on https://www.rbc.com/investor-relations/financial-information.html).
   The copy used for the results is 6,464,097 bytes and 250 pages.
2. Save it as `data/raw/rbc_2024.pdf`.

Then:
```bash
python -m src.ingest data/raw/rbc_2024.pdf     # sanity-check page extraction
python -m eval.evaluate --pdf data/raw/rbc_2024.pdf
```
