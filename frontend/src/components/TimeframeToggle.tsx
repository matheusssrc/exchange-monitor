import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { TIMEFRAMES, type Timeframe } from "@/lib/ranges";

interface TimeframeToggleProps {
  value: Timeframe;
  onChange: (timeframe: Timeframe) => void;
}

export function TimeframeToggle({ value, onChange }: TimeframeToggleProps) {
  return (
    <ToggleGroup
      type="single"
      value={value}
      onValueChange={(next) => {
        if (next) {
          onChange(next as Timeframe);
        }
      }}
    >
      {TIMEFRAMES.map((tf) => (
        <ToggleGroupItem key={tf} value={tf} aria-label={tf}>
          {tf}
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  );
}
