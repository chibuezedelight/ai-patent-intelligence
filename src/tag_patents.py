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
