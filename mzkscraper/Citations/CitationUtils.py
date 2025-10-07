import unicodedata
from typing import Any, Iterable


def join_non_empty(sep: str, to_join: Iterable[Any]) -> str:
    """
    Given a list of strings, join them together and return the joined string.

    :param sep: Separator to join together.
    :param to_join: List of strings to join together.
    :return: Joined string.
    """
    output = ""
    first = True
    for element in to_join:
        if element != "" and element is not None:
            if first:
                output = str(element)
                first = False
            else:
                output += sep + str(element)
    return output


def clean_up_page_numbers(page_numbers: list[int | None]) -> list[int]:
    return [x for x in page_numbers if x is not None]


def strip_accents(s: str) -> str:
    """
    Strips accents from a string.

    :param s: String to strip accents from.
    :return: Stripped string.

    By "oefe" from StackOverflow:
    https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-normalize-in-a-python-unicode-string
    """
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def strip_date(date: str) -> str:
    return date.replace("[", "").replace("]", "").replace("?", "")
