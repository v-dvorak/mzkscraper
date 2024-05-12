from .Scraper import MZKScraper

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
