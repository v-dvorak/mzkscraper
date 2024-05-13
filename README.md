# MZK Scraper

MZK Scraper is a web scraper that enables users to search through [Moravska Zemska Knihovna](https://www.digitalniknihovna.cz/mzk) 's scanned documents based on query parameters.

The `MZKScraper` class and its methods are used to retrieve IDs of documents that align with the user's specified criteria. After this, these IDs can be used with [IIIF](https://iiif.io/) to retrieve any information about the documents, e.g. IDs of document's pages that can be later used to download the pages.

## Usage

See [`example.py`](./example.py).

```python
from path/to/the/scraper/file import MZKScraper

# initialize scaper class
scraper = MZKScraper()

# get a complete query based on provided params
query = MZKScraper.get_search_query(authors="Komenský, Jan Amos", access="public", doctypes="monograph")

# scrape the search results
# this will retrieve document IDs that are on the second and fifth search page
results = scraper.get_search_results(query, pages=[2, 5], timeout=60)
```

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

Try to search for desired documents manually and then use these filters as method params. (After all I made this scraper after knowing exactly how to filter out desired documents.)

If the query looks ok and the page loads with some results when you open it manually, try to increase method's timeout, the page is loaded dynamically and in takes significantly longer to load pages with multiple filters activated.

## Motivation

The whole digital database implements the really nice and convenient to use [IIIF API](https://iiif.io/api/image/3.0/). There is only one problem with it:

I was not able to find any documentation on how to use this api to search for documents using filters. (Like "give me IDs to all sheet music documents".) And seemingly there is no other option.

## How does it work?

MZKScraper loads a page from an url with specified search filters and a page number (iterating through page numbers, the program is able to load more than 60 document IDs at once) in which it searches for this specific class `ng-star-inserted` which accompanies all the search result.

In these classes it looks for `href` and in it for `uuid` substring, when a class includes a link with this specific substring, the cryptic ID behind `uuid:` is ID of a document that corresponds to the search filters.

## Useful links

- [IIIF Digital Library docs](https://iiif.digitalniknihovna.cz/)
- [downloading data from MZK for OMR tasks](https://github.com/v-dvorak/omr-layout-analysis)
- [how to use MZK Digital Library](https://www.mzk.cz/sluzby/navody/digitalni-knihovna-mzk) - long read, only in Czech
