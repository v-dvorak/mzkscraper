# MZKScraper

**MZKScraper** is a Python API wrapper for the [Moravská Zemská Knihovna Digital Library](https://www.digitalniknihovna.cz/mzk), enabling users to search, retrieve, and process publicly available documents using flexible query parameters.

The `MZKScraper` class provides a simple interface for discovering document UUIDs that match your criteria. Once retrieved, these UUIDs can be used to access detailed information or content via the [IIIF](https://iiif.io/) API.
For example, the `get_pages_in_document` method returns UUIDs of a document’s individual pages, which can then be downloaded with the `download_image` method.

## Features

### Document Search

- Search the MZK digital collection using multiple parameters (text, authors, keywords, access rights, etc.).
- Retrieve document UUIDs for further metadata or content queries.

### Citation Retrieval

- Automatically fetch citation data from the MZK API.
- Convert document UUIDs into **BibTeX** citations with unique tags (optionally including page UUIDs for page-specific references).
- Generate **ISO 690** citations via the `Citation` class or directly from the API as plain text.

### Page Handling

- Use `get_pages_in_document` with optional parameters like `valid_labels`, `label_preprocessing`, and `label_formatting` to filter or process pages before downloading.
- Quickly open any document or page in your default web browser with `open_in_browser(document_id, page_id=None)`.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/v-dvorak/mzkscraper
```

Or use it as a **Git submodule** in your own project:

```bash
git submodule add https://github.com/v-dvorak/mzkscraper
cd mzkscraper
python -m pip install -r requirements.txt
python -m pip install -e .
```

For example usage, see [`example.ipynb`](./example.ipynb).

## Supported Query Parameters

* `text_query`
* `access`
* `keywords`
* `authors`
* `languages`
* `licenses`
* `locations`
* `publishers`
* `places`
* `genres`
* `doctypes`
* `published_from`
* `published_to`

For full details, refer to the [Digital Library documentation](https://www.digitalniknihovna.cz/help).

## Troubleshooting

### Empty Results

If no results are returned:

1. **Validate your query manually** in the digital library.
   If you see the message *“Attention! No results found. Please, try a different query.”*, the parameters may be invalid or overly restrictive.
2. **Check spelling and diacritics.**
   Example:
   - `authors="Komensky, Jan Amos"` will not find anything,
   - `authors="Komenský, Jan Amos"` will return a list of books.
3. **Try longer timeouts.**
   Pages with multiple filters take longer to load. Increase the `timeout` parameter if necessary.

### Handling API Errors

Interactions with MZK or IIIF may occasionally result in `4xx` or `5xx` errors. These are most probably issues with the source service - wait a bit and retry.
For simplicity, `MZKScraper` does not attempt to handle or retry these automatically.

## Additional Resources

- [Swagger Kramerius API Documentation](https://api.kramerius.mzk.cz/search/openapi/client/v7.0/)
- [Valid languages for Solr query](docs/languages.json)
- [Valid physical locations for Solr query](docs/physical_locations.json)
- [Solr request generator from Kramerius](https://github.com/ceskaexpedice/kramerius-web-client/blob/master/src/app/services/solr.service.ts)
- [IIIF Digital Library documentation](https://iiif.digitalniknihovna.cz/)
- [How to use the MZK Digital Library (Czech only)](https://www.mzk.cz/sluzby/navody/digitalni-knihovna-mzk)

