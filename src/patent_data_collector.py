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