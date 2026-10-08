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