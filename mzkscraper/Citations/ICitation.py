from . import CitationUtils


class ICitation:
    """
    Interface. Keeps all relevant information to cite a given document or document pages.
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
            document_url: str = None,
    ):
        if authors is None:
            self.authors = []
        else:
            self.authors = authors

        self.title = title
        self.subtitle = subtitle

        self.publisher = publisher
        self.date_issued = date_issued
        self.place_issued = place_issued

        if page_numbers is None:
            self.page_numbers = []
        elif isinstance(page_numbers, int):
            self.page_numbers = [page_numbers]
        else:
            self.page_numbers = page_numbers
        self.page_numbers = CitationUtils.clean_up_page_numbers(self.page_numbers)

        self.identifiers = identifiers

        self.document_url = document_url
