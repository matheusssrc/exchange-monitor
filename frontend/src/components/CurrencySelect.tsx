import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

export interface SelectOption {
  value: string;
  label: string;
}

interface CurrencySelectProps {
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
  ariaLabel: string;
  placeholder?: string;
  className?: string;
}

export function CurrencySelect({
  value,
  onChange,
  options,
  ariaLabel,
  placeholder,
  className,
}: CurrencySelectProps) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger
        aria-label={ariaLabel}
        className={cn("w-[220px] bg-secondary font-medium", className)}
      >
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        {options.map((option) => (
          <SelectItem key={option.value} value={option.value}>
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
