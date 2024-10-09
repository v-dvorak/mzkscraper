import requests
import xml.etree.ElementTree as ET
from collections import defaultdict

from .. import ScraperUtils
from ..MZKBase import MZKBase
from .Citation import Citation


class MZKCitationGenerator(MZKBase):
    """
    Generates Citation objects based on given document ID and optional page ID.
    """
    def __init__(self):
        super().__init__()

    def _get_image_id_from_mzk_json(self, img_json: dict) -> str:
        return self.uuid_pattern.search(img_json["thumbnail"][0]["id"]).group(0)

    @staticmethod
    def get_iso_690_citation_directly(uuid: str, italic=True) -> str:
        """
        Using MZK API, can cite document or a specific page. Returns plain text citation.

        :param uuid: document or page id
        :param italic: whether to include italic text styling, default is True
        """
        citation_url = "https://citace.kramerius.cloud/v1/kramerius?url=https://api.kramerius.mzk.cz&uuid=uuid:{doc_id}&format=html&lang=en&k7=true"

        response = requests.get(citation_url.format(doc_id=uuid))

        if response.status_code == 200:
            if not italic:
                return response.text.replace("<i>", "").replace("</i>", "")
            return response.text
        else:
            print(f"Returned {response.status_code}")
            return None

    def get_page_number_from_document(self, doc_id: str, page_id: str) -> int:
        """
        Requests metadata of a document via `doc_id` from library and tries to match page number to `page_id`.
        In case of failure, -1 is returned.

        :param doc_id: document ID
        :param page_id: page ID

        :return: page number or -1 if failure
        """
        page_info = ScraperUtils.get_json_from_url(self.iiif_request_url + doc_id)
        if page_info is None:
            return -1

        try:
            for page_number, sheet in enumerate(page_info["items"]):
                current_page_id = self._get_image_id_from_mzk_json(sheet)
                if current_page_id == page_id:
                    return page_number
        except TypeError:
            return -1

    def retrieve_citation_data_from_document_metadata(self, doc_id: str, page_id: str = None) -> Citation | None:
        """
        Requests document metadata from library and finds all relevant information for proper citation.

        :param doc_id: document ID
        :param page_id: page ID, optional, returns page number only if page_id is provided

        :return: Citation object or None if failure
        """
        # request metadata
        response = requests.get(
            self.document_metadata.format(doc_id=doc_id),
        )
        if page_id is not None:
            page_number = self.get_page_number_from_document(doc_id, page_id)
        else:
            page_number = None

        if response.status_code == 200:
            xml_content = response.content

            tree = ET.ElementTree(ET.fromstring(xml_content))
            root = tree.getroot()
            ns = {"mods": "http://www.loc.gov/mods/v3"}

            # ==============================
            # DATE, PLACE, PUBLISHER
            # ==============================
            # dateIssued
            date_issued = root.find(".//mods:dateIssued", ns)
            date_issued_text = date_issued.text if date_issued is not None else None

            # placeIssued
            place_issued = root.find('.//mods:placeTerm[@type="text"]', ns)
            place_issued_text = place_issued.text if place_issued is not None else None

            # publisher
            publisher = root.find(".//mods:publisher", ns)
            publisher_text = publisher.text if publisher is not None else None

            # ==============================
            # IDENTIFIERS
            # ==============================
            identifiers = root.findall(".//mods:identifier", ns)
            identifier_dict = {}
            for identifier in identifiers:
                identifier_type = identifier.attrib.get("type")
                identifier_value = identifier.text
                identifier_dict[identifier_type] = identifier_value

            # ==============================
            # TITLE, SUBTITLE
            # ==============================
            titles = root.find("./mods:mods/mods:titleInfo", ns)
            main_title = titles.find("./mods:title", ns)
            subtitle = titles.find("./mods:subTitle", ns)
            main_title_text = main_title.text if main_title is not None else None
            subtitle_text = subtitle.text if subtitle is not None else None

            # ==============================
            # AUTHORS
            # ==============================
            names = root.findall('./mods:mods/mods:name[@type="personal"]', ns)
            primary_list = []
            other_list = []

            # iterate through authors
            for name in names:
                usage = name.attrib.get("usage")

                family_name = name.find('.//mods:namePart[@type="family"]', ns)
                given_name = name.find('.//mods:namePart[@type="given"]', ns)
                family_name_text = family_name.text if family_name is not None else None
                given_name_text = given_name.text if given_name is not None else None

                # try to search for non "family, given" name
                if family_name_text is None and given_name_text is None:
                    name = name.find('.//mods:namePart', ns)
                    name_text = name.text if name is not None else None
                    # mess in MZK metadata, full name maybe in on "namepart"
                    if ", " in name_text:
                        tmp = name_text.split(", ")
                        name_tuple = (tmp[1], tmp[0])
                    else:
                        name_tuple = (name_text, None)
                else:
                    name_tuple = (given_name_text, family_name_text)

                # primary author has to be first
                if usage == "primary":
                    primary_list.append(name_tuple)
                else:
                    other_list.append(name_tuple)

            authors = primary_list + other_list

            return Citation(
                authors=authors,
                title=main_title_text,
                subtitle=subtitle_text,
                publisher=publisher_text,
                date_issued=date_issued_text,
                place_issued=place_issued_text,
                page_numbers=[page_number],
                identifiers=identifier_dict,
                document_url=self.mzk_view_document + doc_id
            )
        else:
            return None

    @staticmethod
    def _flatten(xss: list[list[any]]) -> list[any]:
        return [x for xs in xss for x in xs]

    @staticmethod
    def group_page_citation_by_document_id(citations: list[Citation]) -> list[Citation]:
        """
        Given a list of Citations, this method joins them by document ID and updates page numbers in the new Citations.

        :param citations: list of Citations
        :return: list of Citations
        """
        grouped = defaultdict(list)
        combined: list[Citation] = []

        for cit in citations:
            grouped[cit.document_url].append(cit)

        for group in grouped.values():
            if len(group) > 1:
                nums = MZKCitationGenerator._flatten([cit.page_numbers for cit in group])
                # take data from first document, all were parsed from the same doc
                combined.append(Citation(
                    authors=group[0].authors,
                    title=group[0].title,
                    subtitle=group[0].subtitle,
                    date_issued=group[0].date_issued,
                    place_issued=group[0].place_issued,
                    page_numbers=nums,
                    identifiers=group[0].identifiers,
                    document_url=group[0].document_url
                ))
            else:
                combined.append(group[0])

        return combined
