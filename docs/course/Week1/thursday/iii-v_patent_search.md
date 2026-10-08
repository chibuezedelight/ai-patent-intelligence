# Patent Search Strategy: InP Lasers & GaAs Quantum-Dot Lasers

Goal: retrieve patents on **InP lasers** and **GaAs quantum-dot lasers** (stage 1), then narrow to **datacenter use** (stage 2).

---

## 1. Search logic

Minimum structure: **three blocks combined with AND**.

| Block | Role |
|---|---|
| A | It is a semiconductor laser |
| B | The material (InP **or** GaAs quantum dot) |
| D | Application: datacenter (stage 2 only) |

The rest of the classification list (cavity, emission, integration) is used to **tag results afterwards**, not in the search query.

---

## 2. Stage 1: core search

### Block A: semiconductor laser

```
"semiconductor laser" OR "laser diode" OR "diode laser"
```

### Block B1: InP lasers

```
InP OR "indium phosphide" OR InGaAsP OR InAlGaAs
```

### Block B2: GaAs quantum-dot lasers

```
("quantum dot" OR "quantum dots" OR QD) AND (GaAs OR "gallium arsenide" OR InAs)
```

### Combined query

```
A AND (B1 OR B2)
```

### Why these keywords

- GaAs quantum-dot lasers almost always use **InAs dots** grown on GaAs. Many patents write "InAs quantum dots" and never "GaAs quantum-dot laser", so InAs must be included.
- InP laser patents often name only the active layer (**InGaAsP**, **InAlGaAs**) or the wavelength (1310 / 1550 nm), not "InP".

---

## 3. CPC classification codes (strongly recommended)

Combining keywords with CPC codes gives much cleaner results.

| Purpose | CPC code |
|---|---|
| Semiconductor lasers (all) | H01S 5/ |
| III-V material lasers | H01S 5/343 (and subgroups) |
| Long-wavelength InP lasers (>1000 nm) | H01S 5/34306 |
| Quantum dots / reduced dimensionality | H01S 5/341 |
| Nanotechnology tag for quantum dots | B82Y 20/00 |

Robust version:

```
CPC = H01S5/343* AND (B1 OR B2)
```

> Check each code in the CPC browser (Espacenet) before use; subgroup numbers occasionally change.

---

## 4. Optional exclusions (use carefully)

```
NOT (GaN OR "gallium nitride" OR "quantum cascade")
```

Do **not** exclude "LED" or "photodetector": many laser patents mention them in passing, and relevant hits would be lost.

---

## 5. Stage 2: datacenter filter

### Block D: datacenter / datacom

```
"data center" OR datacenter OR "data centre" OR datacom OR "optical interconnect"
OR "optical transceiver" OR "co-packaged optics" OR CPO OR "silicon photonics"
```

Supporting CPC codes:

| Purpose | CPC code |
|---|---|
| Optical transmission systems | H04B 10/ |
| Coupling optics to opto-electronic chips | G02B 6/42 |

### Final query

```
A AND (B1 OR B2) AND D
```

---

## 6. Tagging results (classification after retrieval)

Tag each patent using these categories. This gives clean trend charts.

| Dimension | Tags |
|---|---|
| Material | InP, GaAs QD |
| Emission | Edge-emitting (EEL), VCSEL |
| Cavity | Fabry-Pérot, DFB, DBR / tunable, EML |
| Active region | Bulk, quantum well, quantum dot |
| Integration | Discrete, monolithic InP PIC, heterogeneous on Si / SiN, grown on Si |
| Trend | External laser source (CPO), comb laser, high-temperature operation |
| Application | Datacenter, telecom, sensing / LiDAR, other |

Tagging can be done with keyword rules first, then checked (or refined) with an LLM classifier on title + abstract + claims.

---

## 7. Data fields to extract

| Field | Used for |
|---|---|
| Publication / application number | Unique ID |
| Family ID | Count inventions, not duplicates |
| Priority date | Timing of the invention (use for trends) |
| Assignee / applicant | Company analysis |
| Inventors | Talent and team analysis |
| CPC codes | Technology classification |
| Priority country + family countries | Geography and target markets |
| Forward / backward citations | Influence and who builds on whom |
| Legal status | Active, granted, lapsed, expired |
| Title, abstract, claims | Tagging and text analysis |

---

## 8. Recommended patent analyses

### 8.1 Competitor landscape

- **Top assignees** by number of patent families.
- **Filing frequency per company over time**: who is accelerating, who is slowing down.
- **New entrants**: companies whose first filing in this field is within the last 3–5 years.
- **Technology mix per company**: e.g. one company focuses on DFB + CPO, another on QD-on-silicon.
- **Geographic strategy**: where each company files (US, EP, CN, JP, KR, TW) shows which markets they protect.
- **Portfolio quality**: family size (more countries = more valuable) and forward citations (more cited = more influential).

### 8.2 Current customers

- **Datacenter and system companies filing laser-related patents** (e.g. hyperscalers, switch / GPU / network chip makers): they reveal demand and the specifications they care about.
- **Co-assignees**: patents filed jointly by a laser maker and a system company indicate a supply or development relationship.
- **Citation links**: system companies citing a laser maker's patents suggest they build on that technology.

### 8.3 Potential customers

- Companies filing in **Block D topics** (CPO, optical interconnect, silicon photonics transceivers) **without** their own laser patents: they need lasers but don't make them.
- Companies whose **silicon-photonics patents mention an "external laser source"**: direct buyers for CW InP DFB lasers.

### 8.4 White spaces

- **Heatmap of material × integration × application**: empty or thin cells are possible gaps (e.g. QD lasers for CPO external sources).
- **Lapsed or expired patents**: technology that is free to use.
- **Topics with growing filings but few players**: opportunity before the field gets crowded.
- **Geographic gaps**: inventions protected in the US/CN but not in Europe.

### 8.5 Other useful analyses

- **Technology life cycle**: number of applicants vs. number of filings per year. Growth in both = emerging; filings up but applicants down = consolidation.
- **Inventor mobility**: inventors moving between companies indicate know-how transfer and talent hotspots.
- **Universities and research centres** (e.g. imec, Ghent University, UCSB): early-stage technology and licensing / partnership options.
- **Assignee name normalization** (essential): merge names such as Finisar / II-VI / Coherent, or subsidiaries, before any company analysis.

---

## 9. Suggested plots and charts

| Chart | Shows |
|---|---|
| Line chart: filings per year (InP vs GaAs QD) | Overall trend |
| Stacked area chart: filings per year by cavity / emission / integration | How the technology mix changes |
| Horizontal bar chart: top 15 assignees | Who leads |
| Line chart: filings per year for top 5–10 assignees | Company momentum |
| Heatmap: assignee × technology tag | Company specialisation |
| Bubble chart: total filings (x) vs. recent growth (y), bubble = citations | Leaders vs. rising challengers |
| World map or bar chart: filings by country | Geographic focus |
| Heatmap: material × integration × application | White spaces |
| Network graph: co-assignees and citations | Partnerships and customer links |
| Life-cycle curve: applicants vs. filings per year | Maturity of the field |
| Sankey diagram: material → structure → application | Flow from technology to market |

---

## 10. Practical tips

- Test each block separately and check **20–30 results by hand** before combining.
- Count **patent families**, not individual publications, to avoid double counting.
- Use **priority date** for trends, not publication date.
- The **last 18 months are incomplete**: patents are published about 18 months after filing, so recent years always look low.
- Block D ("silicon photonics" especially) is broad: it is the most likely source of noise.
