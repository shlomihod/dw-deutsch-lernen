__all__ = ["scrap_dw", "save_dataframes"]

import sys
import logging

from dwscraper.pipeline import (build_page_df,
                                build_text_df,
                                build_paragraph_df)

from dwscraper.utils import save_dataframes


logger = logging.getLogger(__name__)


def scrap_dw(n_pages, verbose=False):

     logging_level = logging.INFO if verbose else logging.WARNING
     logging.basicConfig(stream=sys.stdout,
                         level=logging_level)

     page_df = build_page_df(n_pages)

     text_df = build_text_df(page_df)

     if not text_df["text"].apply(bool).all():
          logger.warn("Not all texts were extracted properly!")

     paragraph_df = build_paragraph_df(text_df)

     logger.info("Texts labels count:\n{}"
                 .format(text_df['y'].value_counts()))

     return page_df, text_df, paragraph_df