from . import CitationUtils
from .ICitation import ICitation


class CitationISO690:
    def __init__(self):
        pass

    @staticmethod
    def get_iso_690_citations(citation: ICitation) -> str:
        """
        Generates ISO 690 citations from a Citation object.

        :param citation: Citation object
        """
        return CitationUtils.join_non_empty(
            ". ",
            [
                CitationISO690._get_author_part(citation),
                CitationISO690._get_title_part(citation),
                CitationISO690._get_issued_and_page_part(citation),
                CitationISO690._get_identifiers_part(citation, identifier="isbn"),
                CitationISO690._get_url_part(citation),
            ]
        )

    @staticmethod
    def _get_author_part(citation: ICitation) -> str:
        aut = []
        for author in citation.authors:
            if author is None:
                continue
            given, family = author
            if given is not None and family is not None:
                aut.append(f"{family.upper()}, {given}")
            elif given is not None:
                aut.append(given)
            elif family is not None:
                aut.append(family.upper())

        if len(citation.authors) > 0:
            authors_cit = "; ".join(aut)
        else:
            authors_cit = "Anon"
        return authors_cit

    @staticmethod
    def _get_title_part(citation: ICitation) -> str:
        if citation.subtitle is not None:
            return f"{citation.title}: {citation.subtitle}"
        else:
            return citation.title

    @staticmethod
    def _get_issued_and_page_part(citation: ICitation) -> str:
        place_cit = None
        if citation.place_issued is not None and citation.publisher is not None:
            place_cit = f"{citation.place_issued}: {citation.publisher}"

        return CitationUtils.join_non_empty(", ", [place_cit, citation.date_issued,
                                                   CitationISO690._generate_pages_citation(citation)])

    @staticmethod
    def _generate_pages_citation(citation: ICitation) -> str:
        if len(citation.page_numbers) == 0:
            return ""
        return "s. [" + CitationUtils.join_non_empty(", ", sorted(citation.page_numbers)) + "]"

    @staticmethod
    def _get_identifiers_part(citation: ICitation, identifier: str = "isbn"):
        if citation.identifiers is None:
            return ""
        ident = citation.identifiers.get(identifier, "")
        if ident != "":
            return f"{identifier.upper()}: {ident}"
        return ""

    @staticmethod
    def _get_url_part(citation: ICitation):
        if citation.document_url is None:
            return ""
        return f"Dostupné také z: {citation.document_url}"
