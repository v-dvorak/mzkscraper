# MZK Scraper

MZK Scraper is a web scraper that enables users to search through [Moravska Zemska Knihovna](https://www.digitalniknihovna.cz/mzk) 's scanned documents based on query parameters.

The `MZKScraper` class and its methods are used to retrieve IDs of documents that align with the user's specified criteria. After this, these IDs can be used with [IIIF](https://iiif.io/) to retrieve any information about the documents, e.g. the method `get_pages_in_document` returns IDs of document's pages that can be later used to download the pages using the `download_image` method.

### Other features

`get_pages_in_document` has multiple parameters (`valid_labels`, `label_preprocessing`, `label_formatting`) that help to reject pages before processing them any further.

Passing the document ID (and optional page ID) to `open_in_browser` method opens up the specified document (and page) in default browser.

## Usage

Download this project or use it as a submodule in your own project, see [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules).
Set up a virtual environment and install necessary modules from [requirements.txt](./requirements.txt).

For example usage see [`example.py`](./example.py).

```python
from path/to/the/scraper/file import MZKScraper

# initialize scaper class
scraper = MZKScraper()

# get a complete query based on provided params
query = MZKScraper.get_search_query(authors="Komenský, Jan Amos", access="public", doctypes="monograph")

# scrape the search results
# this will retrieve document IDs that are on the second and fifth search page
results = scraper.get_search_results(query, pages=[2, 5], timeout=60)

# now we can use collected IDs and IIIF to get page IDs
pages_in_first_document = scraper.get_pages_in_document(results[0])
# page info is stored in a PageData class with attributes:
# source, page_id and label
for i, page in enumerate(pages_in_first_document):
    print(f"{i+1}: {page.page_id} label: {page.label}")

# download first page of the first document
scraper.download_image(
    pages_in_first_document[0].page_id,
    "this_is_first_page_of_the_document.jpg",
    Path("path/to/your_dir"),
    verbose=True
)
```

### [How does it work?](./docs/README.md)

## Supported query parameters

- text_query
- access
- keywords
- authors
- languages
- licenses
- locations
- publishers
- places
- genres
- doctypes
- published_from
- published_to

For more information checkout [Digital Library's documentation](https://www.digitalniknihovna.cz/help).

## Troubleshooting

### The returned list is empty:

This may be caused by invalid search query, try to open the link that is displayed along with the "Nothing found" error message. If you end at page with this message: "Attention! No results found. Please, try a different query." the query is most definitely wrong or you filters are too strict.

Check that the parameters you entered are correct. For example: passing `authors="Komensky, Jan Amos"` you'll end up with empty list, on the other hand `authors="Komenský, Jan Amos"` will be successful. Notice `y/ý`.

Try to search for desired documents manually and then use these filters as method params. After all, I made this scraper after knowing exactly how to filter out desired documents.

If the query looks ok and the page loads with some results when you open it manually, try to increase method's `timeout`. The page is loaded dynamically and in takes significantly longer to load pages with multiple filters activated.

## Useful links

- [IIIF Digital Library docs](https://iiif.digitalniknihovna.cz/)
- [downloading data from MZK for OMR tasks](https://github.com/v-dvorak/omr-layout-analysis)
- [how to use MZK Digital Library](https://www.mzk.cz/sluzby/navody/digitalni-knihovna-mzk) - long read, only in Czech
