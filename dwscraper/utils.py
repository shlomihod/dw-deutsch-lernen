import re
import os
from functools import partial

import pandas as pd
from tqdm import tqdm

NEWLINES_RE = re.compile(r"\s*\n+\s*")
SPACES_RE = re.compile(r"[ ]+")


def tqdm_is_logged(is_logged, **kwargs):
    if is_logged:
        return partial(tqdm, **kwargs)
    else:
        return iter
        

def batches(iterable, n=1):
    """
    From http://stackoverflow.com/a/8290508/270334
    :param n:
    :param iterable:
    """
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def exception_handler(request, exception):
    print("{} failed: {} ".format(request.kwargs, exception))


def oncify_newline_spaces(text):
    text = NEWLINES_RE.sub("\n", text)
    text = SPACES_RE.sub(" ", text)
    text = text.strip()
    return text


def save_dataframes(path, page_df, text_df, paragraph_df):
    with pd.HDFStore(os.path.join(path, 'dw.h5')) as dw_store:
        print("Saving page_df...")
        dw_store["page_df"] = page_df.drop(["soup"], axis=1)

        print("Saving text_df...")
        dw_store["text_df"] = text_df

        print("Saving paragraph_df...")
        dw_store["paragraph_df"] = paragraph_df
