import React, { useState } from "react";
import { useDebounceThrottle } from "../../hooks/useDebounceThrottle";
import { useNavigationStore } from "../../store/navigationStore";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { Loader2, ChevronLeft, ChevronRight } from "lucide-react";

const PAGE_SIZE = 25;

const InventoryView: React.FC = () => {
  const {
    searchQuery: globalSearch,
    setSearchQuery,
    goToProduct,
  } = useNavigationStore();
  const [localSearch, setLocalSearch] = useState(globalSearch ?? "");
  const [page, setPage] = useState(1);

  // Reset to page 1 whenever the search term changes
  const debouncedSetSearch = useDebounceThrottle(
    (value: string) => {
      setPage(1);
      setSearchQuery(value);
    },
    150,
    0,
  );

  const {
    products,
    totalItems,
    totalPages,
    isLoading,
    isError,
    handleRetry,
    retryCount,
  } = useConductorCatalog({
    page,
    pageSize: PAGE_SIZE,
    searchQuery: globalSearch,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = e.target.value;
    setLocalSearch(v);
    debouncedSetSearch(v);
  };

  const handleProductClick = (productId: string) => {
    goToProduct(productId);
  };

  return (
    <div className="dark:bg-zinc-900 min-h-screen p-4">
      {/* ── Search bar ── */}
      <div className="mb-4 flex items-center gap-2">
        <input
          type="text"
          placeholder="Search by name, SKU, or brand…"
          value={localSearch}
          onChange={handleInputChange}
          className="dark:bg-zinc-800 dark:text-zinc-100 placeholder-zinc-400 flex-1 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {totalItems > 0 && (
          <span className="text-zinc-400 text-sm whitespace-nowrap">
            {totalItems.toLocaleString()} products
          </span>
        )}
      </div>

      {/* ── States ── */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin h-6 w-6 text-blue-500" />
          <span className="ml-2 dark:text-zinc-300">Loading…</span>
        </div>
      )}

      {isError && (
        <div className="dark:bg-zinc-800 p-4 rounded-lg text-center">
          <p className="text-red-500 mb-2">Failed to load inventory.</p>
          <button
            onClick={handleRetry}
            className="px-4 py-2 bg-zinc-700 text-white rounded hover:bg-zinc-600"
          >
            Retry ({retryCount}/3)
          </button>
        </div>
      )}

      {/* ── Product grid ── */}
      {!isLoading && !isError && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {products.length === 0 ? (
              <div className="col-span-full text-zinc-400 py-12 text-center">
                No products found.
              </div>
            ) : (
              products.map((product) => {
                const hasPrice = product.price != null;
                const isOutOfStock = (product as any).stock === 0;
                const isUnconfirmed =
                  (product as any).stock == null && !hasPrice;
                return (
                  <button
                    key={product.id}
                    onClick={() => handleProductClick(product.id)}
                    className={`dark:bg-zinc-800 rounded-md p-4 shadow-md text-left hover:ring-2 hover:ring-blue-500 transition-all ${
                      isOutOfStock ? "ring-2 ring-red-600" : ""
                    }`}
                  >
                    {isOutOfStock && (
                      <span className="inline-block mb-2 text-xs font-bold bg-red-600 text-white px-2 py-0.5 rounded">
                        OUT OF STOCK
                      </span>
                    )}
                    {isUnconfirmed && (
                      <span className="inline-block mb-2 text-xs font-bold bg-amber-500 text-white px-2 py-0.5 rounded">
                        UNCONFIRMED
                      </span>
                    )}
                    <h3 className="dark:text-zinc-100 text-sm font-semibold mb-1 truncate">
                      {product.name}
                    </h3>
                    <p className="text-zinc-400 text-xs mb-1 truncate">
                      {product.brand}
                    </p>
                    {hasPrice ? (
                      <p className="text-blue-400 text-sm font-medium">
                        ₪{product.price!.toLocaleString()}
                      </p>
                    ) : (
                      <p className="text-amber-400 text-xs font-medium">
                        Call for Price
                      </p>
                    )}
                  </button>
                );
              })
            )}
          </div>

          {/* ── Pagination ── */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-3 mt-6">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-1.5 rounded dark:bg-zinc-700 disabled:opacity-40 hover:bg-zinc-600"
              >
                <ChevronLeft className="h-4 w-4 text-zinc-300" />
              </button>
              <span className="text-zinc-400 text-sm">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-1.5 rounded dark:bg-zinc-700 disabled:opacity-40 hover:bg-zinc-600"
              >
                <ChevronRight className="h-4 w-4 text-zinc-300" />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default InventoryView;
