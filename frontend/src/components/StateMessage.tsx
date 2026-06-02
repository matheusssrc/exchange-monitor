import { Skeleton } from "@/components/ui/skeleton";

interface StateMessageProps {
  variant: "loading" | "empty" | "error";
  title?: string;
  description?: string;
}

export function StateMessage({ variant, title, description }: StateMessageProps) {
  if (variant === "loading") {
    return (
      <div className="space-y-2" role="status" aria-label="Loading">
        <Skeleton className="h-6 w-3/4" />
        <Skeleton className="h-6 w-1/2" />
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center gap-1 py-8 text-center">
      {title ? <p className="text-sm font-medium text-foreground">{title}</p> : null}
      {description ? (
        <p className="text-xs text-muted-foreground">{description}</p>
      ) : null}
    </div>
  );
}
