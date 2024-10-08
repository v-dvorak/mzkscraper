from typing import Callable

from .BibTeX import CitationBibTeX
from .ICitation import ICitation
from .ISO690 import CitationISO690


class Citation(ICitation):
    """
    Keeps all relevant information to cite a given document or document pages.
    """

    def __init__(
            self,
            authors: list[tuple[str, str]] = None,
            title: str = None,
            subtitle: str = None,
            publisher: str = None,
            date_issued: str | int = None,
            place_issued: str = None,
            page_numbers: int | list[int] = None,
            identifiers: dict[str, str] = None,
            document_url: str = None
    ):
        super().__init__(
            authors,
            title,
            subtitle,
            publisher,
            date_issued,
            place_issued,
            page_numbers,
            identifiers,
            document_url
        )

    def get_iso_690_citation(self) -> str:
        """
        Creates and returns citation string based on ISO690.

        Read more: https://www.citace.com/CSN-ISO-690
        """
        return CitationISO690.get_iso_690_citations(self)

    def get_bibtex_citation(
            self,
            template: str = "@misc",
            indent: int = 4,
            used_tags: list[str] = None,
            default_author: str = "",
            tag_gen: Callable[[ICitation], str] = None,
    ) -> str:
        """
        Generates a string that represents a BibTeX citation.

        :param template: template for BibTeX citation
        :param indent: indentation for each citation element
        :param used_tags: list of used tags to eliminate conflicts
        :param default_author: default author for bibtex citation ("", "Anon", etc.)
        :param tag_gen: function for generating tags from Citation object for BibTeX citation
        :return: BibTeX citation string
        """
        return CitationBibTeX.get_bibtex_citation(
            self,
            template=template,
            indent=indent,
            used_tags=used_tags,
            default_author=default_author,
            tag_gen=tag_gen
        )

    def __str__(self) -> str:
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )
