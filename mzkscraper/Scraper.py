import datetime
import inflection
import requests
import time
import urllib.parse
from PIL import Image
from io import BytesIO
from pathlib import Path
from seleniumwire import webdriver
from tqdm import tqdm
from typing import Callable

from . import ScraperUtils
from .MZKBase import MZKBase
from .PageData import PageData
from .QueryFactory.QueryFactory import QueryFactory


class MZKScraper(MZKBase):
    def __init__(self):
        super().__init__()
        self.query_factory = QueryFactory()

    def retrieve_document_ids_by_solr_query(
            self,
            query: str,
            requested_document_count: int | str = "all",
            batch_size: int = 100,
    ) -> list[str]:
        """
        Search documents by Solr query in MZK.

        :param query: search query in Solr format
        :param requested_document_count: requested number of pages, "all" for all documents
        :param batch_size: batch size, defaults to 100; this many documents will be requested at once
        """
        # set number of document ids to retrieve
        total_document_count = self._get_number_of_documents_available(query)
        if requested_document_count == "all":
            to_retrieve = total_document_count
        else:
            to_retrieve = min(total_document_count, requested_document_count)

        # retrieve documents in batches
        output = []
        offset = 0
        for _ in tqdm(range(to_retrieve // batch_size + 1)):
            if to_retrieve <= 0:
                break

            # request ids
            result = ScraperUtils.get_json_from_url(
                "https://api.kramerius.mzk.cz/search/api/client/v7.0/search?q=*:*&fq="
                + query
                + f"&rows={min(batch_size, to_retrieve)}&start={offset}"
            )

            for doc in result["response"]["docs"]:
                output.append(doc["pid"][5:])
                offset += 1
                to_retrieve -= 1

        return output

    @staticmethod
    def _get_number_of_documents_available(query: str) -> int:
        """
        Returns the number of documents available in MZK based on Solr query.

        :param query: Solr query
        """
        result = ScraperUtils.get_json_from_url(
            "https://api.kramerius.mzk.cz/search/api/client/v7.0/search?q=*:*&fq=" + query + "&rows=0&start=0"
        )
        return int(result["response"]["numFound"])

    def construct_solr_query_with_qf(
            self,
            access: str = None,
            licences: list[str] | str = None,
            doctypes: list[str] | str = None,
            published_from: str | int = None,
            published_to: str | int = None,

            places: list[str] | str = None,
            publishers: list[str] | str = None,
            locations: list[str] | str = None,
            languages: list[str] | str = None,
            keywords: list[str] | str = None,
            authors: list[str] | str = None,
            geonames: list[str] | str = None,
            genres: list[str] | str = None
    ) -> str:
        """
        Constructs Solr query for document retrieval using reverse-engineered QueryFactory.
        """
        return self.query_factory.create_query(
            access=access,
            licences=licences,
            doctypes=doctypes,
            published_from=published_from,
            published_to=published_to,

            places=places,
            publishers=publishers,
            locations=locations,
            languages=languages,
            keywords=keywords,
            authors=authors,
            geonames=geonames,
            genres=genres,
        )

    @staticmethod
    def construct_hm_query(
            text_query: str = "",
            access: str = "",
            keywords: str = "",
            authors: str = "",
            languages: str = "",
            licences: str = "",
            locations: str = "",
            publishers: str = "",
            places: str = "",
            genres: str = "",
            doctypes: str = "",
            published_from: str | int = "",
            published_to: str | int = "",
    ) -> str:
        """
        Based on inputted params returns a completed human-readable URL.
        """
        # both years have to be filled for the filters to work
        if published_from != "" and published_to == "":
            published_to = datetime.datetime.now().year
        elif published_from == "" and published_to != "":
            published_from = 0

        # format request and turn it into valid url (substitute special characters)
        return "https://www.digitalniknihovna.cz/mzk/search?" + urllib.parse.urlencode(
            {
                "text_query": text_query,
                "access": access,
                "keywords": keywords,
                "authors": authors,
                "languages": languages,
                "licences": licences,
                "locations": locations,
                "publishers": publishers,
                "places": places,
                "genres": genres,
                "doctypes": doctypes,
                "published_from": published_from,
                "published_to": published_to,
            }
        )

    @staticmethod
    def transform_query_from_hm_to_solr_using_mzk(query: str, timeout: int = 3) -> str:
        """
        Dynamically loads MZK search page, triggering an XHR request that includes the wanted Solr search query.

        :param query: human-readable search query
        :param timeout: timeout in seconds, defaults to 3
        """
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)

        try:
            # load page and wait a bit
            driver.get(query)
            time.sleep(timeout)

            # listen to XHR requests
            for request in driver.requests:
                if request.response and "https://api.kramerius.mzk.cz/search/api/client/v7.0/search" in request.url:
                    driver.quit()
                    return MZKScraper._clean_up_query(request.url)
        except Exception as e:
            print(f"Error: {e}")
            driver.quit()

    @staticmethod
    def _clean_up_query(query: str) -> str:
        return query.split("&")[1][3:]

    @staticmethod
    def _strip_page_label(label: str) -> str:
        # remove brackets
        return label.split(" ")[1].replace("(", "").replace(")", "")

    def _get_image_id(self, img_json: dict) -> str:
        return self.uuid_pattern.search(img_json["thumbnail"][0]["id"]).group(0)

    def get_pages_in_document(
            self,
            doc_id: str,
            valid_labels: list[str] = None,
            label_preprocessing: Callable[[str], str] = None,
            label_formatting: Callable[[str], str] = inflection.underscore,
    ) -> list[PageData] | None:
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
            return self.extract_page_ids_from_document(
                page_data,
                valid_labels=valid_labels,
                label_preprocessing=label_preprocessing,
                label_formatting=label_formatting,
            )
        else:
            return None

    def extract_page_ids_from_document(
            self,
            page_info: dict[str, str],
            valid_labels: list[str] = None,
            label_preprocessing: Callable[[str], str] = None,
            label_formatting: Callable[[str], str] = inflection.underscore,
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
            label_preprocessing = MZKScraper._strip_page_label

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
                        output.append(
                            PageData(
                                doc_id,
                                self._get_image_id(sheet),
                                label_formatting(label),
                            )
                        )
                except IndexError:
                    continue

        return output

    def _get_img_request_url(self, img_id: str, size: str) -> str:
        return self.iiif_download_url.format(img_id=img_id, size=size)

    def download_image(
            self,
            img_id: str,
            file_name: str,
            output_dir: Path,
            size: str = "^!640,640",
            verbose=False,
    ):
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
            with open(filepath, "wb") as file:
                file.write(response.content)
            if verbose:
                print(f"Image downloaded: {file_name}")
        else:
            print(f"Error: {response.status_code}")

    def get_image(self, img_id: str, size: str = "^!640,640", verbose=False) -> Image:
        """
        Given an image ID downloads it to specified directory.

        :param img_id: image ID
        :param size: size of image, for more see IIIF docs
        :param verbose: verbose mode
        """
        # download the corresponding image using url
        url = self._get_img_request_url(img_id, size)
        response = requests.get(url)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            print(f"Error: {response.status_code}")
            return None
