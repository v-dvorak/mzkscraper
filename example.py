from pathlib import Path

from .Scraper import MZKScraper
from .Citations.CitationGenerator import MZKCitationGenerator
from .Citations.BibTeX import CitationBibTeX


# initialize scaper class
scraper = MZKScraper()

# SEARCH BY AUTHOR example
# get a complete query based on provided params and print it
print()
print("SEARCH BY AUTHOR")
query = MZKScraper.get_search_query(authors="Komenský, Jan Amos", access="public", doctypes="monograph")
print(query)

# scrape the search results and print them
# this will retrieve document IDs that are on the second and fifth search page
results = scraper.get_search_results(query, pages=[2, 5], timeout=60)
print(f"Found {len(results)} results:")
print(*results, sep="\n")


# SEARCH BY TEXT example
print()
print("SEARCH BY TEXT")
# get a complete query based on provided params and print it
query = MZKScraper.get_search_query(text_query="Jan Hus", published_from=1950)
print(query)

# scrape the search results and print them
# this will retrieve document IDs that are on the first page of search results
results = scraper.get_search_results(query, timeout=60)
print(f"Found {len(results)} results:")
print(*results, sep="\n")

# GET PAGE IDS IN A DOCUMENT example
print()
print("GET PAGE IDS IN A DOCUMENT")
# now we can use collected IDs and IIIF to get page IDs
pages_in_first_document = scraper.get_pages_in_document(results[0])
# page info is stored in a PageData class with attributes:
#                           source, page_id and label
for i, page in enumerate(pages_in_first_document):
    print(f"{i + 1}: {page.page_id} label: {page.label}")

# DOWNLOAD SINGLE PAGE example
print()
print("DOWNLOAD SINGLE PAGE")
# download first page of the first document
# scraper.download_image(
#     pages_in_first_document[0].page_id,
#     "this_is_first_page_of_the_document.jpg",
#     Path("path/to/the/your_dir"),
#     verbose=True
# )

# VIEW PAGE ONLINE example
# from first document open the fifth page online
print(pages_in_first_document[4].page_id)
scraper.open_in_browser(results[0], pages_in_first_document[4].page_id)

# SEARCH FOR DOCUMENT THAT DOES NOT EXIST example
# get a complete query based on provided params and print it
print()
print("SEARCH FOR DOCUMENT THAT DOES NOT EXIST")
query = MZKScraper.get_search_query(text_query="meow meow blub meow")
print(query)

# scrape the search results and print them
# this will retrieve document IDs that are on the first page of search results
results = scraper.get_search_results(query, timeout=60)
print(f"Found {len(results)} results:")
print(*results, sep="\n")

# GENERATE CITATIONS
# initialize citation generator
citgen = MZKCitationGenerator()
doc_id = "c5a386c9-3c42-4658-a968-b7971c873cfd"
page_id = "561d95c1-3862-4a49-9ff9-9bb42599e2c9"

# retrieve info
parsed_data = citgen.retrieve_citation_data_from_document_metadata(doc_id, page_id)

if parsed_data:
    print(parsed_data.get_iso_690_citation())
    print(parsed_data.get_bibtex_citation())
