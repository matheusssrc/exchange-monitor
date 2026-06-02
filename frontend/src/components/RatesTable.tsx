import { StateMessage } from "@/components/StateMessage";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatNumber, formatTimestamp } from "@/lib/format";
import { pairLabel } from "@/lib/pairs";
import { cn } from "@/lib/utils";

export interface RatesTableRow {
  pair: string;
  bid: string | null;
  ask: string | null;
  fetchedAt: string | null;
}

interface RatesTableProps {
  rows: RatesTableRow[];
  isLoading: boolean;
  selectedPair: string;
  onSelectPair?: (pair: string) => void;
}

export function RatesTable({
  rows,
  isLoading,
  selectedPair,
  onSelectPair,
}: RatesTableProps) {
  if (isLoading) {
    return <StateMessage variant="loading" />;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Par</TableHead>
          <TableHead className="text-right">Bid</TableHead>
          <TableHead className="text-right">Ask</TableHead>
          <TableHead className="text-right">Atualizado</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((row) => (
          <TableRow
            key={row.pair}
            data-state={row.pair === selectedPair ? "selected" : undefined}
            className={cn(
              onSelectPair && "cursor-pointer",
              row.pair === selectedPair && "bg-muted/50",
            )}
            onClick={onSelectPair ? () => onSelectPair(row.pair) : undefined}
          >
            <TableCell className="font-medium">{pairLabel(row.pair)}</TableCell>
            <TableCell className="text-right tabular-nums">
              {row.bid === null ? "—" : formatNumber(row.bid)}
            </TableCell>
            <TableCell className="text-right tabular-nums">
              {row.ask === null ? "—" : formatNumber(row.ask)}
            </TableCell>
            <TableCell className="text-right text-xs text-muted-foreground">
              {row.fetchedAt === null ? "—" : formatTimestamp(row.fetchedAt)}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
