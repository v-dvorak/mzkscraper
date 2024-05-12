import urllib.parse
import datetime
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


class MZKScraper:
    def __init__(self):
        # precompile regex
        self.uuid_pattern = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")

    @staticmethod
    def scrape_for_class(url, timeout: float = 60,
                         search_for: str = "ng-star-inserted",
                         wait_for=EC.any_of(
                                EC.presence_of_element_located((By.CLASS_NAME, "app-card-content-wrapper")),
                                EC.presence_of_element_located((By.CLASS_NAME, "app-alert"))
                            ),
                         log_level: int = 3):
        """
        Loads specified page, waits for a certain html objet to load or for specified time
        and then searches for a certain class.

        Parameters
        :param url: page that will be scraped
        :param timeout: timeout in seconds
        :param search_for: class that will be searched for
        :param wait_for: class that will be waited for
        :param log_level: logging level
        """
        try:
            # initialize a headless browser with Selenium
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument(f"--log-level={log_level}")
            driver = webdriver.Chrome(options=options)

            # load page
            driver.get(url)

            # wait for dynamic loading
            WebDriverWait(driver, timeout).until(
                wait_for
            )

            # parse html
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            ng_star_inserted_elements = soup.find_all(class_=search_for)

            # search for href attributes
            href_list = [element.get("href") for element in ng_star_inserted_elements]

            return href_list
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            driver.quit()

    def _clean_up_hrefs(self, hrefs: list[str | None]) -> list[str]:
        """
        Given a list of urls, returns cleaned up href list that consists only of valid uuids.

        Parameters
        :param hrefs: list of urls, elements may be None

        Returns
        :return: list of uuids
        """
        output = []
        for href in hrefs:
            if href is not None:
                # output.append(href.split(":")[1].split("?fulltext=")[0])
                match = self.uuid_pattern.search(href)
                if match is not None:
                    output.append(match.group())
        return output

    def get_search_results(self, query: str, pages: list[int] = None,
                           timeout: float = 60, max_res_per_page: int = 60) -> list[str]:
        """
        Given a search query to MZK loads the query and searches for documents inside this page. MZK search results
        are loaded dynamically.

        Parameters
        :param query: search query to MZK
        :param pages: list of pages to load, the list is sorted in increasing order before scraping begins
        :param timeout: timeout in seconds, if method doesn't return anything try to increase this timeout
        :param max_res_per_page: maximum results expected per page, if number of results is less than max_res_per_page
        a warning will be logged

        Returns
        :return: list of found documents IDs
        """
        if pages is None:
            pages = [1]

        if "page" not in query:
            query += "&page={page_num}"

        pages.sort()

        found_documents = []
        for page_num in pages:
            hrefs = self.scrape_for_class(query.format(page_num=page_num), timeout=timeout)
            hrefs = self._clean_up_hrefs(hrefs)
            if len(hrefs) == 0:
                print(f"No results found at page number {page_num}".format(page_num=page_num))
                print("at {query}.".format(query=query.format(page_num=page_num)))
                print("Quitting job.")
                break
            elif len(hrefs) < max_res_per_page:
                print(f"Warning: Found less results than expected. Expected {max_res_per_page}, got {len(hrefs)}.")
                print("at {query}.".format(query=query.format(page_num=page_num)))
            found_documents += hrefs
            page_num += 1

        return found_documents

    @staticmethod
    def get_search_query(text_query: str = "", access: str = "", keywords: str = "", authors: str = "",
                         languages: str = "", licenses: str = "", locations: str = "", publishers: str = "",
                         places: str = "", genres: str = "", doctypes: str = "",
                         published_from: str | int = "", published_to: str | int = "") -> str:
        """
        Based on inputted params returns a completed search query URL for MZK.
        """
        # both years have to be filled for the filters to work
        if published_from != "" and published_to == "":
            published_to = datetime.datetime.now().year
        elif published_from == "" and published_to != "":
            published_from = 0

        # format request and turn it into valid url (substitute special characters)
        return urllib.parse.quote_plus(
            "https://www.digitalniknihovna.cz/mzk/search?q={text_query}&access={access}&keywords={keywords}&authors={authors}&languages={languages}&licenses={licenses}&locations={locations}&publishers={publishers}&places={places}&genres={genres}&doctypes={doctypes}&from={published_from}&to={published_to}".format(
                text_query=text_query, access=access, keywords=keywords, authors=authors, languages=languages,
                licenses=licenses, locations=locations, publishers=publishers, places=places, genres=genres,
                doctypes=doctypes, published_from=published_from, published_to=published_to),
            safe="/:=&?")
