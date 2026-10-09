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