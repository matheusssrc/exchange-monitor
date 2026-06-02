# Trillia Exchange Monitor — Frontend

Dashboard SPA em **React + TypeScript** para o Trillia Exchange Monitor. Consome a API REST
do backend e mostra o monitoramento de câmbio em tempo quase real numa única tela:

- **seletor de moeda base** (ex.: BRL) que filtra os pares exibidos;
- **tabela de cotações** com bid/ask e horário da última atualização, de `GET /rates/latest`;
- **seletor de par** do gráfico + **timeframes** (1m / 5m / 15m);
- **gráfico de candlestick (OHLC)** construído a partir de `GET /rates/history`, com eixo de
  preço à direita e marcador do último preço, atualizado a cada 30s.

Construído com React 19, Vite 8 e TypeScript 6 (strict). Estilo com Tailwind CSS + shadcn/ui,
dados com TanStack Query, gráficos com Recharts e validação de payload com Zod. Testes em
Vitest + Testing Library + MSW.

## Pré-requisitos

- **Node.js 22+** e npm.
- O [backend](../README.md) rodando em `http://localhost:8000` para dados reais
  (ver a nota sobre o proxy abaixo).

## Começando

```bash
npm install
npm run dev
```

O dev server sobe em `http://localhost:5173`.

## Scripts

| Script | Descrição |
| --- | --- |
| `npm run dev` | Dev server Vite com HMR. |
| `npm run build` | Type-check (`tsc --noEmit`) e build para `dist/`. |
| `npm run preview` | Serve o build de produção localmente. |
| `npm run lint` | Roda o ESLint no projeto. |
| `npm run typecheck` | Type-check com TypeScript, sem emitir. |
| `npm test` | Roda a suíte Vitest uma vez. |
| `npm run test:cov` | Roda a suíte com relatório de cobertura. |

## Notas

- **Proxy da API.** O frontend sempre chama a API pelo caminho relativo `/api`, mantendo
  tudo same-origin (sem CORS) em qualquer ambiente. No dev, o Vite faz proxy de `/api` para
  o backend em `http://localhost:8000`, removendo o prefixo `/api` antes de encaminhar
  (ver [`vite.config.ts`](vite.config.ts)). Em produção, o nginx cumpre o mesmo papel. Suba
  o backend antes do `npm run dev` para ver dados reais.
- **Alias de path.** `@/` resolve para `src/` (configurado em
  [`vite.config.ts`](vite.config.ts) e [`tsconfig.json`](tsconfig.json)).
- **TypeScript estrito.** `strict`, `noUncheckedIndexedAccess`, `noUnusedLocals` e
  `noUnusedParameters` ligados.
- **Candlestick.** O histórico é agregado no cliente em candles OHLC por timeframe
  (`src/lib/ohlc.ts`); o último candle representa o preço em formação e é destacado por uma
  linha de referência no gráfico.

## Estrutura

```
src/
├── components/   # HistoryChart (candlestick), RatesTable, CurrencySelect, TimeframeToggle, ui/ (shadcn)
├── hooks/        # useAllLatestRates, useRateHistory, usePairs, useUrlState
├── lib/          # api, ohlc, ranges, pairs, format, env (Zod), utils
├── pages/        # Dashboard
└── styles/       # globals.css (tokens de tema)
```

---

Licença MIT · Matheus Rossi Carvalho.
