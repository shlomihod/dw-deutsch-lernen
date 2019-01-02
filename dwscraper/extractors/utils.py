import logging
from multiprocessing import Pool

from bs4 import BeautifulSoup
from tqdm import tqdm


logger = logging.getLogger(__name__)
tqdm.pandas()


def _bs_parse_html(html):
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:  # TODO: REALLY BAD!
        logger.warn("Failed BS parsing!")
        soup = BeautifulSoup()
    return soup


def soupify(df, is_parallel=False):
    logger.info("Instantiating soup objects...")

    if is_parallel:
        logger.info("Parallel soupify...")
        with Pool() as p:
            soups = list(p.map(_bs_parse_html, df["html"]))
    else:
        logger.info("Serial soupify...")

        apply_method_name = ('progress_apply'
                                if logger.level <= logging.INFO
                                else 'apply')

        df_apply_method = getattr(df["html"], apply_method_name)
        soups = df_apply_method(_bs_parse_html)
    
    return soups
