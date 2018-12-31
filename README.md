# Deutsche Welle - Deutsch Lernen - Scraper

Toolbox for scraping [Deutsch Lernen](https://www.dw.com/) section in [Deutsche Welle](https://www.dw.com/de/deutsch-lernen/s-2055) website.

The articles are leveled by the [CEFR](https://en.wikipedia.org/wiki/Common_European_Framework_of_Reference_for_Languages).

## Requirements
Python 3.6

## Setup

1. Install `pipenv`:

```shell
$ pip install pipenv
```

2. Install the required packages from the project folder:

```shell
$ pipenv sync
```

## Usage

```shell
$ pipenv run python scrap_dw.py
```

```
usage: scrap_dw.py [-h] [-v] [path] [n_pages]

Scrap Deutsch Lernen articles from DW website.

positional arguments:
  path           Path to save data frames
  n_pages        Number of pages (~articles) to sample (integer or 'all'

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Whether to print additional information
```

## Resulted Data

Three pandas' data frames will be stored in a HDF5 `dw.h5` file in the `path` argument directory:

1. `page_df` - The web page that were scraped.
2. `text_df` - The leveled texts from each web page.
3. `paragraph_df` - The leveled texts splitted by paragraphs (each row is a paragraph).

The `dw.h5` can be opened with `pandas`:

```python
import pandas as pd

with pd.HDFStore('dw.h5') as dw_store:
    page_df = dw_store['page_df']
    text_df = dw_store['text_df']
    paragraph_df = dw_store['paragraph_df']
```

### `text_df` columns

1. `text` - The text itself.
2. `y` - The text level by the CEFR.
3. `tags` & `themes` - tags that are extracted from the web page (Schlagwörter & Themenseiten)

### Levels - `y` column in `text_df` and `paragraph_df`

```
0 - B1
1 - B2, C1
```

## Notebooks

1. [Corpus building decisions documentation](notebooks/corpus-building-decisions-documentation.ipynb)
2. [Basic EDA](notebooks/basic-EDA.ipynb)

## TODO

- [ ] Convert to a Python package
- [ ] Better documentation of the data frames' columns
