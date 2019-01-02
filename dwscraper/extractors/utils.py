import logging
from multiprocessing import Pool

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def _bs_parse_html(html):
    return BeautifulSoup(html, "lxml")


def soupify(df, is_parallel=True):
    logging.info("Instantiating soup objects...")

    if is_parallel:
        logging.info("Parallel soupify...")
        with Pool() as p:
            soups = list(p.map(_bs_parse_html, df["html"]))
    else:
        logging.info("Serial soupify...")
        soups = df["html"].apply(_bs_parse_html)
    
    return soups
