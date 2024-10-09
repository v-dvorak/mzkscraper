# MZKScraper

MZKScraper is a Python API wrapper that enables users to search through [Moravska Zemska Knihovna](https://www.digitalniknihovna.cz/mzk) 's documents available online based on query parameters.

The `MZKScraper` class and its methods are used to retrieve UUIDs of documents that correspond to user's specified criteria. After this, these UUIDs can be used to retrieve any information about the documents via [IIIF](https://iiif.io/), e.g. the method `get_pages_in_document` returns UUIDs of document's pages that can be later used to download the pages using the `download_image` method.

The latest added features remove the necessity to dynamically load MZK webpage to get a Solr query.

### Citations

The `mzscraper` can retrieve information for proper document citations via MZK API, that can be converted in batches to `BibTeX` citations from document UUIDs (and optionally page UUID used to retrieve page number) with unique tags.

`ISO690` citations can be generated from `Citation` class, or they can be requested from MZK API as a plain text.

### Other features

`get_pages_in_document` has multiple parameters (`valid_labels`, `label_preprocessing`, `label_formatting`) that help to filter pages before processing them any further.

Passing the document ID (and optional page ID) to `open_in_browser` method opens up the specified document (and page) in default browser.

## Usage

Download this project or use it as a submodule in your own project, see [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules).
Set up a virtual environment and install necessary modules from [requirements.txt](./requirements.txt). And install this project as a package for you local environment:

```bash
python pip install -e ./mzkscraper
```

For example usage see [`example.ipynb`](./example.ipynb).

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

### The returned list is empty

This may be caused by invalid search query, verify it manually. If you end at page with message: "Attention! No results found. Please, try a different query." the query is most definitely wrong or you filters are too strict.

Check that the parameters you entered are correct. For example: passing `authors="Komensky, Jan Amos"` you'll end up with empty list, on the other hand `authors="Komenský, Jan Amos"` will be successful. Notice `y/ý`.

Try to search for desired documents manually and then use these filters as method params. After all, I made this scraper after knowing exactly how to filter out desired documents.

If the query looks ok and the page loads with some results when you open it manually, try to increase method's `timeout`. The page is loaded dynamically and in takes significantly longer to load pages with multiple filters activated.

### Handling errors

Sometimes an interaction with MZK through IIIF may result end up raising `4xx` or `5xx` error. To preserve sanity and keeping the scripts rather simple I decided to ignore these errors and to not investigate them any further. In case of error, wait a bit and try again.

## Other resources

- [valid languages for Solr query](docs/languages.json)
- [valid physical locations for Solr query](docs/physical_locations.json)

## Useful links

- [IIIF Digital Library docs](https://iiif.digitalniknihovna.cz/)
- [how to use MZK Digital Library](https://www.mzk.cz/sluzby/navody/digitalni-knihovna-mzk) - long read, only in Czech
