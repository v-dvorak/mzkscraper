import json


class PageData:
    """
    Keeps information about a single page of a document.
    """
    def __init__(self, doc_id: str, page_id: str, label: str):
        self.source = doc_id
        self.page_id = page_id
        self.label = label

    def __str__(self):
        return f'{self.source} {self.page_id} {self.label}'


class PageDataEncoder(json.JSONEncoder):
    """
    Encoder for `json` library.
    """
    def default(self, obj):
        if isinstance(obj, PageData):
            return {
                "source": obj.source,
                "img_id": obj.page_id,
                "label": obj.label
            }
        return super().default(obj)
