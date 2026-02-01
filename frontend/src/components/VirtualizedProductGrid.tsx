/**
 * VirtualizedProductGrid - Efficient rendering of large product lists
 * Uses react-window to render only visible items, preventing DOM bloat
 * 
 * Performance improvement: From O(n) DOM nodes to O(viewport_height)
 * Example: 1000 products -> ~20 visible DOM nodes instead of 1000
 */

import React, { useMemo } from "react";
import { FixedSizeGrid as Grid } from "react-window";
import type { Product } from "../lib/catalogLoader";

interface VirtualizedProductGridProps {
  products: Product[];
  columnCount?: number;
  rowHeight?: number;
  columnWidth?: number;
  renderItem: (product: Product) => React.ReactNode;
  className?: string;
  height?: number;
  overscanCount?: number;
}

/**
 * Chunk products array into grid rows
 */
function chunkProducts(products: Product[], columnCount: number): Product[][] {
  const chunks: Product[][] = [];
  for (let i = 0; i < products.length; i += columnCount) {
    chunks.push(products.slice(i, i + columnCount));
  }
  return chunks;
}

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
    // Chunk products into grid rows
    const rows = useMemo(
      () => chunkProducts(products, columnCount),
      [products, columnCount]
    );

    // Calculate width dynamically based on columns
    const width = columnCount * columnWidth + 24; // +24 for padding

    if (rows.length === 0) {
      return (
        <div className={`${className} flex items-center justify-center`}>
          <div className="text-zinc-500">No products to display</div>
        </div>
      );
    }

    /**
     * Render individual cell in the grid
     * row and column indices are provided by react-window
     */
    const Cell = ({
      columnIndex,
      rowIndex,
      style,
    }: {
      columnIndex: number;
      rowIndex: number;
      style: React.CSSProperties;
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
    };

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
          {Cell}
        </Grid>
      </div>
    );
  }
);

VirtualizedProductGrid.displayName = "VirtualizedProductGrid";
