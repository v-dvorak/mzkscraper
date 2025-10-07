import json
from typing import Optional


class PageData:
    """
    Keeps information about a single page of a document.
    """

    def __init__(self, doc_id: str, page_id: str, label: str):
        self.source = doc_id
        self.page_id = page_id
        self.label = label
        self.system_id: Optional[int] = None

    def __str__(self):
        return f'{self.source} {self.page_id} {self.label}'


class PageDataEncoder(json.JSONEncoder):
    """
    Encoder for `json` library.
    """

    def default(self, o):
        if isinstance(o, PageData):
            return {
                "source": o.source,
                "img_id": o.page_id,
                "label": o.label,
                "id": o.system_id
            }
        return super().default(o)
