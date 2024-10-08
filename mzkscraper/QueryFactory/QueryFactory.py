import datetime
import json
import urllib.parse

from ..Citations.CitationUtils import join_non_empty


class MZKQueryFactory:
    def __init__(self):
        self.query_base = "(model:monograph OR model:periodical OR (model:collection AND collection.is_standalone:true) OR model:graphic OR model:map OR model:sheetmusic OR model:soundrecording OR model:archive OR model:manuscript OR model:convolute OR model:monographunit)"
        self.access: dict[str, str] = json.load(open('mzkscraper/QueryFactory/tag_data/access_tags.json', 'r'))
        self.doctypes: dict[str, str] = json.load(open('mzkscraper/QueryFactory/tag_data/doctypes_formatting.json', 'r'))
        self.licences: dict[str, str] = json.load(open('mzkscraper/QueryFactory/tag_data/licences_tags.json', 'r'))

    def _get_licence_part(self, licences: list[str]) -> str:
        return join_non_empty("OR", [
            self.licences[l] for l in licences
        ])

    def _get_doctype_part(self, doctypes: list[str]) -> str:
        return join_non_empty(" OR ", [
            self.doctypes[d] for d in doctypes
        ])

    @staticmethod
    def _get_others_part(prefix: str, others: list[str]) -> str:
        return join_non_empty(" AND ", [
            f'({prefix}"{other}")' for other in others
        ])

    @staticmethod
    def _get_date_part(published_from: int | str, published_to: int | str) -> str:
        return f"((date_range_start.year:[* TO {published_to}] AND date_range_end.year:[{published_from} TO *]))"

    def create_query(
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
        if isinstance(licences, str):
            licences = [licences]
        if isinstance(doctypes, str):
            doctypes = [doctypes]

        if isinstance(places, str):
            places = [places]
        if isinstance(publishers, str):
            publishers = [publishers]
        if isinstance(locations, str):
            locations = [locations]
        if isinstance(languages, str):
            languages = [languages]
        if isinstance(keywords, str):
            keywords = [keywords]
        if isinstance(authors, str):
            authors = [authors]
        if isinstance(geonames, str):
            geonames = [geonames]
        if isinstance(genres, str):
            genres = [genres]

        if published_from is not None or published_to is not None:
            if published_from is None:
                published_from = 0
            if published_to is None:
                published_to = datetime.datetime.now().year

        return urllib.parse.quote_plus(
            "(" + join_non_empty(" AND ", [
                self.query_base,
                self.access[access] if access is not None else "",
                ("(" + self._get_licence_part(licences) + ")") if licences is not None else "",
                ("(" + self._get_doctype_part(doctypes) + ")") if doctypes is not None else "",
                self._get_date_part(published_from, published_to) if published_from is not None else "",

                *[
                    MZKQueryFactory._get_others_part(prefix, data) for prefix, data in [
                        ("publication_places.search:", places),
                        ("publishers.search:", publishers),
                        ("physical_locations.facet:", locations),
                        ("languages.facet:", languages),
                        ("keywords.facet:", keywords),
                        ("authors.facet:", authors),
                        ("geographic_names.search:", geonames),
                        ("genres.search:", genres),
                    ] if data is not None
                ]
            ]) + ")", safe="()=:")
