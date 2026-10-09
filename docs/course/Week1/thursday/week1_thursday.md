# Week 1, Thursday: Build the First Patent Dataset

AI Patent Intelligence Platform for III-V Semiconductor Lasers. Follow the steps in order, on Windows with PowerShell. The search design comes from `docs/course/Week1/thursday/iii-v_patent_search.md`, sections 1 to 5.

## Before you start

**What you will have at the end:** a working EPO login in code, a tested search for InP lasers and GaAs quantum-dot lasers, and a CSV file with 2,248 patents (publication years 2010 to 2026) in `data/raw`.

**Time needed:** about 4 hours, plus about 15 minutes of download time. **Week 1 goal:** a first patent dataset (today) and a short report (Friday). Today builds the dataset that Friday analyses.

**What you need from Monday:** the `(.venv)` environment with `requests`, `pandas` and `python-dotenv`, an approved EPO app, and a `.env` file with `EPO_CONSUMER_KEY` and `EPO_CONSUMER_SECRET`.

**How to read each step:** Why is the reason. Do this is what to type or click. It worked if is your check. If it goes wrong lists the usual problems and the fix. Run every command from the project root, with `(.venv)` showing in the prompt.

## Decisions made today

| Decision | Choice | Reason |
|---|---|---|
| Date range | Publication years 2010 to 2026 | CPC counts are reliable from 2010. Older years can be added later by changing one number. |
| Query | Stage 1 keywords OR the CPC set | Each one misses patents the other finds. |
| Exclusions (GaN, quantum cascade) | Not used in the search. Tagged on Friday. | A hard exclusion drops patents that only mention GaN in passing. |
| Datacenter filter (stage 2) | Not a second search. Tagged on Friday. | No extra API calls, and the full set stays available. |
| Trend year | Priority date, not publication date | The priority date is closest to when the invention was made. |

## Words you will see

| Word | Meaning |
|---|---|
| Token | A temporary pass the EPO gives your script after it shows the key and secret. |
| CQL | The search language of the EPO, for example `ti="laser diode"`. |
| ti, ab | Search the title (ti) or the abstract (ab). |
| CPC | A subject category code for a patent, like a shelf number in a library. Many patents share one. |
| Block | A small search piece, such as "it is a semiconductor laser". Blocks are joined with AND and OR. |
| Range | The slice of results you ask for, for example 1-25. The EPO sends results in pages. |
| Throttling | The EPO slows you down when you ask too fast. It answers 403 with the word RobotDetected. |
| XML | The tagged text format the EPO answers in. |
| Priority date | The date of the first filing of an invention. |
| Patent family | All patent documents that belong to the same invention. |

## Step 1: Check the setup

**Why:** Most Thursday errors come from a wrong name in `.env` or a missing library. Checking takes one minute.

**You need:** Monday finished.

**Do this**

```powershell
.venv\Scripts\Activate.ps1
pip list
```

Open `.env` and check that the two names are exactly these (no quotes, no spaces around the equals sign):

```
EPO_CONSUMER_KEY=your_key
EPO_CONSUMER_SECRET=your_secret
```

**It worked if:** the prompt starts with `(.venv)` and `pip list` shows requests, pandas and python-dotenv.

**If it goes wrong**

- No `(.venv)` in the prompt. Fix: run the activation line again.
- The EPO app is still pending. Fix: wait for approval. Nothing below works without it.

## Step 2: Get an access token

**Why:** The EPO gives data only to programs that show a valid token. This is the first half of `src/patent_data_collector.py`.

**You need:** The `.env` from Step 1.

**Do this:** put this in `src/patent_data_collector.py`. The imports at the top are used by Step 4 as well, so keep them all.

```python
import os
import time
import xml.etree.ElementTree as ET

import requests
from dotenv import load_dotenv

AUTH_URL = "https://ops.epo.org/3.2/auth/accesstoken"
SEARCH_URL = "https://ops.epo.org/3.2/rest-services/published-data/search"
NS = {"ops": "http://ops.epo.org", "ex": "http://www.epo.org/exchange"}


def get_token():
    """Ask the EPO for a temporary access token."""
    load_dotenv()
    key = os.getenv("EPO_CONSUMER_KEY")
    secret = os.getenv("EPO_CONSUMER_SECRET")
    if not key or not secret:
        raise ValueError("Missing EPO_CONSUMER_KEY or EPO_CONSUMER_SECRET in .env")

    response = requests.post(
        AUTH_URL,
        auth=(key, secret),
        data={"grant_type": "client_credentials"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]
```

Test it:

```powershell
python -c "import sys; sys.path.insert(0,'src'); from patent_data_collector import get_token; print(len(get_token()))"
```

**It worked if:** it prints a number (the length of the token) and no error.

**If it goes wrong**

- `Missing EPO_CONSUMER_KEY or EPO_CONSUMER_SECRET`. Fix: the names in `.env` do not match Step 1.
- `401` or `400` error. Fix: wrong key or secret, or the app is not approved yet.
- `getaddrinfo failed`. Fix: no internet connection. Check Wi-Fi or VPN and try again.
- `cannot import name 'get_token'`. Fix: the function is missing or the file is not saved. Press Ctrl+S.

## Step 3: Write the search blocks

**Why:** The search is built from small blocks, so each one can be tested alone. This follows the search document: A is the laser, B1 is InP, B2 is GaAs quantum dots, D is datacenter.

**You need:** Step 2 working.

**Do this:** create `src/search_blocks.py` with this content. The function `terms()` turns a list of words into a search piece that looks in the title and the abstract. `STAGE1` is A AND (B1 OR B2). `CPC_SET` is the three CPC codes for III-V lasers, InP lasers and quantum dots.

```python
"""Search blocks for the III-V laser patent search (see docs/course/Week1/thursday/iii-v_patent_search.md)."""


def terms(*words):
    """Match any of the words in the title OR the abstract."""
    parts = []
    for word in words:
        parts.append(f'ti="{word}"')
        parts.append(f'ab="{word}"')
    return "(" + " OR ".join(parts) + ")"


# Block A: it is a semiconductor laser
BLOCK_A = terms("semiconductor laser", "laser diode", "diode laser")

# Block B1: InP lasers
BLOCK_B1 = terms("InP", "indium phosphide", "InGaAsP", "InAlGaAs")

# Block B2: GaAs quantum-dot lasers
BLOCK_B2 = (
    "("
    + terms("quantum dot", "quantum dots", "QD")
    + " AND "
    + terms("GaAs", "gallium arsenide", "InAs")
    + ")"
)

# Block D (stage 2): datacenter
BLOCK_D = terms(
    "data center", "datacenter", "data centre", "datacom", "optical interconnect",
    "optical transceiver", "co-packaged optics", "CPO", "silicon photonics",
)

CPC_ALL_LASERS = "cpc=H01S5/00"
CPC_III_V = "cpc=H01S5/343"
CPC_INP_LONG = "cpc=H01S5/34306"
CPC_QD = "cpc=H01S5/341"
EXCLUDE = terms("GaN", "gallium nitride", "quantum cascade")

STAGE1 = f"{BLOCK_A} AND ({BLOCK_B1} OR {BLOCK_B2})"

CPC_SET = f"({CPC_III_V} OR {CPC_INP_LONG} OR {CPC_QD})"

QUERIES = {
    "B2 (GaAs QD)": BLOCK_B2,
    "QD terms only": terms("quantum dot", "quantum dots", "QD"),
    "GaAs/InAs terms only": terms("GaAs", "gallium arsenide", "InAs"),
    "D alone (datacenter)": BLOCK_D,
    "A AND D": f"{BLOCK_A} AND {BLOCK_D}",
    "B1 AND D": f"{BLOCK_B1} AND {BLOCK_D}",
    "CPC set (343, 34306, 341)": CPC_SET,
    "UNION: stage 1 OR CPC set": f"({STAGE1}) OR {CPC_SET}",
}
```

**It worked if:** the file has no red underlines in VS Code and appears only once (no pasted copy below it).

**If it goes wrong**

- A `SyntaxError` about brackets. Fix: a bracket was lost while copying. Paste the file again.
- The content appears twice in the file. Fix: delete the second copy.

## Step 4: Add the search function

**Why:** This is the part that asks the EPO and reads the answer. `_get` waits and retries when the EPO says you are too fast. `search` returns the number of matches and the first patent numbers.

**You need:** Steps 2 and 3.

**Do this:** add this below `get_token` in `src/patent_data_collector.py`. The whole file is now Step 2 plus Step 4.

```python
def _get(url, token, params, retries=3):
    """GET request that waits and retries when the EPO says we are going too fast."""
    for attempt in range(retries + 1):
        response = requests.get(
            url,
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
        )
        too_fast = response.status_code == 403 and "RobotDetected" in response.text
        if too_fast and attempt < retries:
            wait = 60 * (attempt + 1)
            print(f"EPO says slow down. Waiting {wait} seconds...")
            time.sleep(wait)
            continue
        return response


def search(token, query, first=1, last=25):
    """Run one search. Return (total number of matches, list of patent numbers)."""
    response = _get(SEARCH_URL, token, {"q": query, "Range": f"{first}-{last}"})
    if response.status_code == 404:  # the EPO answers 404 when nothing matches
        return 0, []
    if response.status_code >= 400:
        raise RuntimeError(f"EPO error {response.status_code}: {response.text[:300]}")

    root = ET.fromstring(response.content)
    result = root.find("ops:biblio-search", NS)
    total = int(result.attrib["total-result-count"])

    numbers = []
    for ref in result.findall(".//ops:publication-reference", NS):
        doc = ref.find("ex:document-id[@document-id-type='docdb']", NS)
        country = doc.findtext("ex:country", namespaces=NS)
        number = doc.findtext("ex:doc-number", namespaces=NS)
        kind = doc.findtext("ex:kind", namespaces=NS)
        numbers.append(f"{country}{number}{kind}")
    return total, numbers
```

**It worked if:** Step 5 prints counts.

**If it goes wrong**

- `NameError: name 'time' is not defined`. Fix: add `import time` to the imports at the top of the file. It only appears when the EPO throttles you, so it can stay hidden for a while.
- `RobotDetected` (403). Fix: the EPO is limiting you. The script waits 1, 2 and 3 minutes by itself. If it still fails, wait 10 to 15 minutes.
- A 404 is not an error. For this service it means zero matches.

## Step 5: Test every block

**Why:** The search document says to test each block alone before combining. A block with a typo returns zero or too many.

**You need:** Steps 3 and 4.

**Do this:** create `src/test_blocks.py`:

```python
import time

from patent_data_collector import get_token, search
from search_blocks import QUERIES

token = get_token()
for label, query in QUERIES.items():
    try:
        total, numbers = search(token, query, 1, 3)
        print(f"{label:34} {total:>8}   e.g. {numbers}")
    except RuntimeError as error:
        print(f"{label:34} ERROR: {str(error)[:150]}".replace("\n", " "))
    time.sleep(1)  # be polite to the EPO servers
```

Run it:

```powershell
python src/test_blocks.py
```

Then take 5 of the example patent numbers it prints for each block, open them on worldwide.espacenet.com, and read the title and abstract. Do they match what the block should find?

**It worked if:** all 8 lines show a count and an example list, with no ERROR, and the examples look like real semiconductor laser patents.

**If it goes wrong**

- `ERROR ... 403`. Fix: throttling. Wait a few minutes and rerun.
- A count of 0. Fix: look for a typo in the field codes (`ti`, `ab`, `cpc`).
- Many examples are not lasers. Fix: normal for broad blocks like "D alone". They are not used alone.

## Step 6: Count patents per year

**Why:** One search can only return its first 2,000 results. Counting per year shows whether any year goes over, and how the two methods compare.

**You need:** Step 5 working.

**Do this:** create `src/year_counts.py`:

```python
import time

from patent_data_collector import get_token, search
from search_blocks import CPC_SET, STAGE1

FIRST_YEAR = 2010
LAST_YEAR = 2026

token = get_token()
print(f"{'year':<6}{'keywords':>10}{'cpc':>8}")
for year in range(FIRST_YEAR, LAST_YEAR + 1):
    date = f'pd within "{year}0101 {year}1231"'
    keywords_total, _ = search(token, f"({STAGE1}) AND {date}", 1, 1)
    time.sleep(3)
    cpc_total, _ = search(token, f"{CPC_SET} AND {date}", 1, 1)
    time.sleep(3)
    print(f"{year:<6}{keywords_total:>10}{cpc_total:>8}")
```

```powershell
python src/year_counts.py
```

It makes 34 searches with pauses, so it takes a few minutes. If the EPO throttles you, run it in two halves by changing `FIRST_YEAR` and `LAST_YEAR`.

**Results from this run**

| Year | Keywords | CPC | Year | Keywords | CPC |
|---|---|---|---|---|---|
| 2010 | 22 | 70 | 2019 | 17 | 135 |
| 2011 | 24 | 91 | 2020 | 17 | 153 |
| 2012 | 20 | 70 | 2021 | 12 | 154 |
| 2013 | 21 | 71 | 2022 | 14 | 172 |
| 2014 | 14 | 64 | 2023 | 14 | 163 |
| 2015 | 16 | 71 | 2024 | 9 | 192 |
| 2016 | 15 | 93 | 2025 | 13 | 155 |
| 2017 | 16 | 100 | 2026 | 7 | 145 |
| 2018 | 16 | 121 | | | |

**What it shows**

- No year is near 2,000, so no year needs to be split.
- The CPC counts grow from 70 to about 190 a year. The keyword counts stay flat at 7 to 24, so keywords alone are too thin for trends. CPC is the base of the dataset and keywords add extra candidates.
- The keyword search found 2,635 patents over all years, but only about 270 are from 2010 onward. We also counted 1970 to 2005 once: keyword matches peaked in 1986 to 1988 (161 to 171 a year) and CPC was almost empty before 1990. Years 2006 to 2009 were not counted because a connection drop stopped that run. This is why the dataset starts in 2010.
- 2026 is a partial year, and the latest years are always incomplete because patents are published about 18 months after filing.

**It worked if:** every year prints two numbers.

**If it goes wrong**

- The table stops with RobotDetected. Fix: wait 10 to 15 minutes and rerun for the missing years.
- `invalid_access_token`. Fix: the token expired. Run the script again.

## Step 7: Download the dataset

**Why:** This is the main task of the day. The script asks the EPO for the full record of each patent (title, applicants, abstract, dates, CPC codes, citations) and saves them in one CSV.

**You need:** Steps 2 to 6.

**Do this:** create `src/collect_dataset.py`. It asks for 25 records at a time, one year at a time, with a 5 second pause. It saves after every year, so a stop loses nothing, and it skips saved years when you run it again.

```python
"""Collect the III-V laser patents (publication years FIRST_YEAR to LAST_YEAR) into one CSV."""
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import requests

from patent_data_collector import NS, SEARCH_URL, _get, get_token
from search_blocks import CPC_SET, STAGE1

FIRST_YEAR = 2010
LAST_YEAR = 2026
PAGE_SIZE = 25
PAUSE = 5  # seconds between requests
OUTPUT = Path("data/raw/iii_v_laser_patents.csv")
DEBUG_FILE = Path("data/raw/debug_response.xml")

state = {"token": None}


def text_of(element, path):
    """Text of the first element matching path, or an empty string."""
    found = element.find(path, NS)
    return found.text.strip() if found is not None and found.text else ""


def docdb_number(document_id):
    """Turn a docdb <document-id> into a number like EP3000000A1."""
    return (
        text_of(document_id, "ex:country")
        + text_of(document_id, "ex:doc-number")
        + text_of(document_id, "ex:kind")
    )


def names(biblio, group, item, name_tag):
    """Applicant or inventor names without duplicates (the EPO lists each name in several formats)."""
    people = biblio.findall(f"ex:parties/ex:{group}/ex:{item}", NS)
    chosen = people
    for wanted in ("epodoc", "docdb", "original"):
        matching = [p for p in people if p.get("data-format") == wanted]
        if matching:
            chosen = matching
            break
    result = []
    for person in chosen:
        name = re.sub(r"\s*\[[A-Z]{2}\]$", "", text_of(person, f"ex:{name_tag}/ex:name"))
        if name and name not in result:
            result.append(name)
    return "; ".join(result)


def parse_document(doc):
    """Turn one <exchange-document> into a flat dictionary (one CSV row)."""
    biblio = doc.find("ex:bibliographic-data", NS)
    if biblio is None:
        return None
    pub = biblio.find("ex:publication-reference/ex:document-id[@document-id-type='docdb']", NS)
    app = biblio.find("ex:application-reference/ex:document-id[@document-id-type='docdb']", NS)

    priority_dates = [
        d.text
        for d in biblio.findall("ex:priority-claims/ex:priority-claim/ex:document-id/ex:date", NS)
        if d.text
    ]

    titles = biblio.findall("ex:invention-title", NS)
    title = next(
        (t.text for t in titles if t.get("lang") == "en"),
        (titles[0].text or "") if titles else "",
    )

    abstracts = doc.findall("ex:abstract", NS)
    chosen = next((a for a in abstracts if a.get("lang") == "en"), abstracts[0] if abstracts else None)
    abstract = " ".join("".join(chosen.itertext()).split()) if chosen is not None else ""

    cpc = []
    for c in biblio.findall("ex:patent-classifications/ex:patent-classification", NS):
        section = text_of(c, "ex:section")
        if not section:
            continue
        code = (
            section + text_of(c, "ex:class") + text_of(c, "ex:subclass")
            + text_of(c, "ex:main-group") + "/" + text_of(c, "ex:subgroup")
        )
        if code not in cpc:
            cpc.append(code)

    cited = []
    cited_path = "ex:references-cited/ex:citation/ex:patcit/ex:document-id[@document-id-type='docdb']"
    for ref in biblio.findall(cited_path, NS):
        number = docdb_number(ref)
        if number and number not in cited:
            cited.append(number)

    return {
        "number": doc.get("country", "") + doc.get("doc-number", "") + doc.get("kind", ""),
        "family_id": doc.get("family-id", ""),
        "publication_date": text_of(pub, "ex:date") if pub is not None else "",
        "application_date": text_of(app, "ex:date") if app is not None else "",
        "priority_date": min(priority_dates) if priority_dates else "",
        "title": title,
        "applicants": names(biblio, "applicants", "applicant", "applicant-name"),
        "inventors": names(biblio, "inventors", "inventor", "inventor-name"),
        "cpc": "; ".join(cpc),
        "abstract_lang": chosen.get("lang", "") if chosen is not None else "",
        "abstract": abstract,
        "cited_count": len(cited),
        "cited": "; ".join(cited),
    }


def page(query, first, last):
    """Fetch one page of full records. Returns (total matches, list of records)."""
    for _ in range(5):
        try:
            response = _get(
                SEARCH_URL + "/biblio", state["token"], {"q": query, "Range": f"{first}-{last}"}
            )
        except requests.exceptions.RequestException as error:
            print(f"  Connection problem ({type(error).__name__}). Waiting 30 seconds...")
            time.sleep(30)
            continue
        if response.status_code == 404:  # the EPO answers 404 when nothing matches
            return 0, []
        if response.status_code == 400 and "invalid_access_token" in response.text:
            state["token"] = get_token()
            continue
        if response.status_code >= 400:
            raise RuntimeError(f"EPO error {response.status_code}: {response.text[:300]}")

        root = ET.fromstring(response.content)
        result = root.find("ops:biblio-search", NS)
        total = int(result.attrib["total-result-count"])
        parsed = (parse_document(d) for d in result.findall(".//ex:exchange-document", NS))
        records = [r for r in parsed if r]
        if total > 0 and not records:
            DEBUG_FILE.write_text(response.text, encoding="utf-8")
            raise RuntimeError(f"{total} matches but no record could be read. Reply saved to {DEBUG_FILE}")
        return total, records
    raise RuntimeError("Gave up after 5 attempts (connection or token problem)")


def collect_year(year):
    """All records published in one year. Returns (total matches, records)."""
    date = f'pd within "{year}0101 {year}1231"'
    query = f"(({STAGE1}) OR {CPC_SET}) AND {date}"
    total, records = page(query, 1, min(PAGE_SIZE, 25))
    if total > 2000:
        print(f"  WARNING: {year} has {total} matches, above the 2,000 cap. Split this year.")
    first = PAGE_SIZE + 1
    while first <= min(total, 2000):
        time.sleep(PAUSE)
        last = min(first + PAGE_SIZE - 1, total)
        _, more = page(query, first, last)
        records.extend(more)
        first += PAGE_SIZE
    return total, records


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rows, done_years = [], set()
    if OUTPUT.exists():  # resume: skip years that are already saved
        old = pd.read_csv(OUTPUT, dtype=str, keep_default_na=False)
        rows = old.to_dict("records")
        done_years = set(old["query_year"].astype(int))
        print(f"Resuming. Years already saved: {sorted(done_years)}")

    state["token"] = get_token()
    token_time = time.time()
    print(f"{'year':<6}{'matches':>9}{'fetched':>9}")
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        if year in done_years:
            continue
        if time.time() - token_time > 900:  # fresh token every 15 minutes
            state["token"] = get_token()
            token_time = time.time()
        total, records = collect_year(year)
        for record in records:
            record["query_year"] = str(year)
        rows.extend(records)
        pd.DataFrame(rows).drop_duplicates("number").to_csv(OUTPUT, index=False)  # save after every year
        print(f"{year:<6}{total:>9}{len(records):>9}")
        time.sleep(PAUSE)

    final = pd.DataFrame(rows).drop_duplicates("number")
    print(f"\nSaved {len(final)} patents to {OUTPUT}")
    print(final[["number", "publication_date", "applicants", "title"]].head(5).to_string())


if __name__ == "__main__":
    main()
```

First test with one year. Set `FIRST_YEAR = 2024` and `LAST_YEAR = 2024`, save with Ctrl+S, and run:

```powershell
python src/collect_dataset.py
```

Check the file (explained in Step 8). Then set the range to 2010 and 2026, save again, and run the same command. It skips 2024 and fetches the rest in about 15 minutes. Keep the terminal open.

**Results from this run**

| Year | Matches | Fetched | Year | Matches | Fetched |
|---|---|---|---|---|---|
| 2010 | 89 | 89 | 2019 | 148 | 148 |
| 2011 | 110 | 110 | 2020 | 167 | 167 |
| 2012 | 90 | 90 | 2021 | 163 | 163 |
| 2013 | 91 | 91 | 2022 | 185 | 185 |
| 2014 | 76 | 76 | 2023 | 174 | 174 |
| 2015 | 85 | 85 | 2024 | 198 | 198 |
| 2016 | 104 | 104 | 2025 | 168 | 168 |
| 2017 | 115 | 115 | 2026 | 151 | 151 |
| 2018 | 134 | 134 | | | |

Total: **2,248 patents**.

**It worked if:** matches equal fetched on every row, and the last lines say `Saved 2248 patents`.

**If it goes wrong**

- Nothing prints after "Resuming". Fix: you changed the years but did not save the file. Press Ctrl+S and rerun.
- `no record could be read`. Fix: open `data/raw/debug_response.xml`, copy its first 60 lines and show them to Claude. The reading code needs a small change.
- `EPO error 403 ... RobotDetected` and the script stops. Fix: wait 10 to 15 minutes and run the same command. It resumes.
- `Connection problem ... Waiting 30 seconds`. Fix: no action. The script retries by itself.
- `EPO error 4xx` about the range. Fix: lower `PAGE_SIZE` and show the message to Claude.
- Fewer fetched than matches for a year. Fix: delete that year's rows or the CSV and rerun for that year.

## Step 8: Check the data

**Why:** A download that ran without errors can still be empty in important columns.

**You need:** The CSV from Step 7.

**Do this**

```powershell
python -c "import pandas as pd; d=pd.read_csv('data/raw/iii_v_laser_patents.csv'); print(d.shape); print(d.isna().sum())"
```

**It worked if:** `title`, `applicants`, `priority_date` and `family_id` have no empty cells. In the 2024 test (198 rows) 6 patents had no abstract, 3 had no CPC codes and 104 had no backward citations. These small gaps are normal.

**If it goes wrong**

- `title` or `applicants` mostly empty. Fix: the reading code does not match the EPO answer. Show Claude the first rows.

## Step 9: Save your work to GitHub

**Why:** Every session ends with a commit and push. Code goes up, data and secrets do not.

**You need:** Git signed in, and the `.gitignore` from Monday.

**Do this**

```powershell
git status
git add .
git status
git commit -m "Add EPO collector, search blocks and dataset download"
git push
```

Also save this guide as `docs/course/Week1/thursday/thursday_guide.md`.

**It worked if:** `git status` lists the new files in `src` but NOT `.env`, `.venv` or the CSV in `data/raw`.

**If it goes wrong**

- `.env` or the CSV is listed. Fix: stop. Check the rules in `.gitignore`, then commit only when they disappear.

## Thursday is done when

- The token script works and `.env` stays out of Git.
- `search_blocks.py`, `patent_data_collector.py`, `test_blocks.py`, `year_counts.py` and `collect_dataset.py` are in `src`.
- `data/raw/iii_v_laser_patents.csv` holds 2,248 patents and matches equal fetched for every year.
- The work is committed and pushed.

## Known limits (write these in the Friday report)

- The dataset is a broad candidate pool. The CPC set also catches lasers that are not InP or GaAs quantum-dot lasers (for example a camera with VCSELs), so Friday's tags are needed to separate them.
- The EPO counts results per application (one invention), not per publication step, so the numbers are closer to inventions than to documents.
- Publication years before 2010 are not collected.
- Claims, forward citations, legal status and family countries are not collected yet. Each needs an extra request per patent, so they belong to the Week 2 pipeline.

## How it all fits together

Monday gave you the tools, the folders and the EPO access. Today your script used that access to log in (Step 2), a search was built from tested blocks (Steps 3 to 5), the size of the problem was checked before downloading (Step 6), and the data was saved (Steps 7 and 8). The week goal is a first real dataset and a short report. Today produced the dataset, and the numbers above are the base of Friday's analysis.

## Moving forward

Next: Friday. Tag every patent, count families and companies, make the charts, and write `reports/week1_report.pdf`.
