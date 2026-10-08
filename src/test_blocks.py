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