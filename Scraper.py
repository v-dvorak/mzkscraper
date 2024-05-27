import urllib.parse
import datetime
import re
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import inflection
from typing import Callable
from pathlib import Path
import requests
import webbrowser

from . import ScraperUtils
from .PageData import PageData


class MZKScraper:
    def __init__(self):
        # precompile regex
        self.uuid_pattern = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
        self.iiif_request_url = "https://iiif.digitalniknihovna.cz/mzk/uuid:"
        self.iiif_download_url = "https://api.kramerius.mzk.cz/search/iiif/uuid:{img_id}/full/{size}/0/default.jpg"
        self.mzk_view = "https://www.digitalniknihovna.cz/mzk/view/uuid:{doc_id}?page=uuid:{page_id}"

    @staticmethod
    def scrape_for_class(url, timeout: float = 60,
                         search_for: str = "ng-star-inserted",
                         wait_for=EC.any_of(
                             EC.presence_of_element_located((By.CLASS_NAME, "app-card-content-wrapper")),
                             EC.presence_of_element_located((By.CLASS_NAME, "app-alert"))
                         ),
                         log_level: int = 3) -> list[str]:
        """
        Loads specified page, waits for a certain html objet to load or for specified time
        and then searches for a certain class.

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
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
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

        :param hrefs: list of urls, elements may be None

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
                           timeout: float = 60, max_res_per_page: int = 60,
                           verbose: bool = False) -> list[str]:
        """
        Given a search query to MZK loads the query and searches for documents inside this page. MZK search results
        are loaded dynamically.

        :param query: search query to MZK
        :param pages: list of pages to load, the list is sorted in increasing order before scraping begins
        :param timeout: timeout in seconds, if method doesn't return anything try to increase this timeout
        :param max_res_per_page: maximum results expected per page, if number of results is less than max_res_per_page
        a warning will be logged
        :param verbose: make method verbose

        :return: list of found documents IDs
        """
        if pages is None:
            pages = [1]

        if "page" not in query:
            query += "&page={page_num}"

        pages.sort()

        found_documents = []
        for page_num in tqdm(pages, disable=verbose):
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
            "https://www.digitalniknihovna.cz/mzk/search?q={text_query}&access={access}&keywords={keywords}&authors={authors}&languages={languages}&licences={licenses}&locations={locations}&publishers={publishers}&places={places}&genres={genres}&doctypes={doctypes}&from={published_from}&to={published_to}".format(
                text_query=text_query, access=access, keywords=keywords, authors=authors, languages=languages,
                licenses=licenses, locations=locations, publishers=publishers, places=places, genres=genres,
                doctypes=doctypes, published_from=published_from, published_to=published_to),
            safe="/:=&?")

    @staticmethod
    def _strip_page_label(label: str) -> str:
        return label.split(" ")[1].replace("(", " ").replace(")", "").replace(" ", "")

    def _get_image_id(self, img_json: dict) -> str:
        return self.uuid_pattern.search(img_json["thumbnail"][0]["id"]).group(0)

    def get_pages_in_document(self, doc_id: str, valid_labels: list[str] = None,
                              label_preprocessing: Callable[[str], str] = None,
                              label_formatting: Callable[[str], str] = inflection.underscore) -> list[PageData] | None:
        """
        Sends request to MZK using IIIF and parses information about all pages inside a document.
        Returns list of `ImageData` objects. If request fails, returns `None`.

        :param doc_id: Document ID
        :param valid_labels: list of valid labels strings, if None all labels are valid
        :param label_preprocessing: function that takes text retrieved from IIIF call and returns preprocessed label
        :param label_formatting: function that takes label and returns formatted label

        :return: List of `ImageData` objects or None, if request fails
        """
        page_data = ScraperUtils.get_json_from_url(self.iiif_request_url + doc_id)
        if page_data is not None:
            return self.extract_page_ids_from_document(page_data,
                                                       valid_labels=valid_labels,
                                                       label_preprocessing=label_preprocessing,
                                                       label_formatting=label_formatting)
        else:
            return None

    def extract_page_ids_from_document(self, page_info: dict[str, str], valid_labels: list[str] = None,
                                       label_preprocessing: Callable[[str], str] = None,
                                       label_formatting: Callable[[str], str] = inflection.underscore
                                       ) -> list[PageData]:
        """
        Processes JSON with information about all pages inside a document.
        Returns list of `ImageData` objects.

        :param page_info: JSON-like object with page information
        :param valid_labels: list of valid labels strings, if None all labels are valid
        :param label_preprocessing: function that takes text retrieved from IIIF call and returns preprocessed label
        :param label_formatting: function that takes label and returns formatted label

        :return: List of `ImageData` objects or None, if request fails
        """
        if label_preprocessing is None:
            label_preprocessing = self._strip_page_label

        output = []
        doc_id = page_info["id"]
        for sheet in page_info["items"]:
            labels = sheet["label"]["none"]
            if len(labels) > 1:
                print("Warning: more labels then expected:", labels)
            else:
                try:
                    label = label_preprocessing(labels[0])
                    if valid_labels is None or label in valid_labels:
                        output.append(PageData(doc_id, self._get_image_id(sheet), label_formatting(label)))
                except IndexError:
                    continue

        return output

    def _get_img_request_url(self, img_id: str, size: str) -> str:
        return self.iiif_download_url.format(img_id=img_id, size=size)

    def download_image(self, img_id: str, file_name: str, output_dir: Path,
                       size: str = "^!640,640",
                       verbose=False):
        """
        Given an image ID downloads it to specified directory.

        :param img_id: image ID
        :param file_name: output file name, with extension
        :param output_dir: output directory
        :param size: size of image, for more see IIIF docs
        :param verbose: verbose mode
        """
        # create the output directory if it doesn't exist
        output_dir.mkdir(exist_ok=True, parents=True)

        # download the corresponding image using url
        url = self._get_img_request_url(img_id, size)
        response = requests.get(url)
        if response.status_code == 200:
            filepath = Path(output_dir / file_name)
            # write to file
            with open(filepath, 'wb') as file:
                file.write(response.content)
            if verbose:
                print(f"Image downloaded: {file_name}")
        else:
            print(f"Error: {response.status_code}")

    def open_in_browser(self, doc_id: str, page_id: str = None):
        """
        Given a document ID and a page ID, opens the document in MZK in your default browser.
        Page ID is optional.

        :param doc_id: document ID
        :param page_id: page ID
        """
        webbrowser.open(self.mzk_view.format(doc_id=doc_id, page_id=page_id))

    @staticmethod
    def scrape_for_page_count(url, timeout: float = 60,
                              search_for: str = "waves-effect ng-star-inserted",
                              wait_for=EC.any_of(
                                  EC.presence_of_element_located((By.CLASS_NAME, "app-card-content-wrapper")),
                                  EC.presence_of_element_located((By.CLASS_NAME, "app-alert")),
                                  EC.presence_of_element_located((By.CLASS_NAME, "waves-effect ng-star-inserted"))
                              ),
                              log_level: int = 3) -> int:
        """
        Returns the number of pages occupied by the search results. Returns `-1` when unsuccessful.

        Loads first page of specified query, waits for `app-card-content-wrapper` or `app-alert` classes to load or for specified time
        and then searches for a `waves-effect ng-star-inserted` class.

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
            element_search_results = soup.find_all(class_=search_for)

            # search for href attributes
            page_nums = [element.find("a").contents for element in element_search_results]

            # edge case, when results fit on one page, buttons with page numbers do not appear
            if len(page_nums) == 0:
                return 1
            else:
                page_nums = [int(num[0]) for num in page_nums]
                return max(page_nums)

        except Exception as e:
            print(f"Error: {e}")
            return -1
        finally:
            driver.quit()
