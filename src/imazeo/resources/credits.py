from __future__ import annotations
from imazeo.api_types import CreditQuote, CreditQuoteInput
from imazeo.resources.project import ProjectResource
class CreditsResource(ProjectResource):
    def quote(self, input: CreditQuoteInput) -> CreditQuote:
        return self._http.request_json('POST', self._url('credits', 'quote'), body=input).data
