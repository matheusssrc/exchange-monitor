from datetime import UTC, datetime

import structlog
from pydantic import ValidationError

from trillia_monitor.application.ports.rate_provider import RateProvider
from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair

from .awesomeapi_client import AwesomeApiClient
from .awesomeapi_schema import AwesomeApiResponse
from .exceptions import ProviderResponseInvalid

log = structlog.get_logger()

PROVIDER_NAME = "awesomeapi"


class AwesomeApiProvider(RateProvider):
    def __init__(self, client: AwesomeApiClient):
        self._client = client

    async def fetch(self, pair: CurrencyPair) -> ExchangeRate:
        path = f"{pair.base}-{pair.quote}"
        payload = await self._client.fetch_last(path)

        try:
            parsed = AwesomeApiResponse.parse_raw_dict(payload)
        except ValidationError as exc:
            log.error("provider.parse_failed", pair=str(pair), errors=exc.errors())
            raise ProviderResponseInvalid(f"invalid awesomeapi payload for {pair}") from exc

        key = f"{pair.base}{pair.quote}"
        quote = parsed.quotes.get(key)
        if quote is None:
            raise ProviderResponseInvalid(f"missing quote {key} in response")

        return ExchangeRate(
            pair=pair,
            bid=quote.bid,
            ask=quote.ask,
            fetched_at=datetime.now(tz=UTC),
            provider_timestamp=quote.timestamp,
            provider_name=PROVIDER_NAME,
        )
