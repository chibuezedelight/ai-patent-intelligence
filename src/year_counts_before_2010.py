import time

from patent_data_collector import get_token, search
from search_blocks import CPC_SET, STAGE1

FIRST_YEAR = 1970
LAST_YEAR = 2009

token = get_token()
token_time = time.time()

keywords_sum = 0
cpc_sum = 0

print(f"{'year':<6}{'keywords':>10}{'cpc':>8}")
for year in range(FIRST_YEAR, LAST_YEAR + 1):
    # Tokens expire after about 20 minutes, so ask for a fresh one after 15
    if time.time() - token_time > 900:
        token = get_token()
        token_time = time.time()

    date = f'pd within "{year}0101 {year}1231"'
    try:
        keywords_total, _ = search(token, f"({STAGE1}) AND {date}", 1, 1)
        time.sleep(3)
        cpc_total, _ = search(token, f"{CPC_SET} AND {date}", 1, 1)
        time.sleep(3)
    except RuntimeError as error:
        print(f"{year:<6} ERROR: {str(error)[:100]}".replace("\n", " "))
        continue

    keywords_sum += keywords_total
    cpc_sum += cpc_total
    print(f"{year:<6}{keywords_total:>10}{cpc_total:>8}")

print(f"\n{'total':<6}{keywords_sum:>10}{cpc_sum:>8}")
print(f"Keywords: {keywords_sum} + 267 (2010-2026) = {keywords_sum + 267}, overall was 2635")