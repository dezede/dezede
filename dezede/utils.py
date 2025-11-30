from bs4 import BeautifulSoup


def richtext_to_text(value: str):
    soup = BeautifulSoup(value, 'html.parser')
    for tag in soup.select('a[linktype="note-reference"]'):
        tag.extract()
    for no_space_tag in ['b', 'strong', 'i', 'em', 'a', 'sup', 'span.sc']:
        for tag in soup.select(no_space_tag):
            tag.unwrap()
    soup.smooth()  # Merges consecutive NavigableStrings.
    return soup.get_text(' ', strip=True)
