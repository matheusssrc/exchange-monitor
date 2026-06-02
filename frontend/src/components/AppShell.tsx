import { Activity } from "lucide-react";
import type { ReactNode } from "react";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border">
        <div className="container flex h-14 items-center gap-2">
          <Activity className="h-5 w-5 text-primary" aria-hidden="true" />
          <h1 className="text-lg font-semibold">Trillia Exchange Monitor</h1>
        </div>
      </header>
      <main className="container py-8">{children}</main>
    </div>
  );
}
