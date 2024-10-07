import re


class MZKBase:
    def __init__(self):
        self.uuid_pattern = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
        self.iiif_request_url = "https://iiif.digitalniknihovna.cz/mzk/uuid:"
        self.iiif_download_url = "https://api.kramerius.mzk.cz/search/iiif/uuid:{img_id}/full/{size}/0/default.jpg"
        self.mzk_view_page = "https://www.digitalniknihovna.cz/mzk/uuid/uuid:{doc_id}?page=uuid:{page_id}"
        self.mzk_view_document = "https://www.digitalniknihovna.cz/mzk/uuid/uuid:"
        self.document_metadata = "https://api.kramerius.mzk.cz/search/api/client/v7.0/items/uuid:{doc_id}/metadata/mods"
