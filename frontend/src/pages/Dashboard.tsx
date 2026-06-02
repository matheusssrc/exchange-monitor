import { CurrencySelect } from "@/components/CurrencySelect";
import { HistoryChart } from "@/components/HistoryChart";
import { TimeframeToggle } from "@/components/TimeframeToggle";
import { RatesTable, type RatesTableRow } from "@/components/RatesTable";
import { useAllLatestRates } from "@/hooks/useAllLatestRates";
import { usePairs } from "@/hooks/usePairs";
import { useRateHistory } from "@/hooks/useRateHistory";
import { useUrlState } from "@/hooks/useUrlState";
import { currencyLabel, pairLabel } from "@/lib/pairs";
import { buildOHLC } from "@/lib/ohlc";
import { DEFAULT_TIMEFRAME, isTimeframe, timeframeSeconds, type Timeframe } from "@/lib/ranges";

export function Dashboard() {
  const [base, setBase] = useUrlState("base", "BRL");
  const [pair, setPair] = useUrlState("pair", "BRL-USD");
  const [rawTf, setTf] = useUrlState("tf", DEFAULT_TIMEFRAME);
  const timeframe: Timeframe = isTimeframe(rawTf) ? rawTf : DEFAULT_TIMEFRAME;

  const pairs = usePairs();
  const allCodes = (pairs.data ?? []).map((p) => p.pair);
  const allLatest = useAllLatestRates(allCodes);
  const history = useRateHistory(pair);

  const candles = buildOHLC(history.data?.items ?? [], timeframeSeconds(timeframe));

  const bases = [...new Set((pairs.data ?? []).map((p) => p.base))];
  const baseOptions = bases.map((code) => ({
    value: code,
    label: currencyLabel(code),
  }));

  const pairsForBase = allCodes.filter((code) => code.startsWith(`${base}-`));
  const chartOptions = pairsForBase.map((code) => ({
    value: code,
    label: pairLabel(code),
  }));

  const tableRows: RatesTableRow[] = allLatest
    .filter((entry) => entry.pair.startsWith(`${base}-`))
    .map((entry) => ({
      pair: entry.pair,
      bid: entry.data?.bid ?? null,
      ask: entry.data?.ask ?? null,
      fetchedAt: entry.data?.fetched_at ?? null,
    }));

  function handleBaseChange(nextBase: string): void {
    setBase(nextBase);
    const firstPair = allCodes.find((code) => code.startsWith(`${nextBase}-`));
    if (firstPair) {
      setPair(firstPair);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-sm text-muted-foreground">Moeda base</span>
        <CurrencySelect
          value={base}
          onChange={handleBaseChange}
          options={baseOptions}
          ariaLabel="Moeda base"
        />
      </div>

      <RatesTable
        rows={tableRows}
        isLoading={pairs.isLoading}
        selectedPair={pair}
        onSelectPair={setPair}
      />

      <div className="flex flex-wrap items-center gap-4">
        <CurrencySelect
          value={pair}
          onChange={setPair}
          options={chartOptions}
          ariaLabel="Par do gráfico"
        />
        <TimeframeToggle value={timeframe} onChange={setTf} />
      </div>

      <div className="space-y-2">
        <h2 className="text-sm font-medium text-muted-foreground">
          {pairLabel(pair)}
        </h2>
        <HistoryChart candles={candles} isLoading={history.isLoading} />
      </div>
    </div>
  );
}
