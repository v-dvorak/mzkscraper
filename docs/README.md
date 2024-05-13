# How does it work?

## Document IDs from search query

MZKScraper loads a page from an url with specified search filters and a page number (iterating through page numbers, the program is able to load more than 60 document IDs at once) in which it searches for this specific class `ng-star-inserted` which accompanies all the search result.

In these classes it looks for `href` and in it for `uuid` substring, when a class includes a link with this specific substring, the cryptic ID behind `uuid:` is ID of a document that corresponds to the search filters.

## Getting page IDs using document ID

Knowing the document ID we can finally use an IIIF to retrieve information about it at `https://iiif.digitalniknihovna.cz/mzk/uuid:{ID}`. We are mostly interested in the array of `"items"` that contains information about every single scanned page in this publication.

Page's label is stored as a list of labels - in our case we only consider the first one and that's usually the only one there is. And let's not get fooled - the image ID (which we can use to later download the image though IIIF) is not stored at `"id"` but rather at `"thumbnail"["id"]`.

The first one includes ID of the document itself, the second one is ID of the concrete item aka page. Also notice that the provided width and height are not the real dimensions of that image. They presumably correspond to the size of a thumbnail when the page's preview is loaded while browsing the MZK.

```json
"items": [
    {
        "id": URL1,
        "type": "Canvas",
        "label": {
            "none": [
                "[1] (sheetmusic)"
            ]
        },
        "width": 1000,
        "height": 1000,
        "thumbnail": [
            {
                "id": URL2,
                "type": "Image"
            }
    },
    ...
]
```

## Handling errors

Sometimes an interaction with MZK through IIIF may result end up raising `4xx` or `5xx` error. To preserve sanity and keeping the scraper rather simple I decided to ignore these errors and to not investigate them any further. I want to blame the MZK's inconsistency, but I can't for sure rule out that these are mistakes on my part.
