import time

from patent_data_collector import get_token, search
from search_blocks import CPC_SET, STAGE1

token = get_token()
print(f"{'year':<6}{'keywords':>10}{'cpc':>8}")
for year in range(2024, 2027):
    date = f'pd within "{year}0101 {year}1231"'
    keywords_total, _ = search(token, f"({STAGE1}) AND {date}", 1, 1)
    time.sleep(3)
    cpc_total, _ = search(token, f"{CPC_SET} AND {date}", 1, 1)
    time.sleep(3)
    print(f"{year:<6}{keywords_total:>10}{cpc_total:>8}")