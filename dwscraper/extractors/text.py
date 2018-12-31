"""
Extract the text from the articles.
"""

import re

import pandas as pd


TEXT_DF_COLUMNS = ["url", "rubrik", "y", "artikel", "tags", "theme"]
GLOSSAR_RE = re.compile(r"glossar", re.IGNORECASE)


def extract_intro(soup):
    try:
        intro = soup.find("p", class_="intro").getText().strip()
    except AttributeError:
        return np.nan
    else:
        if not intro:
            return np.nan
        else:
            return intro


 ######### TODO: REFACTOR ALL THIS PART #########

 # https://stackoverflow.com/questions/10491223/how-can-i-turn-br-and-p-into-line-breaks/38861253
def replace_with_newlines(element):
    text = ''
    for elem in element.recursiveChildGenerator():
        if isinstance(elem, str):
            text += elem
        elif elem.name == 'br':
            text += '\n'
    return text


def get_plain_text(tag):
    plain_text = ''
    for line in tag.findAll('p'):
        line = replace_with_newlines(line)
        plain_text += line + "\n"
    return plain_text


def extract_content_DEUTSCH_LERNEN_SINGLE(soup):
    paragraphs = []
    long_text_tag = soup.find("div", class_="longText")
    """
    for tag in long_text_tag.childGenerator():
        if tag.name == "p":
            paragraphs.append(tag.get_text().strip())
        elif tag.get_text().strip().lower == "glossar":
            break
    """
    all_text = get_plain_text(long_text_tag).split("Glossar")[0].strip()
    text = GLOSSAR_RE.split(all_text)[0]
    return pd.Series({ "title": soup.h1.get_text(),
             "text": text})


def extract_content_DEUTSCH_LERNEN_MULTIPLE(soup):
    parts = [part.strip()
     for part in get_plain_text(soup.find("div", class_="longText")).split("\n")
        if part.strip()]
    return [pd.Series({"title": title, "text": text})
            for title, text in zip(parts[::2], parts[1::2])]


def extract_content_THEMEN(soup):
    return pd.Series({ "title": soup.h1.get_text(), \
             "text": get_plain_text(soup.find("div", class_="longText"))})


def extract_content_LEKTIONEN(soup):
    content_part = list(soup.find("div", class_="dkTaskWrapper tab3").children)[3]
    for definition_bubble in content_part.find_all("span"):
        definition_bubble.decompose()
    return pd.Series({ "title": soup.h1.get_text(),
             "text": get_plain_text(content_part)})

"""""
def extract_content(r):
    try:
        if r["rubrik"] == "DEUTSCH LERNEN":
            content = extract_content_DEUTSCH_LERNEN(r["soup"])
        elif r["rubrik"] == "THEMEN":
            content = extract_content_THEMEN(r["soup"])
        elif r["rubrik"] == "LEKTIONEN":
            content = extract_content_LEKTIONEN(r["soup"])
    except AttributeError:
        return np.nan
    else:
        if not content:
            return np.nan
        else:
            return content

def extract_text(df):
    print("Extracting intro...")
    df["intro"] = df["soup"].apply(extract_intro)
    print("Extracting content...")
    df["content"] = df.apply(extract_content, axis=1)
    print("Building text...")
    df["text"] = df["intro"] + df["content"]

    return df
"""


def build_text_rows(page_row):
    text_row = page_row.copy()[TEXT_DF_COLUMNS]
    text_rows = []

    if page_row["rubrik"] == "DEUTSCH LERNEN":

        if page_row["artikel"] == "Top-Thema – Podcast":
            text_row = text_row.append(extract_content_DEUTSCH_LERNEN_SINGLE(page_row["soup"]))
            text_rows = [text_row]

        elif page_row["artikel"] in {"Nachrichten", "Langsam gesprochene Nachrichten"}:
            for content in extract_content_DEUTSCH_LERNEN_MULTIPLE(page_row["soup"]):
                current_text_row = text_row.copy()
                current_text_row = current_text_row.append(content)
                text_rows.append(current_text_row)

    elif page_row["rubrik"] == "LEKTIONEN" and page_row["artikel"] == "Top-Thema – Lektionen":
        text_row = text_row.append(extract_content_LEKTIONEN(page_row["soup"]))
        text_rows = [text_row]

    elif page_row["rubrik"] == "THEMEN":
        text_row = text_row.append(extract_content_THEMEN(page_row["soup"]))
        text_rows = [text_row]

    return pd.DataFrame(text_rows)


"""
def handle_article_withot_content(df):
    article_withot_content_mask = df["content"].isnull()

    if article_withot_content_mask.any():

        print("Articles without content:")
        for url in df[article_withot_content_mask]["url"]:
            print(url)

        print("Dropping articles without content...")
        df = df[~article_withot_content_mask]

    return df
"""
