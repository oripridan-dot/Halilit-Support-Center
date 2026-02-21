/**
 * LiquidCanvas — Server-Driven UI Engine (Level 10)
 * ===================================================
 * Interprets a JSON schema emitted by the Halilit Liquid JIT Engine and
 * renders data widgets without any JSX compilation step.
 *
 * Supported widget types:
 *   "DataGrid"    — full table with sortable columns
 *   "MetricCard"  — single big KPI number
 *   "List"        — simple vertical list of text values
 *
 * Usage:
 *   import { LiquidCanvas } from "./LiquidCanvas";
 *   <LiquidCanvas schema={uiSchema} onClose={() => setSchema(null)} />
 */

import React, { useEffect, useRef, useState } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface LiquidSchema {
  type: "DataGrid" | "MetricCard" | "List";
  title: string;
  columns?: string[];
  dataSource: string; // e.g. "/api/liquid/data/ephemeral_abc123"
}

interface LiquidCanvasProps {
  schema: LiquidSchema;
  onClose?: () => void;
}

interface LiquidResponse {
  columns: string[];
  row_count: number;
  capped: boolean;
  data: Record<string, unknown>[];
}

// ---------------------------------------------------------------------------
// Sub-widgets
// ---------------------------------------------------------------------------

function DataGridWidget({
  schema,
  data,
  columns,
  capped,
}: {
  schema: LiquidSchema;
  data: Record<string, unknown>[];
  columns: string[];
  capped: boolean;
}) {
  const [sortCol, setSortCol] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const displayCols = schema.columns?.length ? schema.columns : columns;

  function handleSort(col: string) {
    if (sortCol === col) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortCol(col);
      setSortDir("asc");
    }
  }

  const sorted = [...data].sort((a, b) => {
    if (!sortCol) return 0;
    const av = a[sortCol] ?? "";
    const bv = b[sortCol] ?? "";
    if (av < bv) return sortDir === "asc" ? -1 : 1;
    if (av > bv) return sortDir === "asc" ? 1 : -1;
    return 0;
  });

  return (
    <div className="overflow-x-auto rounded-lg border border-zinc-700/50">
      <table className="w-full text-left text-xs text-zinc-300">
        <thead className="bg-zinc-800 text-zinc-400 uppercase tracking-widest">
          <tr>
            {displayCols.map((col) => (
              <th
                key={col}
                className="px-3 py-2.5 cursor-pointer select-none hover:text-zinc-100 whitespace-nowrap"
                onClick={() => handleSort(col)}
              >
                {col}
                {sortCol === col && (
                  <span className="ml-1 opacity-60">
                    {sortDir === "asc" ? "↑" : "↓"}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row, i) => (
            <tr
              key={i}
              className="border-t border-zinc-800 hover:bg-zinc-800/40 transition-colors"
            >
              {displayCols.map((col) => (
                <td
                  key={col}
                  className="px-3 py-2 whitespace-nowrap max-w-[200px] truncate"
                >
                  {row[col] !== undefined && row[col] !== null
                    ? String(row[col])
                    : "—"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {capped && (
        <p className="text-[10px] text-amber-500/70 px-3 py-1.5 border-t border-zinc-800">
          ⚠ Results capped at 500 rows.
        </p>
      )}
    </div>
  );
}

function MetricCardWidget({
  data,
  columns,
}: {
  data: Record<string, unknown>[];
  columns: string[];
}) {
  const firstRow = data[0];
  if (!firstRow) return <p className="text-zinc-500 text-sm">No data.</p>;

  return (
    <div className="grid grid-cols-2 gap-3">
      {columns.map((col) => {
        const val = firstRow[col];
        return (
          <div
            key={col}
            className="rounded-lg bg-zinc-800/70 border border-zinc-700/40 px-4 py-3"
          >
            <p className="text-[10px] text-zinc-500 uppercase tracking-widest mb-1">
              {col}
            </p>
            <p className="text-xl font-bold text-zinc-100">
              {val !== null && val !== undefined ? String(val) : "—"}
            </p>
          </div>
        );
      })}
    </div>
  );
}

function ListWidget({
  data,
  columns,
}: {
  data: Record<string, unknown>[];
  columns: string[];
}) {
  const primaryCol = columns[0];
  const secondaryCol = columns[1];
  return (
    <ul className="divide-y divide-zinc-800 rounded-lg border border-zinc-700/50 overflow-hidden">
      {data.map((row, i) => (
        <li
          key={i}
          className="flex items-center justify-between px-3 py-2 hover:bg-zinc-800/40"
        >
          <span className="text-sm text-zinc-200">
            {primaryCol ? String(row[primaryCol] ?? "—") : "—"}
          </span>
          {secondaryCol && (
            <span className="text-xs text-zinc-500 ml-4">
              {String(row[secondaryCol] ?? "—")}
            </span>
          )}
        </li>
      ))}
    </ul>
  );
}

// ---------------------------------------------------------------------------
// Main LiquidCanvas
// ---------------------------------------------------------------------------

export const LiquidCanvas: React.FC<LiquidCanvasProps> = ({
  schema,
  onClose,
}) => {
  const [data, setData] = useState<Record<string, unknown>[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [capped, setCapped] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!schema?.dataSource) return;

    setLoading(true);
    setError(null);

    fetch(schema.dataSource)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        return res.json() as Promise<LiquidResponse>;
      })
      .then((json) => {
        setData(json.data ?? []);
        setColumns(json.columns ?? schema.columns ?? []);
        setCapped(json.capped ?? false);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, [schema]);

  // Close on Escape
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && onClose) onClose();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [onClose]);

  // Close on backdrop click
  function handleBackdrop(e: React.MouseEvent) {
    if (e.target === overlayRef.current && onClose) onClose();
  }

  return (
    <>
      {/* ── Full-screen backdrop ── */}
      <div
        ref={overlayRef}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm px-4"
        onClick={handleBackdrop}
        aria-modal="true"
        role="dialog"
        aria-label="Liquid Canvas"
      >
        {/* ── Panel ── */}
        <div className="relative w-full max-w-4xl max-h-[85vh] flex flex-col rounded-2xl border border-zinc-700/60 bg-[#0d0d0d] shadow-2xl shadow-black/80 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-5 py-3.5 border-b border-zinc-800 bg-[#0f0f0f] shrink-0">
            <div className="flex items-center gap-2.5">
              <span className="text-blue-400 text-lg">🌊</span>
              <div>
                <h2 className="text-sm font-semibold text-zinc-100 tracking-tight">
                  {schema.title || "Liquid Feature"}
                </h2>
                <p className="text-[10px] text-zinc-500">
                  Ephemeral · {schema.dataSource.split("/").pop()} ·{" "}
                  {loading
                    ? "loading…"
                    : error
                      ? "error"
                      : `${data.length} rows`}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-emerald-500/80 font-mono bg-emerald-950/30 border border-emerald-900/30 px-2 py-0.5 rounded">
                Level 10 · JIT
              </span>
              {onClose && (
                <button
                  onClick={onClose}
                  aria-label="Close Liquid Canvas"
                  className="text-zinc-600 hover:text-zinc-300 transition-colors p-1.5 rounded hover:bg-zinc-800"
                >
                  ✕
                </button>
              )}
            </div>
          </div>

          {/* Body */}
          <div className="overflow-y-auto flex-1 p-5">
            {loading && (
              <div className="flex flex-col items-center gap-3 py-16">
                <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                <p className="text-sm text-zinc-500">
                  Synthesising data stream…
                </p>
              </div>
            )}

            {!loading && error && (
              <div className="flex items-start gap-3 rounded-lg bg-red-950/40 border border-red-800/40 px-4 py-3">
                <span className="text-red-400 text-lg mt-0.5">⚠</span>
                <div>
                  <p className="text-sm text-red-300 font-semibold">
                    Data stream error
                  </p>
                  <p className="text-xs text-red-400/80 mt-0.5">{error}</p>
                </div>
              </div>
            )}

            {!loading && !error && data.length === 0 && (
              <div className="text-center py-16">
                <p className="text-zinc-500 text-sm">
                  No data matched the ephemeral query.
                </p>
              </div>
            )}

            {!loading && !error && data.length > 0 && (
              <>
                {schema.type === "DataGrid" && (
                  <DataGridWidget
                    schema={schema}
                    data={data}
                    columns={columns}
                    capped={capped}
                  />
                )}
                {schema.type === "MetricCard" && (
                  <MetricCardWidget data={data} columns={columns} />
                )}
                {schema.type === "List" && (
                  <ListWidget data={data} columns={columns} />
                )}
              </>
            )}
          </div>

          {/* Footer */}
          <div className="shrink-0 px-5 py-2.5 border-t border-zinc-800 flex items-center justify-between bg-[#0f0f0f]">
            <p className="text-[10px] text-zinc-600 font-mono truncate max-w-[60%]">
              {schema.dataSource}
            </p>
            {onClose && (
              <button
                onClick={onClose}
                className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors px-3 py-1 rounded bg-zinc-800 hover:bg-zinc-700"
              >
                Close
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default LiquidCanvas;
