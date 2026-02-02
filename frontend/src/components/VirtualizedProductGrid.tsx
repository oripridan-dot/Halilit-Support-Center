/**
 * VirtualizedProductGrid - Efficient rendering of large product lists
 *
 * Uses react-window to render only visible items, preventing DOM bloat
 * Performance improvement: From O(n) DOM nodes to O(viewport_height)
 * Example: 1000 products -> ~20 visible DOM nodes instead of 1000
 */

import React, { useMemo, useCallback } from "react";
import { FixedSizeGrid as Grid } from "react-window";
import type { Product } from "../lib/catalogLoader";
import { BaseComponentProps } from "../types/componentUtils";

interface VirtualizedProductGridProps extends BaseComponentProps {
  products: Product[];
  columnCount?: number;
  rowHeight?: number;
  columnWidth?: number;
  renderItem: (product: Product) => React.ReactNode;
  height?: number;
  overscanCount?: number;
}

/**
 * Chunk products array into grid rows
 * Pure helper function extracted for testability
 */
function chunkProducts(products: Product[], columnCount: number): Product[][] {
  const chunks: Product[][] = [];
  for (let i = 0; i < products.length; i += columnCount) {
    chunks.push(products.slice(i, i + columnCount));
  }
  return chunks;
}

/**
 * Grid cell renderer component
 * Memoized to prevent unnecessary re-renders
 */
const GridCell = React.memo(
  ({
    rows,
    columnIndex,
    rowIndex,
    style,
    renderItem,
  }: {
    rows: Product[][];
    columnIndex: number;
    rowIndex: number;
    style: React.CSSProperties;
    renderItem: (product: Product) => React.ReactNode;
  }) => {
    const row = rows[rowIndex];
    if (!row || !row[columnIndex]) {
      return <div style={style} />;
    }

    const product = row[columnIndex];

    return (
      <div style={style} className="p-3">
        {renderItem(product)}
      </div>
    );
  },
);

GridCell.displayName = "GridCell";

export const VirtualizedProductGrid = React.memo(
  ({
    products,
    columnCount = 3,
    rowHeight = 320,
    columnWidth = 300,
    renderItem,
    className = "",
    height = 800,
    overscanCount = 2,
  }: VirtualizedProductGridProps) => {
    // Memoize chunked rows
    const rows = useMemo(
      () => chunkProducts(products, columnCount),
      [products, columnCount],
    );

    // Memoize width calculation
    const width = useMemo(
      () => columnCount * columnWidth + 24,
      [columnCount, columnWidth],
    );

    // Memoize cell renderer callback
    const renderItemCallback = useCallback(
      (product: Product) => renderItem(product),
      [renderItem],
    );

    // Handle empty state
    if (rows.length === 0) {
      return (
        <div
          className={`${className} flex items-center justify-center min-h-[200px]`}
        >
          <div className="text-zinc-500 text-center">
            <p>No products to display</p>
          </div>
        </div>
      );
    }

    return (
      <div className={className}>
        <Grid
          columnCount={columnCount}
          columnWidth={columnWidth}
          height={height}
          rowCount={rows.length}
          rowHeight={rowHeight}
          width={width}
          overscanRowCount={overscanCount}
        >
          {(cellProps) => (
            <GridCell
              {...cellProps}
              rows={rows}
              renderItem={renderItemCallback}
            />
          )}
        </Grid>
      </div>
    );
  },
);

VirtualizedProductGrid.displayName = "VirtualizedProductGrid";
