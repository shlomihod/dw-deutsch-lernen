from dwscraper import scrap_dw, save_dataframes
from dwscraper.consts import DEFAULT_NUM_PARALLEL_REQUESTS


def main(path: "Path to save dataframes" = ".",
         n_pages: "Number of pages (~articles) to sample (integer or 'all'" = 'all',
         verbose: ("Whether to print additional information", "flag", "v") = False,
         n_parallel_requests: ("Number of parallel download requests", "option", "r") = DEFAULT_NUM_PARALLEL_REQUESTS):

         
    "Scrap Deutsch Lernen articles from DW website."

    n_pages = None if n_pages == 'all' else int(n_pages)

    page_df, text_df, paragraph_df = scrap_dw(n_pages,
                                              n_parallel_requests,
                                              verbose)

    save_dataframes(path, page_df, text_df, paragraph_df)


if __name__ == "__main__":
    import plac; plac.call(main)
