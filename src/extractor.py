from urllib.parse import urlsplit, urlunsplit

import httpx
from bs4 import BeautifulSoup
from readability import Document


def extract_document(body: str):
    doc = Document(body)

    return doc.title(), doc.summary()


def normalize_image_src(url: str, body: str):
    """
    Often times image tags use relative source links
    e.g. /images/mountain.png instead of https://my.url/images/mountain.png
    we need to normalize this
    """
    soup = BeautifulSoup(body, "lxml")

    scheme, host, _, _, _ = urlsplit(url)

    for img in soup.find_all("img", src=True):
        _, _, path, query, fragment = urlsplit(img["src"])
        img["src"] = urlunsplit((scheme, host, path, query, fragment))

    return str(soup)


def fetch_document(url: str, user_agent: str | None):
    # We prefer to forward the users actual user_agent, it seems the most fair
    if not user_agent:
        # window.navigator.userAgent
        user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0"
    headers = {"user-agent": user_agent}
    resp = httpx.get(url, headers=headers)

    if resp.status_code != httpx.codes.OK:
        return None

    return normalize_image_src(url, resp.text)
