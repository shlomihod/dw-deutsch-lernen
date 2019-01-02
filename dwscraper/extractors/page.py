"""
Extract article web-page metadata (without the text).
"""

import re
import logging

import numpy as np
import pandas as pd

from dwscraper.extractors.utils import soupify
from dwscraper.fetchers import build_initial_page_df, fetch_html
from dwscraper.consts import LEVELS


ARTIKELS = {"DEUTSCH LERNEN": {"Nachrichten",                      # B2 & C1 - Multiple Text
                               "Langsam gesprochene Nachrichten",  # B2 & C1 - Multiple Text
                               "Top-Thema – Podcast"},             # B1 - One Text
            "LEKTIONEN": {"Top-Thema – Lektionen"},                # B1 - One Text
           }

THEMENSEITEN_RE = re.compile(r"/de/\w+/t-\d+")

logger = logging.getLogger(__name__)


def enrich_with_lektionen_page_df(df,
                                  n_parallel_requests=None):
    logging.info("Enriching with LEKTIONEN pages...")
    lektion = df["soup"].apply(lambda soup: soup.find("span", string="Lektion"))
    if (~lektion.isnull()).any():
        df = df[lektion.isnull()]
        lektion = lektion.dropna()
        lektion_page_df = build_initial_page_df("LEKTIONEN",
                                list(lektion.apply(lambda tag: tag.parent.parent["href"])))
        lektion_page_df = fetch_html(lektion_page_df, n_parallel_requests)
        lektion_page_df["soup"] = soupify(lektion_page_df)

        return pd.concat([df, lektion_page_df])

    else:
        return df

def extract_artikel(df):
    logging.info("Extracting artikel type...")
    df["artikel"] = df["soup"].apply(lambda soup:
                                             soup.find(class_="artikel").get_text())
    return df


def filter_by_url(df):
    logging.info("Filterring by URL (no av type...)")
    av_url_filter = df["url"].apply(lambda url: url.split("/")[-1].split("-")[0] != "av")
    logging.info(av_url_filter.value_counts())
    df = df[av_url_filter]
    return df

def filter_by_artikel(df):
    logging.info("Filtering by artikel...")
    df = df[(df["rubrik"] == "THEMEN")
                  | ((df["rubrik"] == "DEUTSCH LERNEN") & (df["artikel"].isin(ARTIKELS["DEUTSCH LERNEN"])))
                  | ((df["rubrik"] == "LEKTIONEN") & (df["artikel"].isin(ARTIKELS["LEKTIONEN"])))]
    return df

def filter_by_nan_level(df):
    logging.info("Filterring by Levels (no na...)")
    return df[~df["y"].isna()]

def extract_meta(df):
    """
    print("Extracting titles...")
    df["title"] = df["soup"].apply(lambda soup:
                                         soup.h1.get_text())
    """

    logging.info("Extracting tags...")
    df["tags"]  =  df["soup"].apply(lambda soup:
                        [tag.text for tag in soup
                                                 .find("ul", class_="smallList")
                                                 .find_all("a")
                             if tag["href"].startswith("/search/")])
    logging.info("Extracting themes...")
    df["themes"]  =  df["soup"].apply(lambda soup:
                        [theme.text for theme in soup
                                                 .find("ul", class_="smallList")
                                                 .find_all("a")
                             if THEMENSEITEN_RE.match(theme["href"])])



    logging.info("Extracting levels...")
    df["levels"] = df["tags"].apply(lambda tags:
                                            tuple(level for level in LEVELS if level in tags))

    return df


def encode_level(r):
    if r["rubrik"] in {"DEUTSCH LERNEN", "LEKTIONEN"}:
        if r["levels"] == ("B1",):
            return 0
        elif r["levels"] == ("B2", "C1"):
            return 1
        else:
            return np.nan
    elif r["rubrik"] == "THEMEN":
        return 2
    else:
        return np.nan


def encode_level_labels(df):
    logging.info("Encoding level labels...")
    df["y"] = df.apply(encode_level, axis=1)
    return df
