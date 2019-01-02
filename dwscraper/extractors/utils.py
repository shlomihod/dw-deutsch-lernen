import logging
from multiprocessing import Pool

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def _bs_parse_html(html):
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:  # TODO: REALLY BAD!
        logger.warn("Failed BS parsing!")
        soup = BeautifulSoup()
    return soup


def soupify(df, is_parallel=False):
    logging.info("Instantiating soup objects...")

    if is_parallel:
        logging.info("Parallel soupify...")
        with Pool() as p:
            soups = list(p.map(_bs_parse_html, df["html"]))
    else:
        logging.info("Serial soupify...")
        soups = df["html"].apply(_bs_parse_html)
    
    return soups
