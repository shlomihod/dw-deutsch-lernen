from dwscraper import scrap_dw, save_dataframes


def main(path: "Path to save dataframes" = ".",
         n_pages: "Number of pages (~articles) to sample (integer or 'all'" = 'all',
         verbose: ("Whether to print additional information", "flag", "v") = False):
    "Scrap Deutsch Lernen articles from DW website."

    n_pages = None if n_pages == 'all' else int(n_pages)

    page_df, text_df, paragraph_df = scrap_dw(n_pages, verbose)

    save_dataframes(path, page_df, text_df, paragraph_df)


if __name__ == "__main__":
    import plac; plac.call(main)
