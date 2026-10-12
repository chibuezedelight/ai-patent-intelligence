# Week 1, Friday: Explore the Dataset and Write the Report

AI Patent Intelligence Platform for III-V Semiconductor Lasers. Follow the steps in order, on Windows with PowerShell. The analysis follows `docs/course/Week1/thursday/iii-v_patent_search.md`, sections 6 to 9: tagging, data fields, analyses and charts.

## Today at a glance

1. Tag every patent and group the patents into families (`src/tag_patents.py`).
2. Check a sample of the tags by hand.
3. Install the notebook tools (`matplotlib`, `ipykernel`).
4. Run the analysis notebook (`notebooks/week1_eda.ipynb`).
5. Read the charts and tables.
6. Write 3 to 5 observations, each with a number.
7. Build `reports/week1_report.pdf`.
8. Commit and push to GitHub.

**Result:** tagged data files, 11 charts, a 13-page report PDF and a pushed repository.

## Before you start

**What you will have at the end:** two tagged files in `data/processed`, a committed notebook, 11 chart images in `reports/figures`, and `reports/week1_report.pdf`.

**Time needed:** about 4 hours. **Week 1 goal:** a first patent dataset (Thursday) and a short report (Friday). Today turns the raw download into answers.

**What you need from Thursday:** `data/raw/iii_v_laser_patents.csv` with 2,248 patents, and the `(.venv)` environment.

**How to read each step:** Why is the reason. Do this is what to type or click. It worked if is your check. If it goes wrong lists the usual problems and the fix. Run commands from the project root, with `(.venv)` showing in the prompt.

## Decisions made today

| Decision | Choice | Reason |
|---|---|---|
| What to count | Patent families, not documents | The same invention is often filed several times. |
| Trend year | Priority year 2010 to 2024 | Priority years before 2010 are only partly in the download, and 2025 and 2026 are not complete yet (patents are published about 18 months after filing). |
| GaN and quantum cascade patents | Flagged, left out of the charts, kept in the files | They matched the CPC set but are not InP or GaAs quantum-dot lasers. |
| Tags | Keyword rules on title and abstract, plus CPC codes | Fast first pass. Checked by hand, refined with claims text later. |
| Company names | Light cleaning only | Full name merging is Week 2, Friday. |

## Words you will see

| Word | Meaning |
|---|---|
| Family | All patent documents that belong to the same invention. |
| Priority year | The year of the first filing of an invention. |
| Lead applicant | The first company named on the patent. |
| Tag | A label such as InP, VCSEL or Datacenter, added by rules. |
| Unspecified | No rule matched, so the patent has no tag in that dimension. |
| Noise flag | Marks patents that mention GaN or quantum cascade lasers. |
| Notebook | A file with code cells you run one by one. Results appear under each cell. |
| Kernel | The Python that runs the notebook. It must be the `.venv` one. |
| Heatmap | A table where darker cells mean bigger numbers. |
| White space | A technology area with few or no patents. |

## Step 1: Tag the patents and group them into families

**Why:** The raw CSV has one row per patent document. Analysis needs families, a priority year, and tags for material, emission, cavity, active region, integration, trend and application (section 6 of the search document).

**You need:** The CSV from Thursday.

**Do this:** create `src/tag_patents.py`. It writes `data/processed/patents_tagged.csv` (one row per document) and `data/processed/families_tagged.csv` (one row per family). A tag is added when its words appear in the title or abstract, or when its CPC code is present. The keyword rules are a first pass.

```python
"""Friday step 1: clean the Thursday dataset, add priority year and families, and tag every patent.

Reads  data/raw/iii_v_laser_patents.csv
Writes data/processed/patents_tagged.csv   (one row per patent document)
       data/processed/families_tagged.csv  (one row per patent family)

Run from the project root:  python src/tag_patents.py
"""
import re
from pathlib import Path

import pandas as pd

INPUT = Path("data/raw/iii_v_laser_patents.csv")
OUT_PATENTS = Path("data/processed/patents_tagged.csv")
OUT_FAMILIES = Path("data/processed/families_tagged.csv")

QD = r"quantum dot|\bqds?\b"

# dimension -> tag -> list of patterns. ALL patterns of a tag must match the lower-case title + abstract.
RULES = {
    "material": {
        "InP": [r"\binp\b|indium phosphide|ingaasp|inalgaas"],
        "GaAs QD": [QD, r"gaas|gallium arsenide|\binas\b"],
    },
    "emission": {
        "VCSEL": [r"vcsel|vertical[- ]cavity surface[- ]emitting"],
        "Edge-emitting": [r"edge[- ]emitting|\beel\b|ridge waveguide"],
    },
    "cavity": {
        "DFB": [r"\bdfb\b|distributed feedback"],
        "DBR / tunable": [r"\bdbr\b|distributed bragg reflector|tunable"],
        "Fabry-Perot": [r"fabry[- ]p[eé]rot"],
        "EML": [r"\beml\b|electro[- ]?absorption modulat"],
    },
    "active_region": {
        "Quantum dot": [QD],
        "Quantum well": [r"quantum well|\bmqw\b"],
    },
    "integration": {
        "Photonic IC": [r"photonic integrated circuit|\bpics?\b|monolithic(ally)? integrat"],
        "Heterogeneous on Si/SiN": [r"heterogeneous|wafer[- ]bond|silicon[- ]on[- ]insulator|\bsoi\b|silicon nitride"],
        "Grown on Si": [r"(grown|growth|epitaxial)[^.]{0,40}\bsilicon\b|silicon substrate|\bsi substrate"],
    },
    "trend": {
        "External laser source": [r"external laser|external light source|remote laser|continuous[- ]wave|\bcw\b"],
        "Comb laser": [r"frequency comb|comb laser|optical comb"],
        "High-temperature": [r"high[- ]temperature|uncooled|athermal|temperature[- ]insensitive"],
    },
    "application": {
        "Datacenter": [
            r"data ?cent(er|re)s?|datacom|optical interconnect|optical transceiver"
            r"|co-packaged|\bcpo\b|silicon photonics"
        ],
        "Telecom": [r"telecom|optical (fiber|fibre) communication|optical communication|long[- ]haul|\b1310\b|\b1550\b"],
        "Sensing / LiDAR": [r"lidar|sensing|\bsensor|spectroscop|time[- ]of[- ]flight|gas detect"],
    },
}
NOISE = r"\bgan\b|gallium nitride|quantum cascade"

# Extra tags read from the CPC codes (many abstracts never name the material or the laser type).
# Codes from the III-V search document, section 3, plus H01S5/183 (vertical-cavity surface-emitting lasers).
# Check each code in the CPC browser on Espacenet before relying on it.
CPC_RULES = {
    "material": {"InP": r"H01S5/34306"},
    "emission": {"VCSEL": r"H01S5/183"},
    "active_region": {"Quantum dot": r"H01S5/341"},
}

SUFFIXES = r"\b(INC|CORP|CORPORATION|LTD|LIMITED|LLC|CO|COMPANY|GMBH|AG|SA|BV|KK|PLC|LP|GROUP|HOLDINGS?)\b"


def clean_name(name):
    """Light company-name cleaning. Full name normalisation comes in Week 2."""
    name = re.sub(r"\s*\[[A-Z]{2}\]", "", name.upper())  # country tags such as [US]
    name = re.sub(r"[.,]", "", name)
    name = re.sub(SUFFIXES, "", name)
    return " ".join(name.split())


def tags_for(text, cpc, dimension):
    """Tags for one patent in one dimension: from the title + abstract words, or from its CPC codes."""
    found = []
    for tag, patterns in RULES[dimension].items():
        by_text = all(re.search(p, text) for p in patterns)
        cpc_pattern = CPC_RULES.get(dimension, {}).get(tag)
        by_cpc = bool(cpc_pattern) and re.search(cpc_pattern, cpc) is not None
        if by_text or by_cpc:
            found.append(tag)
    return "; ".join(found) if found else "unspecified"


def main():
    df = pd.read_csv(INPUT, dtype=str, keep_default_na=False)
    print(f"Read {len(df)} patent rows from {INPUT}")

    # Priority year: first available of priority, application, publication date
    df["priority_year"] = float("nan")
    for column in ("priority_date", "application_date", "publication_date"):
        year = pd.to_numeric(df[column].str[:4], errors="coerce")
        df["priority_year"] = df["priority_year"].fillna(year)
    df["priority_year"] = df["priority_year"].astype("Int64")

    # Companies
    df["lead_applicant"] = df["applicants"].str.split("; ").str[0].fillna("")
    df["lead_applicant_clean"] = df["lead_applicant"].map(clean_name)

    # Tags from title + abstract
    text = (df["title"] + " " + df["abstract"]).str.lower()
    for dimension in RULES:
        df[dimension] = [tags_for(t, c, dimension) for t, c in zip(text, df["cpc"])]
    df["noise_flag"] = text.str.contains(NOISE, regex=True)
    df["datacenter"] = df["application"].str.contains("Datacenter")

    # Families: one row per family, the earliest priority first
    df["family_key"] = df["family_id"].where(df["family_id"] != "", df["number"])
    df["family_size_in_data"] = df.groupby("family_key")["number"].transform("count")
    order = df.assign(_p=df["priority_date"].replace("", "99999999")).sort_values(["_p", "publication_date"])
    families = order.drop_duplicates("family_key").drop(columns="_p")

    OUT_PATENTS.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATENTS, index=False)
    families.to_csv(OUT_FAMILIES, index=False)

    # Summary to read and post
    print(f"\nPatent documents: {len(df)}   Families: {len(families)}")
    print(f"Empty abstract: {(df['abstract'] == '').sum()}   Empty CPC: {(df['cpc'] == '').sum()}   "
          f"No priority year: {df['priority_year'].isna().sum()}")
    print(f"Possible noise (GaN / quantum cascade): {int(families['noise_flag'].sum())} families")

    print("\nFamilies per priority year (2005 onward):")
    per_year = families["priority_year"].value_counts().sort_index()
    print(per_year[per_year.index >= 2005].to_string())

    print("\nTag counts (families):")
    for dimension in RULES:
        counts = families[dimension].str.split("; ").explode().value_counts()
        share = 100 * (families[dimension] == "unspecified").mean()
        print(f"  {dimension} ({share:.0f}% unspecified): " + ", ".join(f"{tag} {n}" for tag, n in counts.items()))

    print("\nTop 15 lead applicants (families):")
    print(families["lead_applicant_clean"].value_counts().head(15).to_string())
    print(f"\nSaved {OUT_PATENTS} and {OUT_FAMILIES}")


if __name__ == "__main__":
    main()
```

```powershell
python src/tag_patents.py
```

**Results from the first run** (the first version of the script, which tagged by words only)

| Measure | Value |
|---|---|
| Patent documents | 2,248 |
| Families | 1,540 |
| Empty abstract | 74 |
| Empty CPC | 112 |
| No priority year | 0 |
| Flagged GaN or quantum cascade | 122 families |

| Priority year | Families | Priority year | Families |
|---|---|---|---|
| 2010 | 55 | 2019 | 86 |
| 2011 | 44 | 2020 | 106 |
| 2012 | 58 | 2021 | 124 |
| 2013 | 54 | 2022 | 126 |
| 2014 | 61 | 2023 | 123 |
| 2015 | 65 | 2024 | 123 |
| 2016 | 85 | 2025 | 66 |
| 2017 | 84 | 2026 | 17 |
| 2018 | 113 | | |

| Dimension | Tags found (families) | Unspecified |
|---|---|---|
| Material | InP 281, GaAs QD 23 | 1,237 |
| Emission | VCSEL 142, Edge-emitting 83 | 1,316 |
| Cavity | DBR / tunable 153, DFB 89, EML 23, Fabry-Perot 9 | 1,296 |
| Active region | Quantum well 378, Quantum dot 63 | 1,107 |
| Integration | Grown on Si 52, Photonic IC 48, Heterogeneous on Si/SiN 38 | 1,423 |
| Trend | High-temperature 33, External laser source 9, Comb laser 7 | 1,494 |
| Application | Telecom 32, Sensing / LiDAR 31, Datacenter 16 | 1,463 |

Top lead applicants (families): Sumitomo Electric Industries 89, Institute of Semiconductors CAS 60, Anhui Geen Semiconductor 56, NTT 48, Mitsubishi Electric 40, Furukawa Electric 26, Sony 22 and Sony Group 22 (the same company), Shandong Huaguang Optoelectronics 20, Samsung Electronics 19, Nuvoton Technology Japan 19, OSRAM Opto Semiconductors 17, Lumentum Operations 17, IBM 16, Seiko Epson 15.

The script above also reads CPC codes and merges Sony and Sony Group, so its tag counts are a little higher than this table and Sony appears once. Put your own numbers next to these.

**It worked if:** it prints `Read 2248 patent rows`, the family count, the per-year table and the tag counts, and the two files exist in `data/processed`.

**If it goes wrong**

- It prints nothing. Fix: the file is not saved (white dot on the tab) or the last two lines are missing. Press Ctrl+S and check the file ends with `if __name__ == "__main__": main()`.
- `FileNotFoundError` for the CSV. Fix: run from the project root, and make sure Thursday's download finished.
- `ModuleNotFoundError: pandas`. Fix: the environment is not active. Run `.venv\Scripts\Activate.ps1`.
- `KeyError` for a column. Fix: the CSV is from an older version of `collect_dataset.py`. Rerun Thursday's download.

## Step 2: Check the tags by hand

**Why:** The search document says to read 20 to 30 results by hand. Keyword rules can be too loose (tagging something that does not fit) or too tight (missing things).

**You need:** Step 1 finished.

**Do this**

```powershell
$f = 'data/processed/families_tagged.csv'
python -c "import pandas as pd; print(pd.read_csv('$f').sample(25)[['title','material','emission']])"
```

Read the 25 rows. Does each tag fit the title? Note any rule that is clearly wrong.

**It worked if:** most tags make sense. A few misses are normal, because abstracts often do not name the material or the application.

**If it goes wrong**

- A tag appears where it does not belong. Fix: tighten its pattern in `RULES`, save, and rerun Step 1.
- Many obvious patents are untagged. Fix: add a word variant to the pattern, or accept it for now. Claims text in Week 2 will help.

## Step 3: Install the notebook tools

**Why:** The analysis runs in a notebook and draws charts with `matplotlib`.

**You need:** The `(.venv)` prompt, and VS Code.

**Do this**

```powershell
pip install matplotlib ipykernel
pip freeze > requirements.txt
```

In VS Code, install the Jupyter extension if it offers one (extensions view, search "Jupyter").

**It worked if:** `pip list` shows matplotlib and ipykernel, and `requirements.txt` was updated.

**If it goes wrong**

- `Running cells requires the ipykernel package`. Fix: run `pip install ipykernel` with `(.venv)` active.
- The `.venv` kernel is not listed. Fix: press Ctrl+Shift+P, choose **Python: Select Interpreter**, pick the one in `.venv`, then reopen the notebook.

## Step 4: Run the analysis notebook

**Why:** One notebook holds the checks, the charts and the tables, so every number can be traced and rerun.

**You need:** Steps 1 and 3.

**Do this:** save `week1_eda.ipynb` in `notebooks/`, open it, choose the `.venv` kernel (top right), and click **Run All**. It works from the project root or from the notebook folder.

| Section | What it does | Output |
|---|---|---|
| 1. Load and check | Counts documents and families, checks duplicates and empty cells | Printed tables |
| 2. Working set | Keeps priority years 2010 to 2024, drops flagged GaN and quantum cascade families | Printed counts |
| 3. Families per year | Total, and InP and GaAs QD where tagged | `01_families_per_year.png` |
| 4. Companies | Top 15 companies, top 12 by three-year period, with change | `02_top_companies.png`, `03_company_momentum.png` |
| 5. Technology mix | Cavity, emission and integration tags by period | `04` to `06` mix charts |
| 6. Specialisation and gaps | Company x tag heatmap, material x application and material x integration | `07_company_by_tag.png`, `08_white_space_cells.png` |
| 7. Life cycle | Families and different companies per year | `09_life_cycle.png` |
| 8. Tracked companies | Coherent, Lumentum, ams OSRAM, Trumpf, Broadcom, Nokia Bell Labs, with name variants | `10_tracked_companies.png` |
| 9. Keywords | Top words and word pairs in titles and abstracts | `11_top_words.png` |
| 10. Observations and report | Your sentences, then the PDF | `reports/week1_report.pdf` |

**It worked if:** every cell shows a green check, 11 PNG files appear in `reports/figures`, and each chart is followed by its data table.

**If it goes wrong**

- `ModuleNotFoundError: matplotlib`. Fix: the kernel is not `.venv`. Select it, then Run All again.
- `FileNotFoundError` for `families_tagged.csv`. Fix: run Step 1 first.
- A chart is empty. Fix: check the working-set counts in section 2. If they are zero, the priority years or the file are wrong.
- `NameError` in a later cell. Fix: an earlier cell did not run. Click **Run All**.

## Step 5: Read the results

**Why:** Charts are only useful if you can say what they show and what they cannot show.

**You need:** Step 4 finished.

**Do this:** go through the sections and ask these questions.

- **Families per year:** is it growing, flat or falling? Ignore 2025 and 2026.
- **Top companies and momentum:** who leads, who is accelerating, who is slowing down (the `change` column)?
- **Technology mix:** which cavity types grow or shrink?
- **Heatmaps:** which cells are thin? These are candidate white spaces, not proof. Most families have no application tag, so the cells are lower bounds.
- **Life cycle:** are families and companies both rising (emerging field), or are families rising while companies fall (consolidation)?
- **Tracked companies:** how many families does each of the six have? Name variants are matched only approximately.

**It worked if:** you can describe each chart in one sentence with a number.

**If it goes wrong**

- A tracked company shows zero. Fix: its name variant may be missing. Search the `applicants` column for part of the name and add it to `TRACKED`.
- The numbers differ from this guide. Fix: expected. The notebook leaves out flagged and out-of-range families, and your data may differ slightly.

## Step 6: Write 3 to 5 observations

**Why:** The plan asks for observations, and a report without them is only pictures. Good observations say what changed, by how much, and who is behind it.

**You need:** Step 5 done.

**Do this:** in the `OBSERVATIONS` cell, replace the example lines with your own findings. Each one needs a number, and each number must match a table in the notebook. Examples from the first run (check them against your tables):

- Activity roughly doubled: families per priority year rose from 55 in 2010 to about 125 a year in 2021 to 2024.
- Sumitomo Electric has the most families (89), followed by the Institute of Semiconductors CAS (60), Anhui Geen (56), NTT (48) and Mitsubishi Electric (40). Of the six tracked companies, only Lumentum and OSRAM Opto Semiconductors reach the top 15 (17 families each).
- Most families carry no technology tag from titles and abstracts, and only 16 families are tagged datacenter, so datacenter conclusions need claims text and better tagging.

**It worked if:** each line has a number you can find in a table.

**If it goes wrong**

- A `SyntaxError` after editing. Fix: each line must be inside quotes and end with a comma.

## Step 7: Build the report PDF

**Why:** The Friday deliverable is `reports/week1_report.pdf`: dataset size, top companies, keywords and observations.

**You need:** Steps 4 and 6.

**Do this:** run the `OBSERVATIONS` cell, then the cell under it. It writes a title page with the dataset size, top companies, tag coverage and limits, then one page per chart, then your observations.

**It worked if:** the cell prints `Saved ...\reports\week1_report.pdf`, the file has 13 pages, and the last page shows your sentences.

**If it goes wrong**

- `NameError: name 'top' is not defined`. Fix: an earlier cell did not run. Click **Run All**, then run the last two cells.
- The last page still shows the example lines. Fix: run the `OBSERVATIONS` cell after editing it, then the report cell again.
- `PermissionError`. Fix: the old PDF is open in a viewer. Close it and rerun.

## Step 8: Save your work to GitHub

**Why:** Every session ends with a commit and push. Code, the notebook, the charts and the report go up. The data files and secrets do not.

**You need:** Git signed in, and the `.gitignore` from Monday.

**Do this**

```powershell
git status
git add .
git status
git commit -m "Add dataset tagging, Week 1 analysis notebook and report"
git push
```

Also save this guide as `docs/course/Week1/friday/friday_guide.md`, before `git add .`.

**It worked if:** the second `git status` lists `src/tag_patents.py`, `notebooks/week1_eda.ipynb`, `reports/week1_report.pdf`, the files in `reports/figures`, `requirements.txt` and the guide, and does NOT list `.env`, `.venv` or any CSV in `data`. After the push, refresh your repository page and check.

**If it goes wrong**

- A CSV or `.env` is listed. Fix: stop. Check the rules in `.gitignore` and run `git check-ignore -v data/processed/families_tagged.csv`. Do not commit until it disappears.
- `push rejected (fetch first)`. Fix: run `git pull --rebase`, then `git push`.
- `nothing to commit`. Fix: you are in the wrong folder, or everything was already committed. Check with `git status`.
- Sign-in fails. Fix: sign in to GitHub from VS Code (Accounts icon, bottom left), then push again.

## Friday is done when

- `data/processed/families_tagged.csv` and `patents_tagged.csv` exist.
- `notebooks/week1_eda.ipynb` runs from top to bottom and is committed.
- `reports/week1_report.pdf` has your observations and is committed.
- GitHub shows the code, notebook and report, and no data files or secrets.

## Known limits (state these in the report)

- Tags come from keyword rules on titles, abstracts and CPC codes, not from claims. Most patents have no material, emission or application tag.
- Only 16 families were tagged datacenter in the first run, so datacenter conclusions are weak.
- Publication years before 2010 are not collected, so priority years before 2010 are partial.
- The latest priority years (2025 and 2026) are incomplete.
- Company names are only lightly cleaned. The six tracked companies are matched by name variants.
- The EPO counts results per application, so the numbers are closer to inventions than to documents.

## How it all fits together

Monday gave you the tools and the EPO access. Thursday built a tested search and downloaded 2,248 patents. Today turned that file into 1,540 families, tagged them, drew the charts and wrote the report. The Week 1 goal was a first real dataset and a short report, and both now exist. The patent counts, the company ranking and the thin tags also tell you what Week 2 must fix: a database, cleaner company names, and claims text.

## Moving forward

Next: Week 2, Monday. Start PostgreSQL in Docker and design the database schema for patents, assignees, inventors and CPC codes. Before that, commit this work and send a short summary of Week 1 for the weekly review.
