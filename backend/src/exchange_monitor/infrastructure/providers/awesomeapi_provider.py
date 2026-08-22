from datetime import UTC, datetime

import structlog
from pydantic import ValidationError

from exchange_monitor.application.ports.rate_provider import RateProvider
from exchange_monitor.domain.entities import ExchangeRate
from exchange_monitor.domain.value_objects import CurrencyPair
from exchange_monitor.infrastructure.bronze.raw_sink import JsonlBronzeSink

from .awesomeapi_client import AwesomeApiClient
from .awesomeapi_schema import AwesomeApiResponse
from .exceptions import ProviderResponseInvalid

log = structlog.get_logger()

PROVIDER_NAME = "awesomeapi"


class AwesomeApiProvider(RateProvider):
    def __init__(self, client: AwesomeApiClient, raw_sink: JsonlBronzeSink | None = None):
        self._client = client
        self._raw_sink = raw_sink

    async def fetch(self, pair: CurrencyPair) -> ExchangeRate:
        path = f"{pair.base}-{pair.quote}"
        payload = await self._client.fetch_last(path)

        if self._raw_sink is not None:
            self._raw_sink.write(path, payload, datetime.now(tz=UTC))

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
