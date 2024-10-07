from collections import Counter
from typing import Callable

import nltk
from nltk.corpus import stopwords

from . import CitationUtils
from .ICitation import ICitation

nltk.download('stopwords')


class CitationBibTeX:
    def __init__(self):
        pass

    @staticmethod
    def get_bibtex_citation(
            citation: ICitation,
            template: str = "@misc",
            indent: int = 4,
            used_tags: list[str] = None,
            default_author: str = "",
            tag_gen: Callable[[ICitation], str] = None,
    ) -> str:
        """
        Generates a string that represents a BibTeX citation.

        :param citation: Citation object
        :param template: template for BibTeX citation
        :param indent: indentation for each citation element
        :param used_tags: list of used tags to eliminate conflicts
        :param default_author: default author for bibtex citation ("", "Anon", etc.)
        :param tag_gen: function for generating tags from Citation object for BibTeX citation
        :return: BibTeX citation string
        """
        if used_tags is None:
            used_tags = []

        if tag_gen is None:
            tag_gen = CitationBibTeX.base_tag_generator
        tag_base = tag_gen(citation)
        tag = tag_base

        # Rather primitive approach.
        # Iterates through possibilities "name:index" and tries them all until something works.
        # May have to be improved in the future.
        i = 1
        while tag in used_tags:
            tag = tag_base + ":" + str(i)
            i += 1

        # assemble citation string
        return f",\n{indent * ' '}".join([
            f"{template}{{{tag}",
            f"author = {{{CitationBibTeX._get_author_part(citation, default_author=default_author)}}}",
            f"title = {{{citation.title if citation.title else ''}}}",
            f"subtitle = {{{citation.subtitle if citation.subtitle else ''}}}",
            f"publisher = {{{citation.publisher if citation.publisher else ''}}}",
            f"year = {{{citation.date_issued if citation.date_issued else ''}}}",
            f"pages = {{{CitationUtils.join_non_empty(', ', citation.page_numbers)}}}",
            f"isbn = {{{citation.identifiers.get('isbn', '')}}}",
            f"url = {{{citation.document_url if citation.document_url else ''}}}",
        ]) + "\n}"

    @staticmethod
    def base_tag_generator(citation: ICitation) -> str:
        """
        Creates tag for citation by combining first authors family name and year, if both are not None.
        If they are, tries given name. When none of the above work, resorts to generating tag from document name.

        :param citation: Citation object
        :return: Tag string
        """
        if citation.authors[0][1] is not None:
            tag = CitationUtils.strip_accents(citation.authors[0][1])
            if citation.date_issued is not None:
                return tag + CitationUtils.strip_date(citation.date_issued)
            return tag

        elif citation.authors[0][0] is not None:
            tag = CitationUtils.strip_accents(citation.authors[0][0])
            if citation.date_issued is not None:
                return tag + CitationUtils.strip_date(citation.date_issued)
            return tag

        else:
            stopwords_dict = Counter(stopwords.words('english'))
            tag = "".join([
                              CitationUtils.strip_accents(word).capitalize()
                              for word in citation.title.split() if word not in stopwords_dict
                          ][:2])
            if citation.date_issued is not None:
                return tag + CitationUtils.strip_date(citation.date_issued)
            return tag

    @staticmethod
    def _get_author_part(citation: ICitation, default_author: str = "") -> str:
        authors = CitationUtils.join_non_empty(
            " and ", [CitationUtils.join_non_empty(" ", author) for author in citation.authors])
        if authors == "":
            return default_author
        return authors
