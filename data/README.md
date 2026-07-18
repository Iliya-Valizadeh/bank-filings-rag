# Data

The filing PDF is **not** committed (size + redistribution). Download it locally.

## Get the RBC 2024 Annual Report
1. Go to RBC's investor relations / annual report page:
   https://www.rbc.com/investor-relations/annual-meeting-reports.html
2. Download the **2024 Annual Report** PDF.
3. Save it as `data/raw/rbc_2024.pdf`.

Then:
```bash
python -m src.ingest data/raw/rbc_2024.pdf     # sanity-check page extraction
python -m eval.evaluate --pdf data/raw/rbc_2024.pdf
```
