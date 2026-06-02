import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  type TooltipContentProps,
  XAxis,
  YAxis,
} from "recharts";

import { StateMessage } from "@/components/StateMessage";
import { Card, CardContent } from "@/components/ui/card";
import { formatNumber, formatTimestamp } from "@/lib/format";
import type { Candle } from "@/lib/ohlc";

interface HistoryChartProps {
  candles: Candle[];
  isLoading: boolean;
}

interface CandleDatum extends Candle {
  range: [number, number];
}

const BULL = "#10b981";
const BEAR = "#ef4444";

interface CandleShapeProps {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  payload?: CandleDatum;
}

function renderCandle(props: CandleShapeProps) {
  const { x, y, width, height, payload } = props;
  if (
    x === undefined ||
    y === undefined ||
    width === undefined ||
    height === undefined ||
    !payload
  ) {
    return <g />;
  }
  const { open, close, high, low } = payload;
  const color = close >= open ? BULL : BEAR;
  const span = high - low || 1;
  const ratio = height / span;
  const priceY = (price: number) => y + (high - price) * ratio;
  const bodyTop = priceY(Math.max(open, close));
  const bodyHeight = Math.max(Math.abs(close - open) * ratio, 1);
  const centerX = x + width / 2;
  const bodyX = x + width * 0.25;
  const bodyWidth = Math.max(width * 0.5, 1);
  return (
    <g>
      <line x1={centerX} x2={centerX} y1={y} y2={y + height} stroke={color} strokeWidth={1} />
      <rect x={bodyX} y={bodyTop} width={bodyWidth} height={bodyHeight} fill={color} />
    </g>
  );
}

function OhlcTooltip({ active, payload }: TooltipContentProps) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }
  const candle = payload[0]?.payload as CandleDatum | undefined;
  if (!candle) {
    return null;
  }
  return (
    <div className="rounded-md border border-border bg-card p-2 text-xs text-card-foreground">
      <div className="mb-1 font-medium">
        {formatTimestamp(new Date(candle.time).toISOString())}
      </div>
      <div className="grid grid-cols-2 gap-x-3 tabular-nums">
        <span>O {formatNumber(candle.open)}</span>
        <span>H {formatNumber(candle.high)}</span>
        <span>L {formatNumber(candle.low)}</span>
        <span>C {formatNumber(candle.close)}</span>
      </div>
    </div>
  );
}

interface PriceTagProps {
  viewBox?: { x?: number; y?: number; width?: number; height?: number };
  value?: number;
}

const TAG_WIDTH = 60;
const TAG_HEIGHT = 18;

/** Renders the current-price label as a solid badge anchored to the right edge,
 * sitting on the dashed tracker line (like a trading platform's last-price tag). */
function PriceTag({ viewBox, value }: PriceTagProps) {
  if (!viewBox || value === undefined) {
    return <g />;
  }
  const x = viewBox.x ?? 0;
  const y = viewBox.y ?? 0;
  const width = viewBox.width ?? 0;
  const tagX = x + width - TAG_WIDTH;
  return (
    <g>
      <rect
        x={tagX}
        y={y - TAG_HEIGHT / 2}
        width={TAG_WIDTH}
        height={TAG_HEIGHT}
        rx={3}
        fill="hsl(var(--foreground))"
      />
      <text
        x={tagX + TAG_WIDTH / 2}
        y={y + 4}
        textAnchor="middle"
        fontSize={11}
        fill="hsl(var(--background))"
      >
        {formatNumber(value)}
      </text>
    </g>
  );
}

export function HistoryChart({ candles, isLoading }: HistoryChartProps) {
  const data: CandleDatum[] = candles.map((candle) => ({
    ...candle,
    range: [candle.low, candle.high],
  }));
  const lastClose = data.at(-1)?.close;

  return (
    <Card>
      <CardContent className="pt-6">
        {isLoading ? (
          <StateMessage variant="loading" />
        ) : data.length === 0 ? (
          <StateMessage
            variant="empty"
            title="Sem dados no período"
            description="Aguarde novos ticks para formar os candles."
          />
        ) : (
          <div className="space-y-3">
            <div className="h-[360px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={data}
                  barCategoryGap="20%"
                  margin={{ top: 8, right: 8, bottom: 0, left: 8 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis
                    dataKey="time"
                    tickFormatter={(t: number) => formatTimestamp(new Date(t).toISOString())}
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={11}
                    minTickGap={40}
                  />
                  <YAxis
                    orientation="right"
                    domain={["auto", "auto"]}
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={11}
                    width={70}
                    tickFormatter={(v: number) => formatNumber(v)}
                  />
                  <Tooltip content={(props) => <OhlcTooltip {...props} />} />
                  <Bar
                    dataKey="range"
                    isAnimationActive={false}
                    shape={(props: unknown) => renderCandle(props as CandleShapeProps)}
                  />
                  {lastClose !== undefined ? (
                    <ReferenceLine
                      y={lastClose}
                      stroke="hsl(var(--foreground))"
                      strokeDasharray="3 3"
                      ifOverflow="extendDomain"
                      label={(props: unknown) => (
                        <PriceTag {...(props as PriceTagProps)} value={lastClose} />
                      )}
                    />
                  ) : null}
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
              <span>
                <strong className="text-foreground">O</strong> Abertura
              </span>
              <span>
                <strong className="text-foreground">H</strong> Máxima
              </span>
              <span>
                <strong className="text-foreground">L</strong> Mínima
              </span>
              <span>
                <strong className="text-foreground">C</strong> Fechamento
              </span>
              <span className="flex items-center gap-1">
                <span
                  className="inline-block h-2 w-2 rounded-sm"
                  style={{ backgroundColor: BULL }}
                />
                Alta (C ≥ O)
              </span>
              <span className="flex items-center gap-1">
                <span
                  className="inline-block h-2 w-2 rounded-sm"
                  style={{ backgroundColor: BEAR }}
                />
                {"Baixa (C < O)"}
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
