import logging

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def _bs_parse_html(html):
    return BeautifulSoup(html, "html.parser")


def soupify(df):
    logging.info("Instantiating soup objects...")
    df["soup"] = df["html"].apply(_bs_parse_html)
    return df
