"""
Fetching URLs and html-pages from DW.
"""

import time
import logging
import warnings
import resource

# https://stackoverflow.com/questions/43183367/grequests-with-requests-has-collision
with warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    import grequests

from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import pandas as pd

from dwscraper.utils import batches, exception_handler, tqdm_is_logged
from dwscraper.consts import LEVELS


INF = float("inf")

NUM_PARALLEL_REQUESTS = 5

DW_URL = "http://www.dw.com"
DW_URL_SEARCH_FORMAT = DW_URL + "/search/?{item_field}{content_type_field}languageCode=de&searchNavigationId={rubrik}&to={to}&sort=DATE&resultsCounter={counter}"
DW_RUBRIK = {"THEMEN": 9077, "DEUTSCH LERNEN": 2055}

logger = logging.getLogger(__name__)
logging.getLogger(__name__)

# https://stackoverflow.com/questions/49572302/grequests-too-many-open-files-error/
resource.setrlimit(resource.RLIMIT_NOFILE, (10000, 10000))


def generate_dw_search_url(rubrik, counter=1000, to=None, **kwargs):
    assert rubrik in DW_RUBRIK
    if rubrik == "DEUTSCH LERNEN":
        assert "item" in kwargs and kwargs["item"] in LEVELS

    if to is None:
        to = time.strftime("%d.%m.%Y")

    format_kwargs = {"rubrik": DW_RUBRIK[rubrik],
                    "counter": counter,
                    "to": to}

    if rubrik == "THEMEN":
        format_kwargs["content_type_field"] = "contentType=ARTICLE&"
    else:
        format_kwargs["content_type_field"] = ""

    if "item" in kwargs:
        format_kwargs["item_field"] = "item={}&".format(kwargs["item"])
    else:
        format_kwargs["item_field"] = ""

    return DW_URL_SEARCH_FORMAT.format(**format_kwargs)


def get_dw_urls(rubrik, limit=INF, **kwargs):

    urls = set()
    to = None
    keep_scraping = True

    if logger.level <= logging.INFO:
        pbar = tqdm()

    while keep_scraping:
        dw_url = generate_dw_search_url(rubrik=rubrik,
                                        to=to,
                                        **kwargs)

        r = requests.get(dw_url)

        soup = BeautifulSoup(r.content, "html.parser")

        search_results = soup.find_all(class_="searchResult")
        if search_results:
            urls |= {result.a["href"] for result in search_results}
            new_to = soup.find_all("span", class_="date")[-1].get_text()
        else:
            keep_scraping = False

        if len(urls) >= limit:
            keep_scraping = False

        if new_to == to:
            keep_scraping = False
        else:
            to = new_to

        if logger.level <= logging.INFO:
            pbar.update(pbar.pos + 1)

    if logger.level <= logging.INFO:
        pbar.close()

    return urls


def build_initial_page_df(rubrik, urls):
    return pd.DataFrame({"rubrik": rubrik, "url": urls})


def initialize_page_df():

    logger.info("Retrieving articles URLS...")

    deutsch_lernen_urls_by_level = (get_dw_urls("DEUTSCH LERNEN", item=level) for level in LEVELS)
    deutsch_lernen_urls = list(set.union(*deutsch_lernen_urls_by_level))
    page_df = build_initial_page_df("DEUTSCH LERNEN", deutsch_lernen_urls)

    # with pd.concat
                    # pd.DataFrame({"rubrik": "THEMEN",
                    #                "url": list(get_dw_urls("THEMEN",
                    #                                        limit=n_themen))})


    return page_df


def fetch_html(df):
    logger.info("Retrieving all the pages ({})...".format(len(df)))

    n_iters = len(df)//NUM_PARALLEL_REQUESTS + 1
    failed_requests = []
    rs = []

    pbar = tqdm_is_logged(logger.level <= logging.INFO, total=n_iters)

    for batch in pbar(batches(df["url"], NUM_PARALLEL_REQUESTS)):
        requests_list = [grequests.get(DW_URL + url, stream=False) for url in batch]
        responses = grequests.map(requests_list, exception_handler=exception_handler)

        for response in responses:
            if response is None:
                continue
            if response.status_code != 200:
                failed_requests.append(response.text)

        rs.extend(responses)


    df["request"] = rs

    logger.info("Trying to retrieving failed ones...")
    df["request"] = df.apply(lambda r:
                                    r["request"]
                                    if r["request"] is not None
                                    else requests.get(DW_URL + r["url"]),
                                  axis=1)

    logger.info("Extracting HTML...")
    df["html"] = df.apply(lambda r:
                                    r["request"].content
                                    if r["request"].content.strip().endswith(b"</html>")
                                    else requests.get(DW_URL + r["url"]).content,
                                  axis=1)


    is_full_html_mask = df["html"].str.strip().str.endswith(b"</html>")
    df = df[is_full_html_mask]

    logger.info("Count of articles with full HTML:\n{}"
                .format(is_full_html_mask.value_counts()))

    return df
