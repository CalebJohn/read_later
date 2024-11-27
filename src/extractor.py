from urllib.parse import urlsplit, urljoin

import httpx
from lxml import html
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
    tree = html.fromstring(body)

    for img in tree.xpath('//img[@src]'):
        src = img.get('src')

        parsed_src = urlsplit(src)

        # Skip if the image already has a domain (has a netloc)
        if parsed_src.netloc:
            continue

        normalized_src = urljoin(url, src)

        img.set('src', normalized_src)

    return html.tostring(tree, method='html', encoding='unicode')


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
