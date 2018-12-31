"""
End-to-end pipeline function that extract pages, texts and paragraphs.
"""

import logging

import pandas as pd

from dwscraper import fetchers
from dwscraper.extractors import page, text
from dwscraper.utils import tqdm_is_logged, oncify_newline_spaces

logger = logging.getLogger(__name__)


def build_page_df(n_pages=None, to_filter=True):
    page_df = fetchers.initialize_page_df()

    if n_pages is not None:
        page_df = page_df.sample(n=int(n_pages))

    page_df = fetchers.fetch_html(page_df)
    page_df = page.soupify(page_df)

    page_df = page.enrich_with_lektionen_page_df(page_df)

    page_df = page.extract_artikel(page_df)

    if to_filter:
        page_df = page.filter_by_artikel(page_df)
        page_df = page.filter_by_url(page_df)


    page_df = page.extract_meta(page_df)

    page_df = page.encode_level_labels(page_df)

    if to_filter:
        page_df = page.filter_by_nan_level(page_df)

    page_df = page_df.reset_index(drop=True)
    logger.info("#pages = {}".format(len(page_df)))

    return page_df


def build_text_df(page_df):
    logger.info("Building Text Dataframe...")

    pbar = tqdm_is_logged(logger.level <= logging.INFO, total=len(page_df))
    
    text_rows = [text.build_text_rows(page_row)
                 for _, page_row in pbar(page_df.iterrows())]
    
    text_df = pd.concat(text_rows)
    
    text_df["text"] = text_df["text"].apply(oncify_newline_spaces)

    text_df = text_df.reset_index(drop=True)
    logger.info("#texts = {}".format(len(text_df)))

    return text_df


def build_paragraph_df(text_df):
    logger.info("Building Paragraphs Dataframe...")

    number_paragraphs = (text_df["text"]
                         .apply(lambda text:
                                len(text.split("\n"))))

    paragraphs_rows = []

    for _, text_row in text_df[number_paragraphs != 1].iterrows():
        for paragraph in text_row["text"].split("\n"):
            paragraphs_row = text_row.copy()
            paragraphs_row["text"] = paragraph
            paragraphs_rows.append(paragraphs_row)

    paragraph_df = pd.concat([text_df[number_paragraphs == 1],
                           pd.DataFrame(paragraphs_rows)])

    assert len(paragraph_df) == number_paragraphs.sum()

    return paragraph_df
